# Contrato recomendado para el backend

El ETL deja dos colecciones listas para que ASP.NET Core las exponga:

## 1. Estadísticas diarias

Colección:
`estadisticas_diarias`

Endpoint sugerido:

`GET /api/estadisticas/paciente/{pacienteId}/diarias?desde=2026-08-01&hasta=2026-08-04`

Respuesta:

```json
{
  "pacienteId": "123",
  "datos": [
    {
      "fecha": "2026-08-01",
      "frecuenciaCardiaca": {
        "promedio": 78.4,
        "minimo": 55,
        "maximo": 110,
        "mediana": 77,
        "lecturas": 8400
      },
      "arritmias": {
        "total": 2,
        "porTipo": {
          "Taquicardia": 1,
          "Bradicardia": 1
        }
      }
    }
  ]
}
```

## 2. Serie de frecuencia cardíaca

Colección:
`series_frecuencia_cardiaca`

Endpoint sugerido:

`GET /api/estadisticas/paciente/{pacienteId}/frecuencia?desde=...&hasta=...`

Respuesta:

```json
{
  "pacienteId": "123",
  "datos": [
    {
      "fecha": "2026-08-04T10:30:00Z",
      "valor": 82
    },
    {
      "fecha": "2026-08-04T10:31:00Z",
      "valor": 84
    }
  ]
}
```

Android/Kotlin puede consumir estas respuestas y dibujar las gráficas.
