# Issue #3 — Script automatizado de despliegue Docker

**Labels:** `devops`, `docker`  
**Estado:** Cerrado  
**Asignado:** @javier-tc

## Descripción

Faltaban scripts de despliegue en `/docker/` según la estructura recomendada de la evaluación.

## Solución

- `docker/deploy.sh` — Linux/Mac/Git Bash
- `docker/deploy.ps1` — Windows PowerShell
- Opción `--etl-only` / `-EtlOnly` para re-ejecutar solo el ETL

## PR relacionado

`feature/deploy-scripts` → `develop`
