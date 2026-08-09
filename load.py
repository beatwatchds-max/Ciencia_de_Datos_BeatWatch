from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo import ASCENDING, MongoClient, UpdateOne
from pymongo.database import Database
from pymongo.errors import (
    BulkWriteError,
    ConfigurationError,
    DuplicateKeyError,
    OperationFailure,
    PyMongoError,
)

from config import (
    MONGO_CONNECTION_STRING,
    DB_NAME,
    ESTADISTICAS_COLLECTION,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

MONGO_URI = MONGO_CONNECTION_STRING
MONGO_DATABASE = DB_NAME
COLECCION_ESTADISTICAS = ESTADISTICAS_COLLECTION


# ============================================================
# CONEXIÓN
# ============================================================


def crear_cliente_mongo(uri: str | None = None) -> MongoClient:
    """Crea el cliente de MongoDB y verifica que el servidor responda."""

    mongo_uri = uri or MONGO_URI

    if not mongo_uri:
        raise RuntimeError(
            "No se encontró MONGO_CONNECTION_STRING para ejecutar LOAD."
        )

    cliente = MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=10_000,
        connectTimeoutMS=10_000,
    )

    # Fuerza una operación para detectar errores de conexión inmediatamente.
    cliente.admin.command("ping")

    return cliente



def obtener_base_datos(
    cliente: MongoClient,
    nombre_base_datos: str | None = None,
) -> Database:
    """
    Obtiene la base de datos indicada.

    Prioridad:
    1. Parámetro nombre_base_datos.
    2. Variable de entorno MONGO_DATABASE.
    3. Base incluida en MONGO_URI.
    """

    nombre = nombre_base_datos or MONGO_DATABASE

    if nombre:
        return cliente[nombre]

    try:
        return cliente.get_default_database()
    except ConfigurationError as error:
        raise ValueError(
            "No se indicó la base de datos. Agrega el nombre a MONGO_URI "
            "o define la variable de entorno MONGO_DATABASE."
        ) from error


# ============================================================
# VALIDACIÓN Y PREPARACIÓN
# ============================================================


def preparar_estadistica(documento: dict[str, Any]) -> dict[str, Any]:
    """Valida y prepara una estadística diaria antes de guardarla."""

    if not isinstance(documento, dict):
        raise TypeError("Cada estadística diaria debe ser un diccionario.")

    estadistica = documento.copy()

    # Nunca reutilizamos un _id recibido accidentalmente.
    estadistica.pop("_id", None)

    id_paciente = estadistica.get("IdPaciente")
    fecha = estadistica.get("Fecha")

    if id_paciente is None:
        raise ValueError("La estadística no contiene IdPaciente.")

    if not fecha or not isinstance(fecha, str):
        raise ValueError(
            "La estadística no contiene una Fecha válida en formato YYYY-MM-DD."
        )

    try:
        datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError as error:
        raise ValueError(
            f"La fecha '{fecha}' no tiene el formato YYYY-MM-DD."
        ) from error

    # Se agrega una fecha técnica para saber cuándo se ejecutó el LOAD.
    estadistica["FechaActualizacion"] = datetime.now(timezone.utc)

    return estadistica



def crear_indice_unico(database: Database, nombre_coleccion: str) -> None:
    """
    Evita duplicados para el mismo paciente y día.

    Si ya existen documentos duplicados, MongoDB no podrá crear el índice y
    se mostrará un error claro para que puedan limpiarse antes de continuar.
    """

    coleccion = database[nombre_coleccion]

    coleccion.create_index(
        [
            ("IdPaciente", ASCENDING),
            ("Fecha", ASCENDING),
        ],
        unique=True,
        name="uq_estadistica_paciente_fecha",
    )


# ============================================================
# LOAD
# ============================================================


