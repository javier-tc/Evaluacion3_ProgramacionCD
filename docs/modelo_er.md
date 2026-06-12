# Modelo Entidad-Relación

```mermaid
erDiagram
    pollution_measurements {
        int id PK
        timestamp measured_at
        varchar pollutant
        float value
        varchar unit
        varchar quality_status
        varchar station_name
    }

    weather_measurements {
        int id PK
        date date UK
        float temp_max
        float temp_min
        float rain_sum
        float precipitation_sum
        float precip_hours
        float precip_prob_max
        float wind_speed_max
        float wind_gusts_max
        int weather_code
    }

    daily_metrics {
        int id PK
        date date
        varchar pollutant
        float avg_value
        float max_value
        varchar unit
    }

    monthly_metrics {
        int id PK
        varchar year_month
        varchar pollutant
        float avg_value
        float max_value
        varchar unit
    }

    correlation_matrix {
        int id PK
        varchar var_x
        varchar var_y
        float correlation
        varchar method
        timestamp computed_at
    }

    etl_execution_log {
        int id PK
        varchar run_id
        varchar stage
        varchar status
        int records_count
        text error_message
        float duration_seconds
        timestamp started_at
        timestamp finished_at
    }

    pollution_measurements ||--o{ daily_metrics : "agrega a"
    pollution_measurements ||--o{ monthly_metrics : "agrega a"
    weather_measurements ||--o{ correlation_matrix : "correlaciona con"
    pollution_measurements ||--o{ correlation_matrix : "correlaciona con"
```

## Relaciones lógicas

- `daily_metrics` y `monthly_metrics` se derivan de `pollution_measurements`
- `correlation_matrix` cruza contaminantes con variables meteorológicas
- `etl_execution_log` registra cada ejecución del pipeline
