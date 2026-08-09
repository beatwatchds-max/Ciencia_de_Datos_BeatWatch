from collections import Counter
from dataclasses import dataclass, field


@dataclass
class LoteCambios:
    """Estado del lote de cambios pendiente de procesar."""

    total: int = 0
    inicio_monotonic: float | None = None
    por_coleccion: Counter = field(default_factory=Counter)
    por_operacion: Counter = field(default_factory=Counter)

    @property
    def pendiente(self) -> bool:
        return self.total > 0

    def registrar(self, cambio: dict, ahora: float) -> None:
        if not self.pendiente:
            self.inicio_monotonic = ahora

        coleccion = cambio.get("ns", {}).get("coll", "desconocida")
        operacion = cambio.get("operationType", "desconocida")

        self.total += 1
        self.por_coleccion[coleccion] += 1
        self.por_operacion[operacion] += 1

    def listo(self, ahora: float, intervalo: int) -> bool:
        if not self.pendiente or self.inicio_monotonic is None:
            return False

        return ahora - self.inicio_monotonic >= intervalo

    def reiniciar(self) -> None:
        self.total = 0
        self.inicio_monotonic = None
        self.por_coleccion.clear()
        self.por_operacion.clear()

    def posponer_reintento(self, ahora: float) -> None:
        """Conserva el lote, pero evita un bucle de reintentos inmediato."""

        if self.pendiente:
            self.inicio_monotonic = ahora
