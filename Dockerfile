FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Usuario sin privilegios: el worker nunca se ejecuta como root.
RUN addgroup --system beatwatch \
    && adduser --system --ingroup beatwatch beatwatch

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copia únicamente los módulos necesarios en runtime. Evita incluir pruebas,
# documentación, metadatos de Git o archivos de configuración local.
COPY --chown=beatwatch:beatwatch \
    batching.py \
    config.py \
    database.py \
    extract.py \
    load.py \
    main.py \
    transform.py \
    trigger.py \
    ./

USER beatwatch

CMD ["python", "trigger.py"]
