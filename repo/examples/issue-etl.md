# Issue #1: Implementar pipeline ETL

**Labels:** `feature`, `etl`

## Descripción

Implementar el pipeline ETL completo para ingerir datos de 5 CSV de contaminantes y la API Open-Meteo.

## Tareas

- [x] Extracción de CSV con validación de archivos
- [x] Extracción de API con reintentos
- [x] Transformación y normalización
- [x] Validación Pydantic + Great Expectations
- [x] Carga a PostgreSQL con rollback

## Criterios de aceptación

- Pipeline ejecuta sin errores con `docker compose up --build`
- Datos filtrados al rango 2025-06-01 — 2026-06-01
- Reportes de validación generados en `data/processed/validation_reports/`

## Rama

`feature/etl`
