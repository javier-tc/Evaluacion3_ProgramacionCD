# Diagrama ETL

```mermaid
flowchart LR
    subgraph extract [Extract]
        E1[Leer CSV]
        E2[API Open-Meteo]
        E3[Guardar raw]
    end

    subgraph transform [Transform]
        T1[Normalizar columnas]
        T2[Coalesce calidad]
        T3[Filtrar fechas]
        T4[Agregar diario/mensual]
        T5[Calcular correlaciones]
    end

    subgraph validate [Validate]
        V1[Pydantic schemas]
        V2[Great Expectations]
        V3[Reporte JSON]
    end

    subgraph load [Load]
        L1[Transaccion SQL]
        L2[Bulk insert]
        L3[Log ETL]
    end

    E1 --> T1
    E2 --> T1
    E3 --> T1
    T1 --> T2 --> T3 --> T4 --> T5
    T5 --> V1 --> V2 --> V3
    V3 --> L1 --> L2 --> L3
```

## Etapas

| Etapa | Módulo | Salida |
|-------|--------|--------|
| Extract | `etl/extract/` | `data/raw/{timestamp}/` |
| Transform | `etl/transform/` | `data/processed/*.parquet` |
| Validate | `etl/validation/` | `validation_reports/*.json` |
| Load | `etl/load/` | PostgreSQL |
