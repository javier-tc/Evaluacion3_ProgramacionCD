# Sistema de Monitoreo y Análisis de Calidad del Aire en Santiago

Solución completa de Ciencia de Datos que integra datos ambientales y meteorológicos mediante un pipeline ETL automatizado, almacenamiento en PostgreSQL, API REST y dashboards interactivos Dash + Plotly.

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
```

## Estructura del proyecto

```
├── api/              # API REST FastAPI
├── dashboards/       # Dashboard Dash + Plotly
├── data/             # Datos raw, processed y external
├── docker/           # Dockerfiles
├── docs/             # Documentación completa
├── etl/              # Pipeline ETL
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

## Documentación

Ver carpeta [`docs/`](docs/) para manuales técnicos, de usuario, despliegue y diagramas.
