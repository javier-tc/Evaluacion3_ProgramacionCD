# Estrategia Git Flow

## Ramas principales

| Rama | Propósito |
|------|-----------|
| `main` | Código en producción, estable |
| `develop` | Integración de features |

## Ramas de feature

| Rama | Contenido |
|------|-----------|
| `feature/etl` | Pipeline ETL completo |
| `feature/api` | API REST FastAPI |
| `feature/dashboard` | Dashboard Dash + Plotly |
| `feature/docker` | Docker Compose y Dockerfiles |
| `feature/tests` | Suite de pruebas pytest |

## Flujo de trabajo

1. Crear feature branch desde `develop`
2. Desarrollar y commitear cambios
3. Abrir Pull Request hacia `develop`
4. Code review y merge
5. Cuando `develop` esté estable, merge a `main` con tag de versión

## Convención de commits

```
tipo(alcance): descripción breve

feat(etl): agregar extracción de CSV CO
fix(api): corregir filtro de fechas
docs(readme): actualizar guía de despliegue
test(validation): agregar tests pydantic
```

## Issues

Usar labels: `bug`, `feature`, `documentation`, `enhancement`

Ver ejemplos en `repo/examples/`

## Pull Requests

Template en `repo/.github/PULL_REQUEST_TEMPLATE.md`
