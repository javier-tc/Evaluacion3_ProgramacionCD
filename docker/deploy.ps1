#script de despliegue del stack completo (windows)
param(
    [switch]$EtlOnly
)

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path ".env")) {
    Write-Host "Creando .env desde .env.example..."
    Copy-Item ".env.example" ".env"
}

if ($EtlOnly) {
    Write-Host "Re-ejecutando ETL..."
    docker compose run --rm etl
    Write-Host "ETL completado."
    exit 0
}

Write-Host "Construyendo y levantando servicios..."
docker compose up --build -d

Write-Host "Esperando servicios (hasta 5 min)..."
$apiPort = if ($env:API_PORT) { $env:API_PORT } else { "8000" }
$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:$apiPort/health" -UseBasicParsing -TimeoutSec 3
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch {}
    Start-Sleep -Seconds 5
}

Write-Host ""
Write-Host "=== Despliegue listo ==="
$dashPort = if ($env:DASHBOARD_PORT) { $env:DASHBOARD_PORT } else { "8050" }
$pgPort = if ($env:POSTGRES_PORT) { $env:POSTGRES_PORT } else { "5432" }
Write-Host "API:       http://localhost:$apiPort"
Write-Host "Swagger:   http://localhost:$apiPort/docs"
Write-Host "Dashboard: http://localhost:$dashPort"
Write-Host "PostgreSQL: localhost:$pgPort"
