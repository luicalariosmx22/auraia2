# Script para ejecutar tests ultra eficientes
# Optimizado para PowerShell Extension en VS Code
# Uso: .\run_test.ps1 -TestFile "test_nombre.py" [-Verbose]

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$TestFile,
    [switch]$ListTests,
    [switch]$Verbose
)

function Write-ColorMessage {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Get-AvailableTests {
    if (-not (Test-Path "tests")) {
        Write-ColorMessage "❌ Carpeta tests/ no encontrada" "Red"
        return @()
    }
    
    return Get-ChildItem "tests\*.py" | Where-Object { $_.Name -like "test_*" }
}

function Load-EnvVariables {
    if (Test-Path ".env.local") {
        Get-Content .env.local | ForEach-Object {
            if ($_ -notmatch '^#' -and $_ -match '=') {
                $parts = $_ -split '=', 2
                [System.Environment]::SetEnvironmentVariable($parts[0], $parts[1], 'Process')
            }
        }
        Write-ColorMessage "✅ Variables de entorno cargadas" "Green"
    }
}

# Header
Write-ColorMessage "🧪 TEST RUNNER - Ultra Eficiente" "Cyan"
Write-ColorMessage "⚡ Sin cargar Flask ni blueprints" "Yellow"
Write-ColorMessage ("=" * 50) "DarkGray"

# Cargar variables de entorno
Load-EnvVariables

# Listar tests disponibles si se solicita
if ($ListTests) {
    Write-ColorMessage "`n📋 Tests disponibles:" "Cyan"
    $tests = Get-AvailableTests
    foreach ($test in $tests) {
        Write-ColorMessage "   • $($test.Name)" "White"
    }
    Write-ColorMessage "`n💡 Uso: .\run_test.ps1 -TestFile `"$($tests[0].Name)`"" "Yellow"
    exit 0
}

# Seleccionar archivo de test
if (-not $TestFile) {
    $tests = Get-AvailableTests
    if ($tests.Count -eq 0) {
        Write-ColorMessage "❌ No se encontraron tests" "Red"
        exit 1
    }
    
    Write-ColorMessage "`n📋 Tests disponibles:" "Cyan"
    for ($i = 0; $i -lt $tests.Count; $i++) {
        Write-ColorMessage "   $($i + 1). $($tests[$i].Name)" "White"
    }
    
    $selection = Read-Host "`n🔢 Selecciona un test (número)"
    
    try {
        $index = [int]$selection - 1
        if ($index -ge 0 -and $index -lt $tests.Count) {
            $TestFile = $tests[$index].Name
        } else {
            Write-ColorMessage "❌ Selección inválida" "Red"
            exit 1
        }
    } catch {
        Write-ColorMessage "❌ Entrada inválida" "Red"
        exit 1
    }
}

# Verificar que existe el archivo
$testPath = "tests\$TestFile"
if (-not (Test-Path $testPath)) {
    Write-ColorMessage "❌ No se encontró: $testPath" "Red"
    exit 1
}

# Ejecutar test
Write-ColorMessage "`n🚀 Ejecutando: $TestFile" "Cyan"
Write-ColorMessage "📁 Ubicación: $testPath" "Gray"

if ($Verbose) {
    Write-ColorMessage "🔧 Modo verbose activado" "Magenta"
}

Write-ColorMessage "`n" + ("=" * 50) "DarkGray"

$startTime = Get-Date

try {
    & python $testPath
    $exitCode = $LASTEXITCODE
    
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-ColorMessage "`n" + ("=" * 50) "DarkGray"
    
    if ($exitCode -eq 0) {
        Write-ColorMessage "✅ Test completado exitosamente" "Green"
    } else {
        Write-ColorMessage "❌ Test falló (código: $exitCode)" "Red"
    }
    
    Write-ColorMessage "⏱️  Tiempo: $($duration.TotalSeconds.ToString('F2')) segundos" "Cyan"
    
} catch {
    Write-ColorMessage "❌ Error ejecutando test: $_" "Red"
    exit 1
}

Write-ColorMessage "`n💡 Para listar tests: .\run_test.ps1 -ListTests" "Yellow"
