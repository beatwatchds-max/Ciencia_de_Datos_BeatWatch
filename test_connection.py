from database import connect_database
from config import DB_NAME


def main():

    client = None

    try:

        client, db = connect_database()

        print("================================")
        print("CONEXION EXITOSA")
        print("================================")

        print(f"Base de datos: {DB_NAME}")

        collections = db.list_collection_names()

        print("\nColecciones encontradas:")

        for collection in collections:
            print(f" - {collection}")

    except Exception as error:

        print("================================")
        print("ERROR DE CONEXION")
        print("================================")

        print(error)

    finally:

        if client:
            client.close()


if __name__ == "__main__":
    main()

