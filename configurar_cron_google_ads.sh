#!/bin/bash
# Script para configurar actualizar_google_ads_cuentas.py como cron job
# Este script configura un trabajo que se ejecutará todos los lunes a las 3:00 AM

echo "==================================="
echo "Configurando cron job para Google Ads"
echo "Ejecución: Todos los lunes a las 3:00 AM"
echo "==================================="

# Obtenemos la ruta absoluta al script Python y directorio de trabajo
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SCRIPT_PATH="${SCRIPT_DIR}/actualizar_google_ads_cuentas.py"
LOG_DIR="${SCRIPT_DIR}/logs"
LOG_PATH="${LOG_DIR}/google_ads_actualizacion_cron.log"

# Verificar que el script existe
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: No se encontró el script en ${SCRIPT_PATH}"
    exit 1
fi

# Crear directorio de logs si no existe
mkdir -p "$LOG_DIR"

# Obtener la ruta al intérprete de Python (podría ser python o python3)
PYTHON_PATH=$(which python3 2>/dev/null || which python)

if [ -z "$PYTHON_PATH" ]; then
    echo "Error: No se pudo encontrar el intérprete de Python"
    exit 1
fi

# Crear un script wrapper que activará el entorno virtual si existe
WRAPPER_SCRIPT="${SCRIPT_DIR}/ejecutar_actualizacion_google_ads.sh"

cat > "$WRAPPER_SCRIPT" << EOL
#!/bin/bash
cd "${SCRIPT_DIR}"
# Activar entorno virtual si existe
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi
${PYTHON_PATH} "${SCRIPT_DIR}/actualizar_y_verificar_google_ads.py" --incluir-mcc >> "${LOG_PATH}" 2>&1
EOL

# Hacer ejecutable el wrapper
chmod +x "$WRAPPER_SCRIPT"

echo "Script wrapper creado en: ${WRAPPER_SCRIPT}"

# Crear la entrada de crontab (ejecutar todos los lunes a las 3:00 AM)
CRON_JOB="0 3 * * 1 ${WRAPPER_SCRIPT}"

# Verificar si el cron job ya existe
EXISTING_CRON=$(crontab -l 2>/dev/null | grep -F "${WRAPPER_SCRIPT}")

if [ -z "$EXISTING_CRON" ]; then
    # Añadir nuevo cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    
    if [ $? -eq 0 ]; then
        echo
        echo "==================================="
        echo "Cron job creado exitosamente!"
        echo "Se ejecutará todos los lunes a las 3:00 AM"
        echo "Logs: ${LOG_PATH}"
        echo "==================================="
    else
        echo
        echo "==================================="
        echo "Error al crear el cron job."
        echo "==================================="
    fi
else
    echo
    echo "==================================="
    echo "El cron job ya existe en el crontab."
    echo "==================================="
fi

echo
echo "Para verificar los cron jobs configurados, ejecute:"
echo "crontab -l"
echo
echo "Para ejecutar manualmente el script una vez:"
echo "${WRAPPER_SCRIPT}"
echo