def cargar_estadisticas_diarias(
    estadisticas: list[dict[str, Any]],
    database: Database,
    nombre_coleccion: str = COLECCION_ESTADISTICAS,
) -> dict[str, int]:
    """
    Inserta o actualiza las estadísticas diarias mediante operaciones upsert.
    """

    if not isinstance(estadisticas, list):
        raise TypeError("estadisticas_diarias debe ser una lista.")

    if not estadisticas:
        print("No hay estadísticas diarias para cargar.")
        return {
            "recibidas": 0,
            "insertadas": 0,
            "actualizadas": 0,
            "sin_cambios": 0,
            "omitidas": 0,
        }

    crear_indice_unico(database, nombre_coleccion)
    coleccion = database[nombre_coleccion]

    operaciones: list[UpdateOne] = []
    omitidas = 0

    for posicion, documento in enumerate(estadisticas, start=1):
        try:
            estadistica = preparar_estadistica(documento)
        except (TypeError, ValueError) as error:
            omitidas += 1
            print(f"Estadística {posicion} omitida: {error}")
            continue

        filtro = {
            "IdPaciente": estadistica["IdPaciente"],
            "Fecha": estadistica["Fecha"],
        }

        fecha_actualizacion = estadistica.pop("FechaActualizacion")

        operaciones.append(
            UpdateOne(
                filtro,
                {
                    "$set": {
                        **estadistica,
                        "FechaActualizacion": fecha_actualizacion,
                    },
                    "$setOnInsert": {
                        "FechaCreacion": fecha_actualizacion,
                    },
                },
                upsert=True,
            )
        )

    if not operaciones:
        print("Ninguna estadística válida pudo cargarse.")
        return {
            "recibidas": len(estadisticas),
            "insertadas": 0,
            "actualizadas": 0,
            "sin_cambios": 0,
            "omitidas": omitidas,
        }

    resultado = coleccion.bulk_write(
        operaciones,
        ordered=False,
    )

    insertadas = resultado.upserted_count
    actualizadas = resultado.modified_count
    coincidentes = resultado.matched_count
    sin_cambios = max(coincidentes - actualizadas, 0)

    return {
        "recibidas": len(estadisticas),
        "insertadas": insertadas,
        "actualizadas": actualizadas,
        "sin_cambios": sin_cambios,
        "omitidas": omitidas,
    }



def load(
    data: dict[str, Any],
    database: Database | None = None,
    nombre_base_datos: str | None = None,
    nombre_coleccion: str = COLECCION_ESTADISTICAS,
) -> dict[str, int]:
   

    print("")
    print("================================")
    print("INICIANDO LOAD")
    print("================================")

    if not isinstance(data, dict):
        raise TypeError("LOAD esperaba el diccionario retornado por transform.py.")

    estadisticas = data.get("estadisticas_diarias", [])

    cliente_creado: MongoClient | None = None

    try:
        if database is None:
            cliente_creado = crear_cliente_mongo()
            database = obtener_base_datos(
                cliente_creado,
                nombre_base_datos,
            )

        resumen = cargar_estadisticas_diarias(
            estadisticas=estadisticas,
            database=database,
            nombre_coleccion=nombre_coleccion,
        )

        print("")
        print("================================")
        print("LOAD FINALIZADO")
        print("================================")
        print("")
        print("RESUMEN DEL LOAD")
        print("--------------------------------")
        print(f"Estadísticas recibidas: {resumen['recibidas']}")
        print(f"Estadísticas insertadas: {resumen['insertadas']}")
        print(f"Estadísticas actualizadas: {resumen['actualizadas']}")
        print(f"Estadísticas sin cambios: {resumen['sin_cambios']}")
        print(f"Estadísticas omitidas: {resumen['omitidas']}")
        print(f"Colección: {nombre_coleccion}")

        return resumen

    except DuplicateKeyError as error:
        raise RuntimeError(
            "Se detectó un valor duplicado para IdPaciente y Fecha. "
            "Revisa los documentos existentes en EstadisticasDiarias."
        ) from error

    except OperationFailure as error:
        raise RuntimeError(
            "MongoDB rechazó una operación. Verifica permisos, índices y "
            "la configuración de la base de datos."
        ) from error

    except BulkWriteError as error:
        detalles = error.details or {}
        errores = detalles.get("writeErrors", [])
        raise RuntimeError(
            f"La carga masiva falló con {len(errores)} error(es) de escritura."
        ) from error

    except PyMongoError as error:
        raise RuntimeError(
            f"No fue posible completar el LOAD en MongoDB: {error}"
        ) from error

    finally:
        if cliente_creado is not None:
            cliente_creado.close()


# ============================================================
# EJECUCIÓN DEL ETL COMPLETO
# ============================================================


def ejecutar_pipeline() -> dict[str, int]:
    """Ejecuta EXTRACT -> TRANSFORM -> LOAD usando la configuración del proyecto."""

    from database import connect_database, close_database
    from extract import extract_all
    from transform import transform

    cliente = None

    try:
        cliente, database = connect_database()
        datos_extraidos = extract_all(database)
        datos_transformados = transform(datos_extraidos)
        return load(
            datos_transformados,
            database=database,
            nombre_coleccion=COLECCION_ESTADISTICAS,
        )
    finally:
        close_database(cliente)


if __name__ == "__main__":
    try:
        ejecutar_pipeline()
    except ImportError as error:
        print("")
        print("No fue posible importar un módulo del pipeline ETL.")
        print(
            "Verifica que database.py, extract.py y transform.py estén "
            "en la misma carpeta que load.py."
        )
        print(f"Detalle: {error}")
    except Exception as error:
        print("")
        print("================================")
        print("ERROR EN EL LOAD")
        print("================================")
        print(error)