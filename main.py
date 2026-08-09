from database import connect_database, close_database
from extract import extract_all
from transform import transform
from load import load
from config import ESTADISTICAS_COLLECTION


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
    client = None

    try:
        client, db = connect_database()
        print(f"MongoDB conectado: {db.name}")
        ejecutar_etl(db)

    except Exception as exc:
        print(f"ERROR: {exc}")
        raise

    finally:
        close_database(client)


if __name__ == "__main__":
    main()
