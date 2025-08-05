#!/bin/bash
# Archivo: start.sh (raíz del proyecto)
# 🐍 Script de arranque para Flask Application (Python) en Railway

echo "--- INICIO DEL SCRIPT start.sh (PYTHON/FLASK) ---"
echo "PORT (asignado por Railway): ${PORT}"
echo "PYTHON_VERSION: $(python --version 2>&1)"
echo "Date: $(date)"
echo "---------------------------------------------------"

# Verificar que Python esté disponible
echo "🔍 Verificando Python..."
if command -v python &> /dev/null; then
    echo "✅ Python version: $(python --version)"
elif command -v python3 &> /dev/null; then
    echo "✅ Python3 version: $(python3 --version)"
    alias python=python3
else
    echo "❌ Python no encontrado!"
    exit 1
fi

# Verificar que run.py existe
echo "🔍 Verificando run.py..."
if [ -f "run.py" ]; then
    echo "✅ run.py encontrado"
    echo "Tamaño: $(stat -c%s run.py 2>/dev/null || echo "unknown") bytes"
else
    echo "❌ run.py no encontrado!"
    exit 1
fi

# Verificar requirements.txt
echo "🔍 Verificando requirements.txt..."
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt encontrado"
else
    echo "❌ requirements.txt no encontrado!"
    exit 1
fi

# Establecer puerto por defecto si no está definido
if [ -z "$PORT" ]; then
    echo "⚠️  PORT no definido, usando 5000"
    export PORT=5000
fi

# Verificar que gunicorn esté instalado
echo "🔍 Verificando gunicorn..."
if command -v gunicorn &> /dev/null; then
    echo "✅ Gunicorn encontrado: $(gunicorn --version)"
else
    echo "⚠️  Gunicorn no encontrado, instalando..."
    pip install gunicorn
fi

# Iniciar el servidor Flask con Gunicorn
echo "🌟 Iniciando Flask Application con Gunicorn..."
echo "Puerto: $PORT"
echo "Comando: gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120"
echo "---------------------------------------------------"

# Ejecutar el servidor Flask con Gunicorn
exec gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-level info
