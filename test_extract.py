from database import connect_database
from extract import extract_all


def main():
    """Prueba manual del EXTRACT sin volcar datos clínicos en los logs."""
    client = None

    try:
        client, db = connect_database()
        datos = extract_all(db)

        print("\n================================")
        print("RESUMEN DEL EXTRACT")
        print("================================")
        print(f"Arritmias: {len(datos['arritmias'])}")
        print(f"Episodios: {len(datos['episodios'])}")
        print(f"Actividades: {len(datos['actividades'])}")
        print("Datos de ejemplo omitidos por seguridad.")

    except Exception as error:
        # No imprimir el mensaje completo: un driver puede incluir URI, host,
        # topología u otros datos internos en su representación de error.
        print("\n================================")
        print("ERROR EN EXTRACT")
        print("================================")
        print(f"Tipo de error: {type(error).__name__}")

    finally:
        if client:
            client.close()


if __name__ == "__main__":
    main()
