from database import connect_database
from extract import extract_all

def main():

    client = None

    try:

        client, db = connect_database()

        datos = extract_all(db)

        print("\n================================")
        print("RESUMEN DEL EXTRACT")
        print("================================")

        print(
            f"Arritmias: "
            f"{len(datos['arritmias'])}"
        )

        print(
            f"Episodios: "
            f"{len(datos['episodios'])}"
        )

        print(
            f"Actividades: "
            f"{len(datos['actividades'])}"
        )

        # Mostrar un documento de ejemplo
        if datos["arritmias"]:

            print("\n================================")
            print("EJEMPLO DE ARRITMIA")
            print("================================")

            print(
                datos["arritmias"][0]
            )

        if datos["episodios"]:

            print("\n================================")
            print("EJEMPLO DE EPISODIO")
            print("================================")

            print(
                datos["episodios"][0]
            )

        if datos["actividades"]:

            print("\n================================")
            print("EJEMPLO DE ACTIVIDAD")
            print("================================")

            print(
                datos["actividades"][0]
            )

    except Exception as error:

        print("\n================================")
        print("ERROR EN EXTRACT")
        print("================================")

        print(error)

    finally:

        if client:
            client.close()


if __name__ == "__main__":
    main()

