# Diagrama Docker

```mermaid
flowchart LR
    subgraph compose [docker compose]
        PG[postgres:16]
        ETL[etl]
        API[api]
        DASH[dashboard]
    end

    subgraph network [air_quality_net]
        PG --- ETL
        ETL --> API
        API --> DASH
    end

    subgraph volumes [Volúmenes]
        V1[pg_data]
        V2[./data]
        V3[./logs]
    end

    PG --- V1
    ETL --- V2
    ETL --- V3
```

## Servicios

| Servicio | Imagen/Base | Puerto | Dependencia |
|----------|-------------|--------|-------------|
| postgres | postgres:16-alpine | 5432 | — |
| etl | python:3.12-slim | — | postgres healthy |
| api | python:3.12-slim | 8000 | etl completed |
| dashboard | python:3.12-slim | 8050 | api healthy |

## Red

Red bridge privada `air_quality_net`. Solo postgres, api y dashboard exponen puertos al host.
