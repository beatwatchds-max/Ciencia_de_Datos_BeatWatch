from batching import LoteCambios


def crear_cambio(coleccion="Arritmias", operacion="insert"):
    return {
        "ns": {"coll": coleccion},
        "operationType": operacion,
    }


def test_lote_no_esta_listo_antes_del_intervalo():
    lote = LoteCambios()
    lote.registrar(crear_cambio(), ahora=100.0)

    assert lote.total == 1
    assert lote.listo(129.9, 30) is False
    assert lote.listo(130.0, 30) is True


def test_lote_agrupa_varios_cambios_en_una_sola_ventana():
    lote = LoteCambios()
    lote.registrar(crear_cambio("Arritmias", "insert"), ahora=10.0)
    lote.registrar(crear_cambio("Arritmias", "update"), ahora=20.0)
    lote.registrar(crear_cambio("ActividadesDiarias", "insert"), ahora=30.0)

    assert lote.total == 3
    assert lote.inicio_monotonic == 10.0
    assert lote.por_coleccion["Arritmias"] == 2
    assert lote.por_coleccion["ActividadesDiarias"] == 1
    assert lote.por_operacion["insert"] == 2
    assert lote.por_operacion["update"] == 1


def test_reiniciar_limpia_el_lote():
    lote = LoteCambios()
    lote.registrar(crear_cambio(), ahora=1.0)
    lote.reiniciar()

    assert lote.total == 0
    assert lote.inicio_monotonic is None
    assert not lote.por_coleccion
    assert not lote.por_operacion


def test_reintento_conserva_cambios_y_mueve_la_ventana():
    lote = LoteCambios()
    lote.registrar(crear_cambio(), ahora=1.0)
    lote.posponer_reintento(60.0)

    assert lote.total == 1
    assert lote.inicio_monotonic == 60.0
