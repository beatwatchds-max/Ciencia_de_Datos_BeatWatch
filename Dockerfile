FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system beatwatch \
    && adduser --system --ingroup beatwatch beatwatch

COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

COPY --chown=beatwatch:beatwatch . .

USER beatwatch

CMD ["python", "trigger.py"]
