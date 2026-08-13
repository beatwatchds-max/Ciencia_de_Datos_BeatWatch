# Diagnóstico DevSecOps - Ciencia_de_Datos_BeatWatch

Fecha de revisión: 2026-08-13

## Resumen

El repositorio ya tenía una base DevSecOps razonable: CI, Ruff, Pytest, Bandit, pip-audit, CodeQL, Dependency Review, Dependabot, `.env` ignorado y ejecución Docker sin root. Sin embargo, todavía no podía considerarse una implementación completa de mejores prácticas por exposición de datos en scripts de diagnóstico y por varios controles de cadena de suministro y CI mejorables.

## Hallazgos

### Alta - exposición de documentos completos en `test_extract.py`

El script imprimía el primer documento completo de arritmias, episodios y actividades. Esos documentos pueden incluir identificadores de paciente y métricas clínicas. Se eliminó el volcado y se conservaron únicamente conteos agregados.

### Alta/Media - errores completos de MongoDB en logs

`test_extract.py`, `test_connection.py`, `main.py` y `trigger.py` podían imprimir el texto completo de excepciones, y `load.py` interpolaba directamente un `PyMongoError`. Los drivers pueden incluir host, topología, URI u otros detalles internos. Se sanitizaron esos mensajes sin cambiar la lógica de negocio ni las operaciones del ETL.

### Media - `.env.example` documentado pero ausente

El README indicaba copiar `.env.example`, pero el archivo no estaba en el árbol revisado. Se añadió una plantilla sin secretos.

### Media - contexto Docker demasiado amplio

El Dockerfile usaba `COPY . .`, lo que facilita incorporar archivos que no son necesarios para runtime. Se cambió a copia selectiva de los módulos requeridos por el worker y se reforzó `.dockerignore`.

### Media - referencias de GitHub Actions por tag móvil

Los workflows usaban referencias como `@v7` y `@v4`. Se fijaron las versiones revisadas a SHA completo y se añadió `persist-credentials: false` al checkout.

### Media - CI sin gate explícito de secretos ni validación del contenedor

Se añadió un escaneo de patrones de secretos de alta confianza y comprobaciones de que la imagen corre sin root y no contiene scripts de prueba ni `.env`.

### Baja/Media - auditoría sólo de dependencias runtime

El CI auditaba `requirements.txt` pero no `requirements-dev.txt`. Ahora ambos conjuntos pasan por `pip-audit`.

## Información expuesta encontrada

No se observó en los archivos públicos revisados una URI real de MongoDB hardcodeada, contraseña, API key o token. El historial público visible contiene dos commits; la búsqueda pública tampoco devolvió cadenas de credenciales conocidas.

Sí existía una exposición potencial de información sensible a través de los logs de `test_extract.py`, porque se imprimían documentos reales de las colecciones de salud. Este paquete corrige ese punto.

## Controles que requieren configuración en GitHub

No pueden garantizarse únicamente mediante archivos del repositorio. Deben verificarse en Settings:

- Secret scanning y Push protection;
- Dependabot alerts/security updates;
- Ruleset o protección de `main`;
- checks obligatorios antes de merge;
- revisión requerida de Pull Requests.

## Estado esperado después del hardening

El flujo funcional del ETL permanece sin cambios. `main.py`, `trigger.py` y `load.py` conservan las mismas operaciones y rutas de éxito; únicamente se evita volcar detalles sensibles cuando ocurre una excepción. El resto del endurecimiento actúa sobre repositorio, CI, contenedor, dependencias, secretos y scripts de diagnóstico.
