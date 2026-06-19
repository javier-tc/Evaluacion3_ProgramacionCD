# Documentación del proyecto

Sistema de Monitoreo y Análisis de Calidad del Aire en Santiago.

## Índice

| Documento | Descripción |
|-----------|-------------|
| [arquitectura.md](arquitectura.md) | Diagrama y capas del sistema |
| [diagrama_etl.md](diagrama_etl.md) | Flujo Extract → Transform → Validate → Load |
| [diagrama_docker.md](diagrama_docker.md) | Servicios Docker Compose |
| [modelo_er.md](modelo_er.md) | Modelo entidad-relación PostgreSQL |
| [manual_tecnico.md](manual_tecnico.md) | Pipeline ETL, esquema BD, limitaciones |
| [manual_usuario.md](manual_usuario.md) | Guía del dashboard por audiencia |
| [api.md](api.md) | Endpoints REST documentados |
| [guia_despliegue.md](guia_despliegue.md) | Requisitos, variables de entorno, troubleshooting |
| [diagramas/](diagramas/) | Fuentes Mermaid para exportar PNG |
| [entregables/](entregables/) | Informe ejecutivo y presentación de evaluación |

## Notebooks ETL

- [`../etl/notebooks/01_exploracion_fuentes.ipynb`](../etl/notebooks/01_exploracion_fuentes.ipynb)
- [`../etl/notebooks/02_pipeline_etl_demo.ipynb`](../etl/notebooks/02_pipeline_etl_demo.ipynb)

## Entregables de evaluación

- `entregables/informe_evaluacion.docx` — informe ejecutivo
- `entregables/presentacion_evaluacion.pptx` — presentación de defensa
