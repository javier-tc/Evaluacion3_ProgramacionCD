# Guía de Despliegue

## Requisitos

- Docker Desktop 4.x+
- Docker Compose v2
- 4 GB RAM mínimo
- Conexión a internet (API Open-Meteo)

## Despliegue

### Opción recomendada (script automatizado)

```bash
git clone <repo-url>
cd Evaluacion3_ProgramacionCD

# Linux/Mac/Git Bash
chmod +x docker/deploy.sh
./docker/deploy.sh

# Windows PowerShell
.\docker\deploy.ps1
```

Los scripts crean `.env` desde `.env.example` si no existe, levantan el stack y muestran las URLs de servicios.

### Opción manual

```bash
cp .env.example .env
docker compose up --build
```

### Re-ejecutar solo el ETL

```bash
./docker/deploy.sh --etl-only
# o
docker compose run --rm etl
```

## Variables de entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| POSTGRES_USER | Usuario PostgreSQL | airquality |
| POSTGRES_PASSWORD | Contraseña | airquality_secret |
| POSTGRES_DB | Base de datos | air_quality_santiago |
| POSTGRES_HOST | Host (postgres en Docker) | postgres |
| API_PORT | Puerto API | 8000 |
| DASHBOARD_PORT | Puerto dashboard | 8050 |
| LOG_LEVEL | Nivel de log | INFO |
| DATE_START | Inicio del análisis | 2025-06-01 |
| DATE_END | Fin del análisis | 2026-06-01 |
| ETL_STRICT_VALIDATION | Abortar carga si falla validación | false |

## Orden de arranque

1. PostgreSQL (healthcheck)
2. ETL (ejecuta y termina)
3. API (espera ETL completado)
4. Dashboard (espera API healthy)

## Troubleshooting

### ETL falla por conexión a PostgreSQL

Verificar que postgres esté healthy: `docker compose ps`

### Dashboard sin datos

Verificar API: `curl http://localhost:8000/health`

### Re-ejecutar ETL

```bash
docker compose run --rm etl
```

### Ver logs

```bash
docker compose logs etl
docker compose logs api
```

## Volúmenes

- `pg_data`: datos persistentes de PostgreSQL
- `./data`: datos raw y processed
- `./logs`: logs de aplicación
