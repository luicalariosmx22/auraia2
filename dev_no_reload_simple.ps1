# Script simple para desarrollo sin auto-reload
param(
    [switch]$Verbose
)

Write-Host "DEV SERVER - Modo sin auto-reload" -ForegroundColor Cyan
Write-Host "Los cambios en tests/ NO reinician el servidor" -ForegroundColor Yellow
Write-Host ("=" * 50) -ForegroundColor DarkGray

# Cargar variables de entorno
if (Test-Path ".env.local") {
    $envCount = 0
    Get-Content .env.local | ForEach-Object {
        if ($_ -notmatch '^#' -and $_ -match '=') {
            $parts = $_ -split '=', 2
            [System.Environment]::SetEnvironmentVariable($parts[0], $parts[1], 'Process')
            $envCount++
        }
    }
    Write-Host "Cargadas $envCount variables de entorno" -ForegroundColor Green
} else {
    Write-Host "No se encontro .env.local" -ForegroundColor Red
    exit 1
}

# Configurar auto-reload desactivado
[System.Environment]::SetEnvironmentVariable('DISABLE_AUTO_RELOAD', 'true', 'Process')
Write-Host "Auto-reload desactivado" -ForegroundColor Yellow

if ($Verbose) {
    Write-Host "Configuracion:" -ForegroundColor Cyan
    Write-Host "   - Puerto: 5000" -ForegroundColor Gray
    Write-Host "   - Debug: False" -ForegroundColor Gray
    Write-Host "   - Auto-reload: Disabled" -ForegroundColor Gray
}

Write-Host "`nIniciando servidor Flask..." -ForegroundColor Cyan

# Ejecutar servidor
try {
    & python dev_start.py
} catch {
    Write-Host "Error al iniciar servidor: $_" -ForegroundColor Red
    exit 1
} finally {
    Write-Host "`nServidor detenido" -ForegroundColor Yellow
}
