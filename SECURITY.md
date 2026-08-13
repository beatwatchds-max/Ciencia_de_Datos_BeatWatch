# Seguridad - BeatWatch ETL

## Alcance

Este repositorio procesa información asociada a pacientes y métricas cardiacas. Los datos reales, identificadores de pacientes, credenciales, cadenas de conexión y volcados de MongoDB no deben publicarse en GitHub, issues, Pull Requests, capturas ni logs compartidos.

## Controles incluidos

- Secretos mediante variables de entorno; `.env` y variantes locales excluidas de Git.
- `.env.example` sin credenciales reales.
- CI con compilación, Ruff, Pytest, Bandit, auditoría de dependencias y gate local de secretos.
- CodeQL para análisis estático adicional.
- Dependency Review en Pull Requests.
- Dependabot para Python y GitHub Actions.
- GitHub Actions con permisos mínimos y referencias fijadas a SHA completo.
- Docker ejecutado con usuario `beatwatch`, sin privilegios de root.
- Imagen Docker con copia selectiva de archivos de runtime.
- Pruebas de regresión para impedir que vuelvan a aparecer volcados de documentos clínicos en scripts de diagnóstico.

## Manejo de información sensible

Nunca registres en logs:

- `MONGO_CONNECTION_STRING` ni credenciales de MongoDB;
- documentos completos de `Arritmias`, `EpisodiosArritmia`, `ActividadesDiarias` o `EstadisticasDiarias`;
- identificadores de pacientes salvo que sean imprescindibles y estén adecuadamente protegidos;
- tokens, API keys, contraseñas o claves privadas.

Los scripts `test_connection.py` y `test_extract.py` sólo deben mostrar estado y conteos agregados.

## Configuración recomendada en GitHub

En **Settings > Code security** verifica/activa:

1. Secret scanning.
2. Push protection.
3. Code scanning / CodeQL.
4. Dependabot alerts.
5. Dependabot security updates.

En **Settings > Rules > Rulesets** protege `main` y exige como checks obligatorios:

- `CI / quality-and-security-gates`;
- `CodeQL`;
- `Dependency Review` en Pull Requests.

Activa revisión de Pull Request antes del merge y evita pushes directos a `main`.

## Si se expone una credencial

1. Revoca o rota la credencial inmediatamente; no basta con borrar el archivo.
2. Sustituye el secreto en Render/MongoDB/GitHub por uno nuevo.
3. Elimina el secreto del historial Git si llegó a versionarse.
4. Revisa logs y accesos relacionados con la credencial expuesta.
5. Ejecuta nuevamente Secret Scanning, CI y auditoría de dependencias.

## Reporte de vulnerabilidades

No publiques secretos, datos de pacientes ni detalles explotables en un issue público. Usa el mecanismo privado de reporte de vulnerabilidades/Security Advisory del repositorio cuando esté habilitado.
