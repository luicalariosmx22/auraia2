# Script PowerShell para auto-reload inteligente
# Excluye tests/ y otros archivos innecesarios
param(
    [switch]$Verbose
)

Write-Host "🚀 DEV SERVER - Auto-reload INTELIGENTE" -ForegroundColor Green
Write-Host "✅ Auto-reload ACTIVADO para archivos importantes" -ForegroundColor Cyan
Write-Host "❌ Auto-reload DESACTIVADO para tests/ y archivos temporales" -ForegroundColor Yellow
Write-Host ("=" * 55) -ForegroundColor DarkGray

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

# Configurar auto-reload inteligente (ACTIVADO pero excluyendo tests/)
[System.Environment]::SetEnvironmentVariable('DISABLE_AUTO_RELOAD', 'false', 'Process')
[System.Environment]::SetEnvironmentVariable('SMART_RELOAD', 'true', 'Process')
Write-Host "🧠 Auto-reload INTELIGENTE activado" -ForegroundColor Green

# Mostrar archivos que SÍ causan reinicio
Write-Host "`n🔄 Archivos que SÍ reinician el servidor:" -ForegroundColor Cyan
Write-Host "   ✅ *.py (excepto en tests/)" -ForegroundColor Green
Write-Host "   ✅ *.html, *.js, *.css" -ForegroundColor Green
Write-Host "   ✅ *.json, *.yaml, *.yml" -ForegroundColor Green

# Mostrar archivos que NO causan reinicio
Write-Host "`n⏸️  Archivos que NO reinician el servidor:" -ForegroundColor Yellow
Write-Host "   ❌ tests/*.py" -ForegroundColor Red
Write-Host "   ❌ __pycache__/, logs/" -ForegroundColor Red
Write-Host "   ❌ *.pyc, *.log, *.tmp" -ForegroundColor Red

if ($Verbose) {
    Write-Host "`nConfiguración detallada:" -ForegroundColor Cyan
    Write-Host "   - Puerto: 5000" -ForegroundColor Gray
    Write-Host "   - Debug: True" -ForegroundColor Gray
    Write-Host "   - Auto-reload: Smart (excluye tests/)" -ForegroundColor Gray
    Write-Host "   - Delay entre reinicios: 1 segundo" -ForegroundColor Gray
}

Write-Host "`n🌐 Iniciando servidor Flask con auto-reload inteligente..." -ForegroundColor Cyan
Write-Host "💡 Tip: Modifica archivos .py fuera de tests/ para ver auto-reload" -ForegroundColor Magenta

# Ejecutar servidor con auto-reload inteligente
try {
    & python dev_start_smart.py
} catch {
    Write-Host "`n❌ Error al iniciar servidor: $_" -ForegroundColor Red
    Write-Host "💡 Tip: Verifica que tengas instalado 'watchdog'" -ForegroundColor Yellow
    Write-Host "   Instalar con: pip install watchdog" -ForegroundColor Gray
    exit 1
} finally {
    Write-Host "`n⏹️  Servidor detenido" -ForegroundColor Yellow
}
