from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_env_and_key_material_are_ignored():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

    required = {
        ".env",
        ".env.*",
        "!.env.example",
        "*.pem",
        "*.key",
        "credentials*.json",
    }

    for rule in required:
        assert rule in gitignore


def test_extract_diagnostic_does_not_dump_health_documents():
    source = (ROOT / "test_extract.py").read_text(encoding="utf-8")

    forbidden = (
        'datos["arritmias"][0]',
        'datos["episodios"][0]',
        'datos["actividades"][0]',
        "print(error)",
    )

    for marker in forbidden:
        assert marker not in source


def test_connection_diagnostic_does_not_print_collection_names():
    source = (ROOT / "test_connection.py").read_text(encoding="utf-8")

    assert "for collection in collections" not in source
    assert "print(error)" not in source


def test_docker_runs_non_root_and_uses_selective_copy():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "USER beatwatch" in dockerfile
    assert "COPY --chown=beatwatch:beatwatch . ." not in dockerfile
    assert "trigger.py" in dockerfile


def test_security_scanner_exists():
    scanner = ROOT / "scripts" / "security_scan.py"
    assert scanner.is_file()


def test_runtime_entrypoints_do_not_dump_driver_errors():
    main_source = (ROOT / "main.py").read_text(encoding="utf-8")
    trigger_source = (ROOT / "trigger.py").read_text(encoding="utf-8")
    load_source = (ROOT / "load.py").read_text(encoding="utf-8")

    assert 'print(f"ERROR: {exc}")' not in main_source
    assert 'ERROR DE MONGODB EN EL WORKER: {exc}' not in trigger_source
    assert 'No fue posible completar el LOAD en MongoDB: {error}' not in load_source
    assert "print(error)" not in load_source
