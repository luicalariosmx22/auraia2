#!/bin/bash
# Script para reiniciar NORA con entorno virtual activado

echo "🔄 REINICIANDO NORA CON ENTORNO VIRTUAL"
echo "========================================="

# Detener cualquier proceso de NORA existente
echo "🛑 Deteniendo procesos existentes..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true
sleep 2

# Ir al directorio correcto
cd /mnt/c/Users/PC/PYTHON/Auraai2

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Verificar que el entorno está activo
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Entorno virtual activado: $VIRTUAL_ENV"
else
    echo "❌ Error: Entorno virtual no se activó"
    exit 1
fi

# Verificar dependencias críticas
echo "🔍 Verificando dependencias..."
python -c "import socketio; print('✅ python-socketio disponible')" || {
    echo "❌ Instalando python-socketio..."
    pip install python-socketio[client]
}

python -c "import requests; print('✅ requests disponible')" || {
    echo "❌ Instalando requests..."
    pip install requests
}

# Iniciar NORA
echo "🚀 Iniciando NORA..."
echo "📡 Puedes acceder a: http://localhost:5000"
echo "🔗 Panel WhatsApp: http://localhost:5000/panel_cliente/aura/whatsapp"
echo ""
echo "Presiona Ctrl+C para detener"

# Ejecutar NORA con logs
python app.py
