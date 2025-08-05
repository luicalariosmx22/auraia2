#!/bin/bash
# Archivo: start.sh - Simple start script para Railway

echo "🚀 Iniciando aplicación Flask..."

# Instalar gunicorn si no existe
if ! command -v gunicorn &> /dev/null; then
    echo "📦 Instalando gunicorn..."
    pip install gunicorn
fi

# Ejecutar la aplicación
echo "🌟 Iniciando servidor con gunicorn..."
echo "🔍 PORT variable: $PORT"
echo "🔍 All env vars:"
env | grep PORT || echo "No PORT variables found"

# Usar puerto 8080 si PORT no está definido o está vacío
FINAL_PORT=${PORT:-8080}
echo "🚀 Using final port: $FINAL_PORT"

exec gunicorn run:app --bind 0.0.0.0:$FINAL_PORT --workers 2 --timeout 120 --log-level info
