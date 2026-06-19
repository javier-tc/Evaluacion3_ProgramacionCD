# Manual Técnico

## Stack tecnológico

- Python 3.12
- pandas, numpy, SQLAlchemy, Pydantic, Great Expectations
- FastAPI, Dash, Plotly
- PostgreSQL 16, Docker Compose
- pytest, loguru, tenacity

## Pipeline ETL

### Extracción

1. CSV de contaminantes desde `data/raw/`
2. API Open-Meteo ERA5 para datos meteorológicos

### Transformación

- Normalización de columnas a snake_case
- Coalesce de calidad: validados > preliminares > no validados
- Parseo de fechas YYMMDD + HHMM
- Filtro temporal: 2025-06-01 a 2026-06-01
- Agregaciones diarias y mensuales
- Cálculo de correlaciones Pearson

### Validación

- **Pydantic**: tipos, valores no negativos, fechas coherentes
- **Great Expectations**: completitud y rangos

### Carga

- SQLAlchemy con transacciones y rollback
- Registro en `etl_execution_log`

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
