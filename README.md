# Sistema de Monitoreo y Análisis de Calidad del Aire en Santiago

Solución completa de Ciencia de Datos que integra datos ambientales y meteorológicos mediante un pipeline ETL automatizado, modelos supervisados con Scikit-learn, almacenamiento en PostgreSQL, API REST y dashboards interactivos Dash + Plotly.

## Integrantes

| GitHub | Aportes principales |
|--------|---------------------|
| [@javier-tc](https://github.com/javier-tc) | Desarrollo del pipeline ETL, API REST, dashboard, containerización Docker y documentación técnica |
| [@roz-ctrl](https://github.com/roz-ctrl) | Limpieza y reorganización del repositorio, documentación del equipo y flujo de colaboración Git |

## Inicio rápido

```bash
cp .env.example .env
docker compose up --build
```

Servicios disponibles:

| Servicio | URL |
|----------|-----|
| API REST | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| Dashboard | http://localhost:8050 |
| PostgreSQL | localhost:5432 |

## Arquitectura

```
data_sources → etl → validation → postgresql → fastapi → dash
                              ↘ models sklearn ↗
```

## Estructura del proyecto

```
├── api/              # API REST FastAPI
├── dashboards/       # Dashboard Dash + Plotly
├── data/             # Datos raw, processed y external
├── docker/           # Dockerfiles
├── docs/             # Documentación completa
├── etl/              # Pipeline ETL
├── models/           # Entrenamiento, evaluación y registro ML
├── scripts/          # Scripts de migración y ETL
├── tests/            # Pruebas automatizadas
└── repo/             # Ejemplos Git Flow
```

## Período de análisis

01-06-2025 al 01-06-2026

## Contaminantes

CO, MP10, MP2.5, NO2, O3

## Notebooks ETL

```bash
jupyter notebook etl/notebooks/
```

- `01_exploracion_fuentes.ipynb` — perfilado de CSV y API Open-Meteo
- `02_pipeline_etl_demo.ipynb` — demo paso a paso del pipeline E-T-V-L

## Despliegue automatizado

```bash
# Linux/Mac/Git Bash
./docker/deploy.sh

# Windows PowerShell
.\docker\deploy.ps1

# Solo re-ejecutar ETL
./docker/deploy.sh --etl-only
```

## Ejecutar tests

```bash
pip install -r requirements.txt
pytest
```

## Entrenar modelos

Después de ejecutar el ETL y tener PostgreSQL poblado:

```bash
python scripts/run_training.py
```

El entrenamiento genera artefactos en `data/processed/models/`, guarda métricas en PostgreSQL y habilita los endpoints `/analytics/ml/metrics` y `/analytics/ml/predict/regression`.

Con Docker Compose el flujo queda automatizado:

```bash
docker compose up --build
```

Orden de servicios: PostgreSQL → ETL → entrenamiento ML → API → dashboard.

## Documentación

Ver carpeta [`docs/`](docs/) para manuales técnicos, de usuario, despliegue y diagramas.

## Entregables de evaluación

| Archivo | Descripción |
|---------|-------------|
| [`docs/entregables/informe_evaluacion.docx`](docs/entregables/informe_evaluacion.docx) | Informe ejecutivo |
| [`docs/entregables/presentacion_evaluacion.pptx`](docs/entregables/presentacion_evaluacion.pptx) | Presentación de defensa |

Regenerar con: `python scripts/generate_informe.py` y `python scripts/generate_presentacion.py`
