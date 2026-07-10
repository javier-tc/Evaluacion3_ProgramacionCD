# Informe Técnico Ejecutivo

## Executive Summary

El proyecto aborda el monitoreo y análisis de calidad del aire en Santiago mediante una solución completa de ciencia de datos. Integra mediciones de contaminantes atmosféricos con variables meteorológicas para responder cómo el clima se relaciona con la concentración diaria de CO, MP10, MP2.5, NO2 y O3.

La solución entrega valor en tres niveles. Primero, automatiza la gestión de datos con un pipeline ETL reproducible. Segundo, expone resultados mediante una API REST documentada. Tercero, facilita la toma de decisiones con dashboards interactivos y modelos supervisados que predicen MP2.5 y clasifican niveles de alerta.

El resultado esperado es una plataforma demostrable end-to-end: extracción desde CSV, API REST externa y BBDD; transformación y validación; carga a PostgreSQL; entrenamiento ML; consulta vía FastAPI; y visualización en Dash.

## Metodología Técnica

### Fuentes de datos

| Fuente | Uso |
|--------|-----|
| CSV locales | Mediciones de CO, MP10, MP2.5, NO2 y O3 |
| Open-Meteo ERA5 | Temperatura, lluvia, precipitación, viento y código meteorológico |
| PostgreSQL | Umbrales de referencia y almacenamiento analítico |

### Pipeline ETL

El ETL se organiza en extracción, transformación, validación y carga. La transformación aplica filtros temporales, limpieza de valores inválidos, coalesce vectorizado de mediciones por calidad, agregaciones diarias/mensuales, reshape con `pivot_table` y `melt`, correlaciones Pearson y enriquecimiento con umbrales de referencia desde BBDD.

La validación usa Pydantic para tipos y reglas de dominio, y Great Expectations para completitud y rangos. La carga se ejecuta con SQLAlchemy en transacciones, rollback ante errores y bloques de inserción configurados por `CHUNK_SIZE`.

### Modelos ML

Se implementan dos problemas supervisados con Scikit-learn:

| Tarea | Objetivo | Algoritmos | Métricas |
|-------|----------|------------|----------|
| Regresión | Predecir promedio diario de MP2.5 | LinearRegression, RandomForestRegressor, GradientBoostingRegressor | MAE, RMSE, R² |
| Clasificación | Clasificar nivel de alerta MP2.5 | LogisticRegression, RandomForestClassifier, SVC | Accuracy, F1 macro, matriz de confusión |

Los modelos usan variables meteorológicas y estacionalidad mensual codificada con seno/coseno. Los artefactos se guardan en `data/processed/models/` y las métricas se persisten en `model_metrics`.

## Resultados y KPIs de Negocio

Los dashboards permiten observar:

| KPI | Interpretación |
|-----|----------------|
| Promedio anual por contaminante | Magnitud del problema y comparación por unidad física |
| Top días de contaminación | Priorización de eventos críticos |
| Correlaciones clima-contaminación | Evidencia técnica para hipótesis ambientales |
| Calidad de datos | Confianza del pipeline y trazabilidad operacional |
| Métricas ML | Capacidad predictiva para apoyar alertas preventivas |

Los resultados deben interpretarse considerando una limitación importante: los CSV disponibles contienen mediciones diarias representadas a hora 00:00, por lo que el análisis horario no debe tratarse como serie intra-día real.

## Despliegue y Operación

El despliegue se realiza con Docker Compose:

```bash
cp .env.example .env
docker compose up --build
```

Orden de ejecución:

1. PostgreSQL crea tablas y queda healthy.
2. ETL carga datos raw, processed y PostgreSQL.
3. Entrenamiento ML genera artefactos y métricas.
4. API FastAPI expone endpoints.
5. Dashboard Dash consume la API.

La integración continua se define en `.github/workflows/ci.yml` y ejecuta `pytest` con cobertura de `etl`, `api` y `models`.

## Evidencias de Funcionalidad

| Evidencia | Ubicación |
|-----------|-----------|
| API interactiva | `http://localhost:8000/docs` |
| Dashboard | `http://localhost:8050` |
| Reportes de validación | `data/processed/validation_reports/` |
| Métricas ML | `GET /analytics/ml/metrics` |
| Predicción MP2.5 | `POST /analytics/ml/predict/regression` |
| Cobertura de tests | `reports/coverage/` |

## Anexos Técnicos

- Arquitectura: `docs/arquitectura.md`
- Modelo entidad-relación: `docs/modelo_er.md`
- Diagrama ETL: `docs/diagrama_etl.md`
- Documentación API: `docs/api.md`
- Guía de despliegue: `docs/guia_despliegue.md`
- Manual de usuario: `docs/manual_usuario.md`

