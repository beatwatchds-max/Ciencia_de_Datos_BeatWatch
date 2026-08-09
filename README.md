# BeatWatch ETL

ETL en Python para BeatWatch que:

1. Extrae datos desde MongoDB.
2. Limpia y normaliza arritmias, episodios y actividad diaria.
3. Genera estadísticas diarias.
4. Guarda los resultados con `upsert` en MongoDB.
5. Puede funcionar de manera automática con MongoDB Change Streams.

## Instalación

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copia `.env.example` como `.env` y coloca tu conexión real de MongoDB.

## Ejecución manual

```powershell
python main.py
```

Esto ejecuta una sola corrida:

```text
EXTRACT -> TRANSFORM -> LOAD
```

## Trigger automático agrupado

`trigger.py` escucha con MongoDB Change Streams estas colecciones:

- `Arritmias`
- `EpisodiosArritmia`
- `ActividadesDiarias`

Los eventos `insert`, `update`, `replace` y `delete` **no disparan el ETL uno por uno**.
Se acumulan en memoria dentro de una ventana y, al terminar esa ventana, se ejecuta **una sola corrida del ETL**.

Ejemplo con una ventana de 60 segundos:

```text
00 s  -> llegan 20 cambios
15 s  -> llegan 40 cambios
35 s  -> llegan 10 cambios
60 s  -> se ejecuta 1 ETL para los 70 cambios acumulados
```

Configura el intervalo en `.env`:

```env
ETL_BATCH_INTERVAL_SECONDS=60
```

Se aceptan valores entre **30 y 60 segundos**.

Para iniciar el worker:

```powershell
python trigger.py
```

Al arrancar, por defecto se ejecuta una sincronización completa para evitar que un reinicio del worker deje estadísticas pendientes:

```env
ETL_RUN_ON_STARTUP=true
```

Si una corrida falla, el lote se conserva y se vuelve a intentar después de otra ventana, evitando un ciclo de reintentos inmediato.

## Render

Despliega el proceso automático como **Background Worker**.

Start Command:

```text
python trigger.py
```

Variables mínimas:

```text
MONGO_CONNECTION_STRING
DB_NAME
ETL_BATCH_INTERVAL_SECONDS=60
ETL_RUN_ON_STARTUP=true
```

MongoDB Change Streams requiere MongoDB Atlas o un replica set.

# DevSecOps incluido

El proyecto incorpora controles automáticos bajo `.github/`.

## 1. CI: calidad + pruebas + seguridad

Workflow:

```text
.github/workflows/ci-security.yml
```

Ejecuta en cada `push`/Pull Request hacia `main`:

- compilación de archivos Python;
- Ruff;
- pruebas unitarias con Pytest;
- Bandit SAST;
- `pip-audit` para dependencias vulnerables.

## 2. CodeQL

Workflow:

```text
.github/workflows/codeql.yml
```

Analiza Python en push, Pull Requests y semanalmente.

## 3. Dependency Review

Workflow:

```text
.github/workflows/dependency-review.yml
```

Revisa dependencias nuevas en Pull Requests y bloquea vulnerabilidades de severidad alta.

> En repositorios privados, algunas funciones de seguridad de GitHub pueden depender del plan/configuración de Code Security.

## 4. Dependabot

Archivo:

```text
.github/dependabot.yml
```

Busca actualizaciones semanales para:

- paquetes de Python;
- GitHub Actions.

## 5. Secretos

El `.env` real está excluido por `.gitignore`. Solo se versiona `.env.example`.

En GitHub se recomienda habilitar **Secret scanning + Push protection** y en Render configurar la conexión de MongoDB como variable de entorno.

## 6. Contenedor endurecido

El `Dockerfile` ejecuta BeatWatch con un usuario sin privilegios llamado `beatwatch`, no como `root`.

Construcción local:

```powershell
docker build -t beatwatch-etl .
docker run --env-file .env beatwatch-etl
```

## 7. Protección de `main`

En GitHub protege `main` con Rulesets/Branch protection y exige los checks de CI antes de permitir merge.

Consulta `SECURITY.md` para la lista de controles recomendados.
