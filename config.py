import os

from dotenv import load_dotenv


load_dotenv()


MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")

DB_NAME = os.getenv("DB_NAME", "BeatWatchDb_Dev")

ARRITMIAS_COLLECTION = os.getenv("ARRITMIAS_COLLECTION", "Arritmias")
EPISODIOS_COLLECTION = os.getenv("EPISODIOS_COLLECTION", "EpisodiosArritmia")
ACTIVIDADES_COLLECTION = os.getenv("ACTIVIDADES_COLLECTION", "ActividadesDiarias")
ESTADISTICAS_COLLECTION = os.getenv("ESTADISTICAS_COLLECTION", "EstadisticasDiarias")


def _leer_intervalo_lote() -> int:
    valor = os.getenv("ETL_BATCH_INTERVAL_SECONDS", "60")

    try:
        intervalo = int(valor)
    except ValueError as exc:
        raise RuntimeError(
            "ETL_BATCH_INTERVAL_SECONDS debe ser un número entero entre 30 y 60."
        ) from exc

    if not 30 <= intervalo <= 60:
        raise RuntimeError(
            "ETL_BATCH_INTERVAL_SECONDS debe estar entre 30 y 60 segundos."
        )

    return intervalo


def _leer_booleano(nombre: str, default: bool) -> bool:
    valor_default = "true" if default else "false"
    valor = os.getenv(nombre, valor_default).strip().lower()

    if valor in {"1", "true", "yes", "si", "sí", "on"}:
        return True
    if valor in {"0", "false", "no", "off"}:
        return False

    raise RuntimeError(
        f"{nombre} debe usar true/false, 1/0, yes/no o on/off."
    )


ETL_BATCH_INTERVAL_SECONDS = _leer_intervalo_lote()
ETL_RUN_ON_STARTUP = _leer_booleano("ETL_RUN_ON_STARTUP", True)
CHANGE_STREAM_MAX_AWAIT_MS = 1_000


def validate_config() -> None:
    """Valida secretos/configuración únicamente cuando se necesita MongoDB."""

    if not MONGO_CONNECTION_STRING:
        raise RuntimeError(
            "No se encontró MONGO_CONNECTION_STRING. Configúralo en .env "
            "o como variable de entorno del servicio."
        )
