from datetime import datetime
from statistics import mean


# ============================================================
# CONFIGURACIÓN
# ============================================================

FC_MIN = 30
FC_MAX = 220

PASOS_MAX = 100000
CALORIAS_MAX = 10000
DISTANCIA_MAX = 200
SUENO_MAX = 24

DURACION_MAX_SECONDS = 24 * 60 * 60


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def obtener_fecha(fecha):
    """
    Convierte una fecha de MongoDB a datetime.
    """
    if isinstance(fecha, datetime):
        return fecha

    return None


def fecha_corta(fecha):
    """
    Obtiene únicamente la fecha YYYY-MM-DD.
    """
    if not isinstance(fecha, datetime):
        return None

    return fecha.strftime("%Y-%m-%d")


def valor_seguro(valor, default=0):
    """
    Convierte valores numéricos a float/int seguros.
    """
    try:
        if valor is None:
            return default

        return float(valor)

    except (ValueError, TypeError):
        return default


# ============================================================
# TRANSFORMAR ARRITMIAS
# ============================================================

def transformar_arritmias(arritmias):
    """
    Limpia y normaliza las arritmias.
    """

    resultado = []

    descartadas = 0

    for arritmia in arritmias:

        fecha = obtener_fecha(arritmia.get("Fecha"))

        if fecha is None:
            descartadas += 1
            continue

        frecuencia = valor_seguro(
            arritmia.get("FrecuenciaCardiaca")
        )

        duracion = valor_seguro(
            arritmia.get("DuracionEpisodioSeconds")
        )

        # ----------------------------------------------------
        # Validación de frecuencia cardiaca
        # ----------------------------------------------------

        frecuencia_valida = (
            FC_MIN <= frecuencia <= FC_MAX
        )

        if not frecuencia_valida:
            frecuencia = None

        # ----------------------------------------------------
        # Validación de duración
        # ----------------------------------------------------

        duracion_valida = (
            0 <= duracion <= DURACION_MAX_SECONDS
        )

        if not duracion_valida:
            duracion = None

        # ----------------------------------------------------
        # Síntomas
        # ----------------------------------------------------

        sintomas = arritmia.get("Sintomas", {})

        if sintomas is None:
            sintomas = {}

        transformada = {
            "Id": arritmia.get("_id"),
            "IdPaciente": arritmia.get("IdPaciente"),
            "Tipo": arritmia.get("Tipo", "Desconocida"),
            "FrecuenciaCardiaca": frecuencia,
            "DuracionEpisodioSeconds": duracion,
            "Fecha": fecha,
            "FechaCorta": fecha_corta(fecha),

            "Sintomas": {
                "Mareo": bool(sintomas.get("Mareo", False)),
                "Palpitaciones": bool(
                    sintomas.get("Palpitaciones", False)
                ),
                "DolorPecho": bool(
                    sintomas.get("DolorPecho", False)
                ),
                "Desmayo": bool(
                    sintomas.get("Desmayo", False)
                ),
                "FaltaAire": bool(
                    sintomas.get("FaltaAire", False)
                ),
                "Fatiga": bool(
                    sintomas.get("Fatiga", False)
                )
            },

            "FrecuenciaValida": frecuencia_valida,
            "DuracionValida": duracion_valida
        }

        resultado.append(transformada)

    print(
        f"Arritmias transformadas: {len(resultado)}"
    )

    print(
        f"Arritmias descartadas: {descartadas}"
    )

    return resultado


# ============================================================
# TRANSFORMAR EPISODIOS
# ============================================================

