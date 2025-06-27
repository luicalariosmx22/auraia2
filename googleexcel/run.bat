@echo off
title Google Ads Excel to SQL Generator
color 0A

echo.
echo =====================================================
echo   GOOGLE ADS EXCEL TO SQL GENERATOR
echo =====================================================
echo.

cd /d "c:\Users\PC\PYTHON\AuraAi2\googleexcel"

REM Verificar si existe el entorno virtual
if not exist ".venv" (
    echo [INFO] Creando entorno virtual...
    python -m venv .venv
)

REM Activar entorno virtual
call .venv\Scripts\activate.bat

REM Verificar si requirements.txt existe e instalar dependencias
if exist "requirements.txt" (
    echo [INFO] Instalando/actualizando dependencias...
    pip install -r requirements.txt --quiet
)

REM Verificar si existe el archivo .env
if not exist ".env" (
    echo [WARNING] No se encontro archivo .env
    echo [INFO] Creando archivo .env de ejemplo...
    echo OPENAI_API_KEY=tu_openai_api_key_aqui > .env
    echo.
    echo IMPORTANTE: Edita el archivo .env y agrega tu API key de OpenAI
    echo.
)

REM Ejecutar el programa principal
echo [INFO] Iniciando aplicacion...
echo.
python main.py

REM Mantener ventana abierta en caso de error
if errorlevel 1 (
    echo.
    echo [ERROR] El programa termino con errores
    pause
)

REM Desactivar entorno virtual
deactivate
