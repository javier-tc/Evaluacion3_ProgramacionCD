# Evidencia de colaboración Git

Documentación del flujo colaborativo del equipo.

## Repositorio

- **URL:** https://github.com/javier-tc/Evaluacion3_ProgramacionCD
- **Integrantes:** [@javier-tc](https://github.com/javier-tc), [@roz-ctrl](https://github.com/roz-ctrl)

## Estrategia

Ver [GITFLOW.md](GITFLOW.md): ramas `main` (producción) y `develop` (integración), features con Pull Requests.

## Pull Requests

| PR | Rama | Descripción | Estado |
|----|------|-------------|--------|
| [#1](https://github.com/javier-tc/Evaluacion3_ProgramacionCD/pull/1) | `pedro-ponce` → `main` | Limpieza CSVs + integrantes | Abierto |
| Local | `feature/etl-notebooks` → `develop` | Notebooks ETL exploratorios | Mergeado (698ba83) |
| Local | `feature/deploy-scripts` → `develop` | Scripts de despliegue Docker | Mergeado (f188063) |
| Local | `feature/validation-tests` → `develop` | Validación estricta + tests | Mergeado (ca7eba8) |
| Local | `feature/docs-github` → `develop` | Plantillas GitHub y docs | Mergeado (5688206) |
| Local | `feature/deliverables-evaluacion` → `develop` | Informe DOCX y PPTX | Mergeado (0c93234) |
| Local | `develop` → `main` | Integración evaluación 3 | Mergeado |

## Ramas feature

```
feature/etl-notebooks
feature/deploy-scripts
feature/validation-tests
feature/docs-github
feature/deliverables-evaluacion
develop
main
```

## Issues

| Issue | Título | Labels | Evidencia |
|-------|--------|--------|-----------|
| #2 | Agregar notebooks ETL para evaluación | `enhancement`, `etl` | [repo/examples/issue-notebooks-etl.md](examples/issue-notebooks-etl.md) |
| #3 | Script automatizado de despliegue Docker | `devops`, `docker` | [repo/examples/issue-deploy-docker.md](examples/issue-deploy-docker.md) |
| #1 | Pipeline ETL inicial | `etl` | [repo/examples/issue-etl.md](examples/issue-etl.md) |

## Convención de commits

```
tipo(alcance): descripción breve
```

Ejemplos: `feat(etl): agregar notebooks exploratorios`, `docs(readme): actualizar guía de despliegue`
