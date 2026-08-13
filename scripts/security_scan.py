"""Escaneo ligero de secretos para CI sin dependencias adicionales.

No sustituye GitHub Secret Scanning/Push Protection. Su objetivo es añadir
un gate determinista al pipeline para patrones de alta confianza.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "htmlcov",
    "dist",
    "build",
}

TEXT_EXTENSIONS = {
    ".py",
    ".yml",
    ".yaml",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
    ".md",
    ".txt",
    ".env",
}

# Se construye en dos partes para que el propio scanner no contenga de forma
# literal el encabezado completo que busca.
PRIVATE_KEY_MARKER = "-----BEGIN " + "PRIVATE KEY-----"

PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "URI de MongoDB con credenciales embebidas",
        re.compile(r"mongodb(?:\+srv)?://[^\s:/@]+:[^\s@]+@", re.IGNORECASE),
    ),
    (
        "Token de GitHub",
        re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    ),
    (
        "AWS Access Key",
        re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    ),
)

GENERIC_SECRET = re.compile(
    r"(?i)\b(password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key)\b"
    r"\s*[:=]\s*[\"']([^\"']{8,})[\"']"
)

SAFE_PLACEHOLDERS = (
    "example",
    "changeme",
    "replace_me",
    "your_",
    "dummy",
    "placeholder",
    "localhost",
    "test",
    "${",
    "<",
)


def _is_text_candidate(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    if path.name == ".env.example":
        return True
    return path.suffix.lower() in TEXT_EXTENSIONS or path.name in {
        "Dockerfile",
        ".gitignore",
        ".dockerignore",
    }


def _scan_file(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    findings: list[str] = []
    relative = path.relative_to(ROOT)

    if PRIVATE_KEY_MARKER in text:
        findings.append(f"{relative}: posible clave privada")

    for label, pattern in PATTERNS:
        if pattern.search(text):
            findings.append(f"{relative}: {label}")

    for match in GENERIC_SECRET.finditer(text):
        value = match.group(2).strip().lower()
        if not value.startswith(SAFE_PLACEHOLDERS):
            findings.append(
                f"{relative}: posible secreto hardcodeado en campo {match.group(1)}"
            )

    return findings


def main() -> int:
    findings: list[str] = []

    for path in ROOT.rglob("*"):
        if path.is_file() and _is_text_candidate(path):
            findings.extend(_scan_file(path))

    if findings:
        print("Posibles secretos detectados:")
        for finding in sorted(set(findings)):
            print(f" - {finding}")
        return 1

    print("Escaneo local de secretos: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
