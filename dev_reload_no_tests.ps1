# Script simple para auto-reload excluyendo tests/
param(
    [switch]$Verbose
)

Write-Host "🚀 DEV SERVER - Auto-reload SIN tests/" -ForegroundColor Green
Write-Host "✅ Se reinicia con cambios en archivos importantes" -ForegroundColor Cyan
Write-Host "❌ NO se reinicia con cambios en tests/" -ForegroundColor Yellow
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
    Write-Host "✅ Cargadas $envCount variables de entorno" -ForegroundColor Green
} else {
    Write-Host "❌ No se encontro .env.local" -ForegroundColor Red
    exit 1
}

if ($Verbose) {
    Write-Host "`nConfiguración:" -ForegroundColor Cyan
    Write-Host "   - Puerto: 5000" -ForegroundColor Gray
    Write-Host "   - Debug: True" -ForegroundColor Gray
    Write-Host "   - Auto-reload: Activado (excluye tests/)" -ForegroundColor Gray
    Write-Host "   - Reloader: werkzeug stat" -ForegroundColor Gray
}

Write-Host "`n🌐 Iniciando servidor Flask..." -ForegroundColor Cyan

# Ejecutar servidor
try {
    & python dev_start_exclude_tests.py
} catch {
    Write-Host "`n❌ Error al iniciar servidor: $_" -ForegroundColor Red
    exit 1
} finally {
    Write-Host "`n⏹️  Servidor detenido" -ForegroundColor Yellow
}
