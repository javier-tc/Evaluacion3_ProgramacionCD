#!/usr/bin/env bash
#script de despliegue del stack completo
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ETL_ONLY=false
for arg in "$@"; do
  case "$arg" in
    --etl-only) ETL_ONLY=true ;;
    -h|--help)
      echo "Uso: ./docker/deploy.sh [--etl-only]"
      echo "  --etl-only  re-ejecuta solo el contenedor ETL"
      exit 0
      ;;
  esac
done

if [ ! -f .env ]; then
  echo "Creando .env desde .env.example..."
  cp .env.example .env
fi

if [ "$ETL_ONLY" = true ]; then
  echo "Re-ejecutando ETL..."
  docker compose run --rm etl
  echo "ETL completado."
  exit 0
fi

echo "Construyendo y levantando servicios..."
docker compose up --build -d

echo "Esperando servicios..."
for i in $(seq 1 60); do
  if docker compose ps --format json 2>/dev/null | grep -q '"Health":"healthy"'; then
  if curl -sf http://localhost:${API_PORT:-8000}/health >/dev/null 2>&1; then
    break
  fi
  fi
  sleep 5
done

echo ""
echo "=== Despliegue listo ==="
echo "API:       http://localhost:${API_PORT:-8000}"
echo "Swagger:   http://localhost:${API_PORT:-8000}/docs"
echo "Dashboard: http://localhost:${DASHBOARD_PORT:-8050}"
echo "PostgreSQL: localhost:${POSTGRES_PORT:-5432}"
