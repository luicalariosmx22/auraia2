@echo off
REM Script para configurar actualizar_google_ads_cuentas.py como tarea programada
REM Este script configura una tarea que se ejecutará todos los lunes a las 3:00 AM

echo ===================================
echo Configurando tarea programada para Google Ads
echo Ejecución: Todos los lunes a las 3:00 AM
echo ===================================

REM Obtenemos la ruta absoluta al script Python
set SCRIPT_PATH=%~dp0actualizar_google_ads_cuentas.py
set LOG_PATH=%~dp0logs\google_ads_actualizacion_cron.log
set PYTHON_PATH=python

REM Crear directorio de logs si no existe
if not exist "%~dp0logs" mkdir "%~dp0logs"

REM Crear archivo batch que ejecutará el script
echo @echo off > "%~dp0ejecutar_actualizacion_google_ads.bat"
echo cd /d "%~dp0" >> "%~dp0ejecutar_actualizacion_google_ads.bat"
echo %PYTHON_PATH% "%~dp0actualizar_y_verificar_google_ads.py" --incluir-mcc >> "%~dp0ejecutar_actualizacion_google_ads.bat"
echo exit >> "%~dp0ejecutar_actualizacion_google_ads.bat"

echo Archivo batch creado: %~dp0ejecutar_actualizacion_google_ads.bat

REM Crear la tarea programada
schtasks /create /tn "Actualizar Google Ads Métricas" /tr "%~dp0ejecutar_actualizacion_google_ads.bat" /sc weekly /d MON /st 03:00 /ru SYSTEM /f

IF %ERRORLEVEL% EQU 0 (
    echo.
    echo ===================================
    echo Tarea programada creada exitosamente!
    echo Nombre: Actualizar Google Ads Métricas
    echo Frecuencia: Todos los lunes a las 3:00 AM
    echo ===================================
) ELSE (
    echo.
    echo ===================================
    echo Error al crear la tarea programada.
    echo Intente ejecutar este script como administrador.
    echo ===================================
)

echo.
echo Para verificar que la tarea se creó correctamente, abra el Programador de tareas:
echo taskschd.msc
echo.
echo Para ejecutar manualmente el script una vez:
echo %~dp0ejecutar_actualizacion_google_ads.bat
echo.

pause
