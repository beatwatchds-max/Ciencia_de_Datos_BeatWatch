"""
Worker automático para BeatWatch ETL usando MongoDB Change Streams.

Los cambios no ejecutan el ETL uno por uno. Se acumulan en una ventana de
30 a 60 segundos (configurable) y al vencer la ventana se ejecuta una única
corrida EXTRACT -> TRANSFORM -> LOAD.
"""

from datetime import datetime
import time

from pymongo.errors import PyMongoError

from batching import LoteCambios
from config import (
    ACTIVIDADES_COLLECTION,
    ARRITMIAS_COLLECTION,
    CHANGE_STREAM_MAX_AWAIT_MS,
    EPISODIOS_COLLECTION,
    ETL_BATCH_INTERVAL_SECONDS,
    ETL_RUN_ON_STARTUP,
)
from database import close_database, connect_database
from main import ejecutar_etl


COLECCIONES_VIGILADAS = [
    ARRITMIAS_COLLECTION,
    EPISODIOS_COLLECTION,
    ACTIVIDADES_COLLECTION,
]

OPERACIONES_VIGILADAS = ["insert", "update", "replace", "delete"]


def construir_pipeline_change_stream():
    """Filtra únicamente cambios que afectan al ETL."""

    return [
        {
            "$match": {
                "operationType": {"$in": OPERACIONES_VIGILADAS},
                "ns.coll": {"$in": COLECCIONES_VIGILADAS},
            }
        }
    ]


def mostrar_cambio(cambio: dict, lote: LoteCambios) -> None:
    coleccion = cambio.get("ns", {}).get("coll", "desconocida")
    operacion = cambio.get("operationType", "desconocida")
    print(
        f"Cambio agrupado | colección={coleccion} | operación={operacion} "
        f"| pendientes={lote.total}"
    )


def procesar_lote(db, lote: LoteCambios) -> bool:
    """Ejecuta una sola corrida ETL para todos los cambios acumulados."""

    if not lote.pendiente:
        return True

    print("\n================================")
    print("PROCESANDO LOTE DE CAMBIOS")
    print("================================")
    print(f"Fecha: {datetime.now().isoformat(timespec='seconds')}")
    print(f"Cambios agrupados: {lote.total}")
    print(f"Por colección: {dict(lote.por_coleccion)}")
    print(f"Por operación: {dict(lote.por_operacion)}")

    try:
        ejecutar_etl(db)
    except Exception as exc:
        # No mostrar el texto completo de la excepción. PyMongo puede incluir
        # detalles de infraestructura en sus mensajes.
        print(f"ERROR AL EJECUTAR EL LOTE ETL: {type(exc).__name__}")
        return False

    lote.reiniciar()
    return True


def ejecutar_trigger():
    client = None
    lote = LoteCambios()

    try:
        client, db = connect_database()
        print("MongoDB conectado correctamente.")
        print("Worker automático de BeatWatch iniciado.")
        print(f"Ventana de agrupación: {ETL_BATCH_INTERVAL_SECONDS} segundos")
        print(f"Colecciones vigiladas: {len(COLECCIONES_VIGILADAS)}")

        # Evita estadísticas desactualizadas tras un reinicio del worker.
        if ETL_RUN_ON_STARTUP:
            print("\nSincronización inicial del ETL...")
            ejecutar_etl(db)

        pipeline = construir_pipeline_change_stream()
        with db.watch(
            pipeline,
            full_document="updateLookup",
            max_await_time_ms=CHANGE_STREAM_MAX_AWAIT_MS,
        ) as stream:
            while stream.alive:
                cambio = stream.try_next()
                ahora = time.monotonic()

                if cambio is not None:
                    lote.registrar(cambio, ahora)
                    mostrar_cambio(cambio, lote)

                if lote.listo(ahora, ETL_BATCH_INTERVAL_SECONDS):
                    procesado = procesar_lote(db, lote)

                    if not procesado:
                        lote.posponer_reintento(ahora)
                        print(
                            "El lote se conserva y se reintentará después de "
                            f"{ETL_BATCH_INTERVAL_SECONDS} segundos."
                        )

    except KeyboardInterrupt:
        print("\nWorker detenido por el usuario.")
    except PyMongoError as exc:
        print(f"ERROR DE MONGODB EN EL WORKER: {type(exc).__name__}")
        raise
    finally:
        close_database(client)


if __name__ == "__main__":
    try:
        ejecutar_trigger()
    except Exception as exc:
        # El proceso sigue terminando con error, pero el traceback sensible no
        # se envía al log de la plataforma.
        print(f"WORKER FINALIZADO POR ERROR: {type(exc).__name__}")
        raise SystemExit(1) from None
