from pymongo import MongoClient

from config import DB_NAME, MONGO_CONNECTION_STRING, validate_config


def connect_database():
    validate_config()

    client = MongoClient(
        MONGO_CONNECTION_STRING,
        serverSelectionTimeoutMS=10_000,
        connectTimeoutMS=10_000,
        retryWrites=True,
    )

    # Fuerza una operación para detectar errores de conexión al arrancar.
    client.admin.command("ping")
    database = client[DB_NAME]

    return client, database


def close_database(client):
    if client is not None:
        client.close()
