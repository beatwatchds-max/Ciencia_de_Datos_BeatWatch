from config import ESTADISTICAS_COLLECTION
from database import close_database, connect_database
from extract import extract_all
from load import load
from transform import transform


def ejecutar_etl(db):
    """Ejecuta una corrida completa EXTRACT -> TRANSFORM -> LOAD."""

    print("\n=== BeatWatch ETL ===")
    print("1. Extrayendo datos...")
    raw = extract_all(db)

    print("2. Transformando datos...")
    transformed = transform(raw)

    print("3. Guardando estadísticas en MongoDB...")
    resumen = load(
        transformed,
        database=db,
        nombre_coleccion=ESTADISTICAS_COLLECTION,
    )

    print("=== ETL terminado correctamente ===\n")
    return resumen


def main():
    """Ejecuta una corrida manual manteniendo la excepción para callers internos."""
    client = None

    try:
        client, db = connect_database()
        print("MongoDB conectado correctamente.")
        ejecutar_etl(db)
    finally:
        close_database(client)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Mantiene código de salida != 0 sin imprimir URI/host/topología que
        # puedan venir en el mensaje o traceback del driver.
        print(f"ERROR ETL: {type(exc).__name__}")
        raise SystemExit(1) from None
