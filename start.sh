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
exec gunicorn run:app --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 --log-level info
