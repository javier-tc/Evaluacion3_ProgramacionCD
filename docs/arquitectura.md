# Diagrama de Arquitectura

## Vista general

```mermaid
flowchart TB
    subgraph sources [Fuentes de Datos]
        CSV_CO[CSV CO]
        CSV_MP10[CSV MP10]
        CSV_MP25[CSV MP2.5]
        CSV_NO2[CSV NO2]
        CSV_O3[CSV O3]
        API_OM[Open-Meteo ERA5]
    end

    subgraph etl_layer [Capa ETL]
        EX[Extract]
        TR[Transform]
        VAL[Validation]
        LD[Load]
    end

    subgraph storage [Almacenamiento]
        RAW[data/raw]
        PROC[data/processed]
        PG[(PostgreSQL)]
    end

    subgraph services [Servicios]
        API[FastAPI]
        DASH[Dash + Plotly]
    end

    CSV_CO --> EX
    CSV_MP10 --> EX
    CSV_MP25 --> EX
    CSV_NO2 --> EX
    CSV_O3 --> EX
    API_OM --> EX
    EX --> RAW
    RAW --> TR
    TR --> PROC
    PROC --> VAL
    VAL --> LD
    LD --> PG
    PG --> API
    API --> DASH
```

## Capas

1. **data_sources**: CSV y API meteorológica
2. **etl**: extracción, transformación, validación y carga
3. **validation**: Pydantic + Great Expectations
4. **postgresql**: almacenamiento normalizado
5. **fastapi**: exposición REST
6. **dash**: visualización interactiva (Dash + Plotly)

## Principios

- Separación por capas
- Dashboard consume solo API (no accede a DB)
- Pipeline reproducible con Docker
- Logging centralizado
