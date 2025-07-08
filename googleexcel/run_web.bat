@echo off
title Google Ads SQL Generator - Web Interface
color 0A

echo.
echo ========================================================
echo   GOOGLE ADS SQL GENERATOR - WEB INTERFACE
echo ========================================================
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
    echo SUPABASE_URL=tu_supabase_url_aqui >> .env
    echo SUPABASE_KEY=tu_supabase_key_aqui >> .env
    echo.
    echo IMPORTANTE: Edita el archivo .env y agrega tus API keys
    echo.
)

REM Crear directorios necesarios
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs
if not exist "templates" mkdir templates
if not exist "static" mkdir static

echo [INFO] Iniciando servidor web en puerto 5001...
echo.
echo ===============================================
echo   SERVIDOR DISPONIBLE EN:
echo   http://localhost:5001
echo ===============================================
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

REM Ejecutar la aplicación Flask
python app.py

REM Si hay error, mantener ventana abierta
if errorlevel 1 (
    echo.
    echo [ERROR] El servidor termino con errores
    pause
)

REM Desactivar entorno virtual
deactivate