def transformar_episodios(episodios):
    """
    Limpia y normaliza los episodios de arritmia.
    """

    resultado = []

    descartados = 0

    for episodio in episodios:

        fecha = obtener_fecha(
            episodio.get("Fecha")
        )

        if fecha is None:
            descartados += 1
            continue

        frecuencia = valor_seguro(
            episodio.get("FrecuenciaCardiaca")
        )

        duracion = valor_seguro(
            episodio.get("DuracionEpisodioSeconds")
        )

        # ----------------------------------------------------
        # Validación de frecuencia
        # ----------------------------------------------------

        frecuencia_valida = (
            FC_MIN <= frecuencia <= FC_MAX
        )

        if not frecuencia_valida:
            frecuencia = None

        # ----------------------------------------------------
        # Validación de duración
        # ----------------------------------------------------

        duracion_valida = (
            0 <= duracion <= DURACION_MAX_SECONDS
        )

        if not duracion_valida:
            duracion = None

        # ----------------------------------------------------
        # Tipo de anomalía
        # ----------------------------------------------------

        tipo = episodio.get(
            "TipoAnomalia",
            "Desconocida"
        )

        if not tipo or tipo == "string":
            tipo = "Desconocida"

        # ----------------------------------------------------
        # Transformación
        # ----------------------------------------------------

        transformado = {
            "Id": episodio.get("_id"),
            "IdPaciente": episodio.get("IdPaciente"),
            "TipoAnomalia": tipo,
            "FrecuenciaCardiaca": frecuencia,
            "DuracionEpisodioSeconds": duracion,
            "EsAlertaCritica": bool(
                episodio.get(
                    "EsAlertaCritica",
                    False
                )
            ),
            "Fecha": fecha,
            "FechaCorta": fecha_corta(fecha),

            "FrecuenciaValida": frecuencia_valida,
            "DuracionValida": duracion_valida
        }

        resultado.append(transformado)

    print(
        f"Episodios transformados: {len(resultado)}"
    )

    print(
        f"Episodios descartados: {descartados}"
    )

    return resultado


# ============================================================
# TRANSFORMAR ACTIVIDADES
# ============================================================

def transformar_actividades(actividades):
    """
    Limpia y normaliza las actividades diarias.
    """

    resultado = []

    descartadas = 0

    for actividad in actividades:

        fecha_sync = obtener_fecha(
            actividad.get("FechaSincronizacion")
        )

        if fecha_sync is None:
            descartadas += 1
            continue

        # ----------------------------------------------------
        # Fecha corta
        # ----------------------------------------------------

        fecha_original = actividad.get(
            "FechaCorta"
        )

        fecha_valida = None

        try:

            fecha_valida = datetime.strptime(
                fecha_original,
                "%Y-%m-%d"
            )

        except (ValueError, TypeError):

            # Si FechaCorta está dañada,
            # utilizamos FechaSincronizacion.
            fecha_valida = fecha_sync

        # ----------------------------------------------------
        # Valores
        # ----------------------------------------------------

        pasos = valor_seguro(
            actividad.get("Pasos")
        )

        calorias = valor_seguro(
            actividad.get("Calorias")
        )

        distancia = valor_seguro(
            actividad.get("DistanciaKm")
        )

        horas_sueno = valor_seguro(
            actividad.get("HorasSueno")
        )

        # ----------------------------------------------------
        # Validaciones
        # ----------------------------------------------------

        pasos_valido = (
            0 <= pasos <= PASOS_MAX
        )

        calorias_valida = (
            0 <= calorias <= CALORIAS_MAX
        )

        distancia_valida = (
            0 <= distancia <= DISTANCIA_MAX
        )

        sueno_valido = (
            0 <= horas_sueno <= SUENO_MAX
        )

        # ----------------------------------------------------
        # Si el dato es inválido, se convierte en None
        # ----------------------------------------------------

        if not pasos_valido:
            pasos = None

        if not calorias_valida:
            calorias = None

        if not distancia_valida:
            distancia = None

        if not sueno_valido:
            horas_sueno = None

        # ----------------------------------------------------
        # Transformación
        # ----------------------------------------------------

        transformada = {
            "Id": actividad.get("_id"),
            "IdPaciente": actividad.get("IdPaciente"),

            "Fecha": fecha_valida,
            "FechaCorta": fecha_corta(fecha_valida),

            "Pasos": int(pasos)
            if pasos is not None else None,

            "Calorias": calorias,

            "DistanciaKm": distancia,

            "HorasSueno": horas_sueno,

            "FechaSincronizacion": fecha_sync,

            "PasosValidos": pasos_valido,
            "CaloriasValidas": calorias_valida,
            "DistanciaValida": distancia_valida,
            "SuenoValido": sueno_valido
        }

        resultado.append(transformada)

    print(
        f"Actividades transformadas: {len(resultado)}"
    )

    print(
        f"Actividades descartadas: {descartadas}"
    )

    return resultado


