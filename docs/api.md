# Documentación API

Base URL: `http://localhost:8000`

Documentación interactiva: `/docs` (Swagger) y `/redoc`

## Endpoints

### GET /health

Estado del sistema y conectividad a PostgreSQL.

**Respuesta:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-06-11T12:00:00"
}
```

### GET /pollution

Mediciones de contaminantes.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| pollutant | string | CO, MP10, MP25, NO2, O3 |
| start_date | date | Fecha inicio |
| end_date | date | Fecha fin |
| limit | int | Máximo registros (default 1000) |

### GET /pollution/daily

Métricas diarias agregadas. Mismos filtros de fecha y contaminante.

### GET /pollution/monthly

Métricas mensuales. Filtro opcional por contaminante.

### GET /weather

Datos meteorológicos diarios. Filtros: `start_date`, `end_date`.

### GET /analytics/correlation

Matriz de correlación entre contaminantes y variables meteorológicas.

### GET /analytics/trends

Tendencias lineales por contaminante (pendiente, R², dirección).

### GET /analytics/top-pollution-days

| Parámetro | Tipo | Default |
|-----------|------|---------|
| pollutant | string | todos |
| top_n | int | 10 |

### GET /analytics/annual-averages

Promedios anuales por contaminante.

### GET /analytics/etl-status

Estado de la última ejecución del pipeline ETL.
