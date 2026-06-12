# Pull Request: Feature API REST

**De:** `feature/api` → `develop`

## Resumen

Implementación de la API REST con FastAPI para exponer datos de calidad del aire y analítica.

## Cambios

- 8 endpoints REST documentados con OpenAPI
- Validación de parámetros con Pydantic
- Servicios de consulta SQLAlchemy
- Health check con verificación de PostgreSQL

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | /health | Estado del sistema |
| GET | /pollution | Mediciones |
| GET | /pollution/daily | Métricas diarias |
| GET | /pollution/monthly | Métricas mensuales |
| GET | /weather | Datos meteorológicos |
| GET | /analytics/correlation | Correlaciones |
| GET | /analytics/trends | Tendencias |
| GET | /analytics/top-pollution-days | Días críticos |

## Tests

```bash
pytest tests/test_api.py -v
```

## Reviewers

@equipo-backend
