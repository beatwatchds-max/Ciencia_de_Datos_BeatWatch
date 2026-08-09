from config import (
    ARRITMIAS_COLLECTION,
    EPISODIOS_COLLECTION,
    ACTIVIDADES_COLLECTION
)


def extract_arritmias(db):
    """
    Extrae todos los registros de la colección Arritmias.
    """

    collection = db[ARRITMIAS_COLLECTION]

    documentos = list(
        collection.find({})
    )

    print(
        f"Arritmias extraídas: {len(documentos)}"
    )

    return documentos


def extract_episodios(db):
    """
    Extrae todos los registros de EpisodiosArritmia.
    """

    collection = db[EPISODIOS_COLLECTION]

    documentos = list(
        collection.find({})
    )

    print(
        f"Episodios de arritmia extraídos: {len(documentos)}"
    )

    return documentos


def extract_actividades(db):
    """
    Extrae todos los registros de ActividadesDiarias.
    """

    collection = db[ACTIVIDADES_COLLECTION]

    documentos = list(
        collection.find({})
    )

    print(
        f"Actividades diarias extraídas: {len(documentos)}"
    )

    return documentos


def extract_all(db):
    """
    Ejecuta toda la fase Extract.
    """

    print("\n================================")
    print("INICIANDO EXTRACT")
    print("================================")

    arritmias = extract_arritmias(db)

    episodios = extract_episodios(db)

    actividades = extract_actividades(db)

    print("\n================================")
    print("EXTRACT FINALIZADO")
    print("================================")

    return {
        "arritmias": arritmias,
        "episodios": episodios,
        "actividades": actividades
    }

