from database import connect_database


def main():
    """Comprueba conectividad sin revelar nombres internos ni URI de MongoDB."""
    client = None

    try:
        client, db = connect_database()
        collections = db.list_collection_names()

        print("================================")
        print("CONEXION EXITOSA")
        print("================================")
        print(f"Colecciones accesibles: {len(collections)}")

    except Exception as error:
        print("================================")
        print("ERROR DE CONEXION")
        print("================================")
        print(f"Tipo de error: {type(error).__name__}")

    finally:
        if client:
            client.close()


if __name__ == "__main__":
    main()
