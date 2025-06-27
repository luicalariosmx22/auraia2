@echo off
REM 🚂 Railway Session para Windows
REM Uso: railway_session.bat

echo 🚂 Configurando sesion Railway...

REM Verificar si existe .env.local
if not exist ".env.local" (
    echo ❌ No se encontro .env.local
    pause
    exit /b 1
)

echo 📁 Cargando variables desde .env.local...

REM Leer variables del archivo .env.local (método simplificado para Windows)
for /f "eol=# delims== tokens=1,*" %%i in (.env.local) do (
    set "%%i=%%j"
)

echo ✅ Variables cargadas

echo.
echo 🎯 Comandos disponibles:
echo   1 - Iniciar servidor
echo   2 - Diagnosticar problemas
echo   3 - Test endpoints
echo   4 - Ver este menu
echo.

:menu
set /p choice="Selecciona una opcion (1-4): "

if "%choice%"=="1" (
    echo 🚀 Iniciando servidor...
    python dev_start.py
    goto menu
)

if "%choice%"=="2" (
    echo 🔍 Ejecutando diagnostico...
    python diagnostico_conocimiento.py
    goto menu
)

if "%choice%"=="3" (
    echo 🧪 Testing endpoints...
    python test_endpoints_completo.py
    goto menu
)

if "%choice%"=="4" (
    goto menu
)

echo Opcion invalida. Intenta de nuevo.
goto menu
