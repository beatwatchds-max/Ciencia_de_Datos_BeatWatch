# Seguridad - BeatWatch ETL

## Controles incluidos

- Secretos fuera del repositorio mediante `.env` y variables de entorno.
- `.env` ignorado por Git.
- CI con compilación, Ruff, pruebas, Bandit y `pip-audit`.
- CodeQL para análisis de código en GitHub.
- Dependency Review en Pull Requests.
- Dependabot para dependencias de Python y GitHub Actions.
- Docker ejecutado con usuario sin privilegios (`beatwatch`).
- Reintento controlado del lote si una corrida ETL falla.
- Sincronización inicial para recuperar consistencia después de reinicios.

## Configuración recomendada en GitHub

En **Settings > Security / Code security** activa, cuando esté disponible para el repositorio:

1. Secret scanning.
2. Push protection.
3. Code scanning / CodeQL.
4. Dependabot alerts y security updates.

En **Settings > Branches / Rulesets** protege `main` y exige que pase:

- `CI / quality-and-security-gates`
- `CodeQL`
- `Dependency Review` para Pull Requests

No guardes `MONGO_CONNECTION_STRING` en archivos versionados. En Render/GitHub usa sus gestores de variables y secretos.
