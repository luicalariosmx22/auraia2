#!/bin/bash
# Script para iniciar NORA con entorno virtual activado
# Este script resuelve todos los problemas de dependencias

echo "🚀 Iniciando NORA con entorno virtual..."

# Navegar al directorio correcto
cd /mnt/c/Users/PC/PYTHON/Auraai2

# Activar entorno virtual
if [ -d "venv" ]; then
    echo "✅ Activando entorno virtual..."
    source venv/bin/activate
    
    # Verificar que las dependencias estén instaladas
    echo "🔍 Verificando dependencias..."
    pip list | grep -E "(socketio|requests|flask|python-dotenv)" || {
        echo "⚠️ Instalando dependencias faltantes..."
        pip install python-socketio[client] requests flask python-dotenv
    }
    
    # Iniciar NORA
    echo "🌟 Iniciando NORA..."
    python3 app.py
else
    echo "❌ No se encontró el entorno virtual. Creando..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo "✅ Entorno virtual creado. Ejecuta de nuevo este script."
fi