# ============================================================
# GENERAR ESTADÍSTICAS DIARIAS
# ============================================================

def generar_estadisticas_diarias(
    arritmias,
    episodios,
    actividades
):
    """
    Agrupa la información por paciente y día
    para posteriormente cargarla en MongoDB.
    """

    estadisticas = {}

    # --------------------------------------------------------
    # ARRITMIAS
    # --------------------------------------------------------

    for arritmia in arritmias:

        paciente = arritmia.get(
            "IdPaciente"
        )

        fecha = arritmia.get(
            "FechaCorta"
        )

        if paciente is None or fecha is None:
            continue

        clave = (
            str(paciente),
            fecha
        )

        if clave not in estadisticas:

            estadisticas[clave] = {
                "IdPaciente": paciente,
                "Fecha": fecha,

                "TotalArritmias": 0,
                "TotalEpisodios": 0,

                "FrecuenciaMaxima": None,
                "FrecuenciaMinima": None,
                "FrecuenciaPromedio": None,

                "DuracionTotalEpisodios": 0,

                "AlertasCriticas": 0,

                "TotalPasos": 0,
                "TotalCalorias": 0,
                "DistanciaTotalKm": 0,
                "HorasSueno": None,

                "_frecuencias": [],
                "_duraciones": []
            }

        estadistica = estadisticas[clave]

        estadistica[
            "TotalArritmias"
        ] += 1

        frecuencia = arritmia.get(
            "FrecuenciaCardiaca"
        )

        if frecuencia is not None:

            estadistica[
                "_frecuencias"
            ].append(frecuencia)

        duracion = arritmia.get(
            "DuracionEpisodioSeconds"
        )

        if duracion is not None:

            estadistica[
                "_duraciones"
            ].append(duracion)

    # --------------------------------------------------------
    # EPISODIOS
    # --------------------------------------------------------

    for episodio in episodios:

        paciente = episodio.get(
            "IdPaciente"
        )

        fecha = episodio.get(
            "FechaCorta"
        )

        if paciente is None or fecha is None:
            continue

        clave = (
            str(paciente),
            fecha
        )

        if clave not in estadisticas:

            estadisticas[clave] = {
                "IdPaciente": paciente,
                "Fecha": fecha,

                "TotalArritmias": 0,
                "TotalEpisodios": 0,

                "FrecuenciaMaxima": None,
                "FrecuenciaMinima": None,
                "FrecuenciaPromedio": None,

                "DuracionTotalEpisodios": 0,

                "AlertasCriticas": 0,

                "TotalPasos": 0,
                "TotalCalorias": 0,
                "DistanciaTotalKm": 0,
                "HorasSueno": None,

                "_frecuencias": [],
                "_duraciones": []
            }

        estadistica = estadisticas[clave]

        estadistica[
            "TotalEpisodios"
        ] += 1

        frecuencia = episodio.get(
            "FrecuenciaCardiaca"
        )

        if frecuencia is not None:

            estadistica[
                "_frecuencias"
            ].append(frecuencia)

        duracion = episodio.get(
            "DuracionEpisodioSeconds"
        )

        if duracion is not None:

            estadistica[
                "_duraciones"
            ].append(duracion)

        if episodio.get(
            "EsAlertaCritica",
            False
        ):

            estadistica[
                "AlertasCriticas"
            ] += 1

    # --------------------------------------------------------
    # ACTIVIDADES
    # --------------------------------------------------------

    for actividad in actividades:

        paciente = actividad.get(
            "IdPaciente"
        )

        fecha = actividad.get(
            "FechaCorta"
        )

        if paciente is None or fecha is None:
            continue

        clave = (
            str(paciente),
            fecha
        )

        if clave not in estadisticas:

            estadisticas[clave] = {
                "IdPaciente": paciente,
                "Fecha": fecha,

                "TotalArritmias": 0,
                "TotalEpisodios": 0,

                "FrecuenciaMaxima": None,
                "FrecuenciaMinima": None,
                "FrecuenciaPromedio": None,

                "DuracionTotalEpisodios": 0,

                "AlertasCriticas": 0,

                "TotalPasos": 0,
                "TotalCalorias": 0,
                "DistanciaTotalKm": 0,
                "HorasSueno": None,

                "_frecuencias": [],
                "_duraciones": []
            }

        estadistica = estadisticas[clave]

        if actividad.get(
            "Pasos"
        ) is not None:

            estadistica[
                "TotalPasos"
            ] += actividad["Pasos"]

        if actividad.get(
            "Calorias"
        ) is not None:

            estadistica[
                "TotalCalorias"
            ] += actividad["Calorias"]

        if actividad.get(
            "DistanciaKm"
        ) is not None:

            estadistica[
                "DistanciaTotalKm"
            ] += actividad["DistanciaKm"]

        if actividad.get(
            "HorasSueno"
        ) is not None:

            estadistica[
                "HorasSueno"
            ] = actividad["HorasSueno"]

    # --------------------------------------------------------
    # CALCULAR PROMEDIOS Y TOTALES
    # --------------------------------------------------------

    resultado = []

    for estadistica in estadisticas.values():

        frecuencias = estadistica.pop(
            "_frecuencias"
        )

        duraciones = estadistica.pop(
            "_duraciones"
        )

        if frecuencias:

            estadistica[
                "FrecuenciaMaxima"
            ] = max(frecuencias)

            estadistica[
                "FrecuenciaMinima"
            ] = min(frecuencias)

            estadistica[
                "FrecuenciaPromedio"
            ] = round(
                mean(frecuencias),
                2
            )

        if duraciones:

            estadistica[
                "DuracionTotalEpisodios"
            ] = sum(duraciones)

        resultado.append(
            estadistica
        )

    print(
        f"Estadísticas diarias generadas: "
        f"{len(resultado)}"
    )

    return resultado


