# Documentación API

Base URL: `http://localhost:8000`

Documentación interactiva: `/docs` (Swagger) y `/redoc`

## Endpoints

### GET /health

Estado del sistema y conectividad a PostgreSQL.

**Respuesta:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-06-11T12:00:00"
}
```

### GET /pollution

Mediciones de contaminantes.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| pollutant | string | CO, MP10, MP25, NO2, O3 |
| start_date | date | Fecha inicio |
| end_date | date | Fecha fin |
| limit | int | Máximo registros (default 1000) |

### GET /pollution/daily

Métricas diarias agregadas. Mismos filtros de fecha y contaminante.

### GET /pollution/monthly

Métricas mensuales. Filtro opcional por contaminante.

### GET /weather

Datos meteorológicos diarios. Filtros: `start_date`, `end_date`.

### GET /analytics/correlation

Matriz de correlación entre contaminantes y variables meteorológicas.

### GET /analytics/trends

Tendencias lineales por contaminante (pendiente, R², dirección).

### GET /analytics/top-pollution-days

| Parámetro | Tipo | Default |
|-----------|------|---------|
| pollutant | string | todos |
| top_n | int | 10 |

### GET /analytics/annual-averages

Promedios anuales por contaminante.

### GET /analytics/etl-status

Estado de la última ejecución del pipeline ETL.

### GET /analytics/data-quality

Métricas de calidad de datos y última ejecución ETL:

| Campo | Descripción |
|-------|-------------|
| total_records | Total mediciones en BD |
| valid_records | Registros con status validated |
| preliminary_records | Registros preliminares |
| non_validated_records | Registros no validados |
| missing_values_estimated | Faltantes estimados en último ETL |
| duplicates_removed | Duplicados eliminados |
| last_validation | Fecha última validación |
| etl_last_run | Fecha último pipeline |
| etl_records_processed | Registros procesados |
| etl_errors | Conteo de ejecuciones fallidas |
| etl_duration_seconds | Duración último pipeline |

### GET /analytics/ml/metrics

Métricas persistidas de los modelos supervisados entrenados con Scikit-learn.

| Campo | Descripción |
|-------|-------------|
| task_type | `regression` o `classification` |
| model_name | Nombre del algoritmo entrenado |
| metric_name | Métrica evaluada (`mae`, `rmse`, `r2`, `accuracy`, `f1_macro`) |
| metric_value | Valor numérico de la métrica |
| artifact_path | Ruta del artefacto `.joblib` |
| trained_at | Fecha y hora de entrenamiento |

### POST /analytics/ml/predict/regression

Predice el promedio diario de MP2.5 a partir de variables meteorológicas.

**Body:**

```json
{
  "temp_max": 22.5,
  "temp_min": 11.3,
  "rain_sum": 0.0,
  "precipitation_sum": 0.0,
  "precip_hours": 0.0,
  "precip_prob_max": 10.0,
  "wind_speed_max": 5.2,
  "wind_gusts_max": 9.8,
  "weather_code": 0,
  "month": 7
}
```

**Respuesta:**

```json
{
  "model_name": "random_forest_regressor",
  "target": "mp25_avg",
  "predicted_value": 31.4,
  "unit": "ug/m3"
}
```
