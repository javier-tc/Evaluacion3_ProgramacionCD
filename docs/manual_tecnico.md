# Manual Técnico

## Stack tecnológico

- Python 3.12
- pandas, numpy, SQLAlchemy, Pydantic, Great Expectations
- scikit-learn, joblib
- FastAPI, Dash, Plotly
- PostgreSQL 16, Docker Compose
- pytest, loguru, tenacity

## Pipeline ETL

### Extracción

1. CSV de contaminantes desde `data/raw/`
2. API Open-Meteo ERA5 para datos meteorológicos

### Transformación

- Normalización de columnas a snake_case
- Coalesce vectorizado de calidad: validados > preliminares > no validados
- Parseo de fechas YYMMDD + HHMM
- Filtro temporal: 2025-06-01 a 2026-06-01
- Agregaciones diarias y mensuales
- Reshape con `pivot_table` y `melt` para correlaciones y dataset ML
- Join con umbrales de referencia extraídos desde PostgreSQL
- Cálculo de correlaciones Pearson

### Decisiones de limpieza

| Regla | Justificación | Evidencia |
|-------|---------------|-----------|
| Coalesce de valores | Prioriza mediciones validadas y conserva preliminares/no validadas cuando aportan cobertura | `quality_status` indica la fuente usada |
| Eliminación de nulos en `value` | Evita métricas y modelos con observaciones sin concentración | Reporte de validación y metadata `missing_values_estimated` |
| Filtro de valores negativos | Las concentraciones negativas no son válidas para el dominio físico | Regla aplicada antes de agregaciones |
| Filtro temporal | Mantiene el período oficial del proyecto | `DATE_START` y `DATE_END` |
| Deduplicación por fecha-contaminante | Evita doble conteo en agregaciones | `duplicates_removed` en estado de calidad |

Los reportes JSON de validación se generan en `data/processed/validation_reports/`.

### Validación

- **Pydantic**: tipos, valores no negativos, fechas coherentes
- **Great Expectations**: completitud y rangos

### Carga

- SQLAlchemy con transacciones y rollback
- Inserción por bloques con `CHUNK_SIZE` para grandes volúmenes
- Registro en `etl_execution_log`

## Modelos supervisados

El módulo `models/` entrena modelos Scikit-learn desde datos consolidados en PostgreSQL.

### Regresión

- Objetivo: predecir promedio diario de MP2.5 (`mp25_avg`)
- Algoritmos: `LinearRegression`, `RandomForestRegressor`, `GradientBoostingRegressor`
- Métricas: MAE, RMSE, R² y validación cruzada por MAE

### Clasificación

- Objetivo: clasificar nivel diario de MP2.5 (`normal`, `moderado`, `alerta`)
- Algoritmos: `LogisticRegression`, `RandomForestClassifier`, `SVC`
- Métricas: accuracy, F1 macro, matriz de confusión y validación cruzada

### Persistencia

- Artefactos `.joblib`: `data/processed/models/`
- Métricas: tabla `model_metrics`
- Entrenamiento manual: `python scripts/run_training.py`

## Esquema de base de datos

| Tabla | Descripción |
|-------|-------------|
| pollution_measurements | Mediciones de contaminantes |
| weather_measurements | Datos meteorológicos diarios |
| daily_metrics | Agregados diarios |
| monthly_metrics | Agregados mensuales |
| correlation_matrix | Correlaciones calculadas |
| etl_execution_log | Log de ejecuciones ETL |

## Limitaciones conocidas

- Los CSV contienen datos **diarios** (hora 00:00), no series horarias reales
- El análisis horario refleja esta limitación
- Los archivos CSV originales provienen de estación O'Higgins pero se referencian como Santiago en el sistema

## Unidades

| Contaminante | Unidad |
|-------------|--------|
| CO | ppm |
| MP10, MP2.5 | µg/m³ |
| NO2, O3 | ppb |

## Logging

Logs estructurados en `logs/etl_YYYY-MM-DD.log` con rotación de 10 MB.

## Notebooks exploratorios

Ubicación: `etl/notebooks/`

| Notebook | Propósito |
|----------|-----------|
| `01_exploracion_fuentes.ipynb` | Perfilado de CSV y muestra Open-Meteo |
| `02_pipeline_etl_demo.ipynb` | Demo E-T-V-L reutilizando módulos de producción |

Variable `NOTEBOOK_LOAD_DB=true` habilita la carga a PostgreSQL en el notebook 02.