# ============================================================
# FUNCIÓN PRINCIPAL DEL TRANSFORM
# ============================================================

def transform(data):
    """
    Ejecuta todo el proceso de transformación.

    Recibe el resultado del EXTRACT.
    """

    print("")
    print("================================")
    print("INICIANDO TRANSFORM")
    print("================================")

    arritmias = data.get(
        "arritmias",
        []
    )

    episodios = data.get(
        "episodios",
        []
    )

    actividades = data.get(
        "actividades",
        []
    )

    # --------------------------------------------------------
    # Transformaciones individuales
    # --------------------------------------------------------

    arritmias_transformadas = transformar_arritmias(
        arritmias
    )

    episodios_transformados = transformar_episodios(
        episodios
    )

    actividades_transformadas = transformar_actividades(
        actividades
    )

    # --------------------------------------------------------
    # Generar estadísticas
    # --------------------------------------------------------

    estadisticas_diarias = generar_estadisticas_diarias(
        arritmias_transformadas,
        episodios_transformados,
        actividades_transformadas
    )

    print("")
    print("================================")
    print("TRANSFORM FINALIZADO")
    print("================================")

    print("")
    print("RESUMEN DEL TRANSFORM")
    print("--------------------------------")
    print(
        f"Arritmias: "
        f"{len(arritmias_transformadas)}"
    )
    print(
        f"Episodios: "
        f"{len(episodios_transformados)}"
    )
    print(
        f"Actividades: "
        f"{len(actividades_transformadas)}"
    )
    print(
        f"Estadísticas diarias: "
        f"{len(estadisticas_diarias)}"
    )

    return {
        "arritmias": arritmias_transformadas,
        "episodios": episodios_transformados,
        "actividades": actividades_transformadas,
        "estadisticas_diarias": estadisticas_diarias
    }


# ============================================================
# PRUEBA DIRECTA
# ============================================================

if __name__ == "__main__":

    print(
        "transform.py listo."
    )

    print(
        "Debe ejecutarse desde el pipeline ETL "
        "recibiendo los datos de extract.py."
    )