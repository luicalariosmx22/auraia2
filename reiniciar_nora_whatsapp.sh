#!/bin/bash
# Reiniciar NORA rápidamente para aplicar cambios

echo "🔄 Reiniciando NORA para aplicar cambios del blueprint WhatsApp Web..."

# Matar procesos Flask que puedan estar corriendo
echo "🛑 Deteniendo procesos Flask existentes..."
pkill -f "dev_start.py" 2>/dev/null || true
pkill -f "python.*dev_start" 2>/dev/null || true
sleep 2

# Verificar que no hay procesos en el puerto 5000
if lsof -i:5000 2>/dev/null; then
    echo "⚠️ Puerto 5000 aún en uso, intentando liberar..."
    fuser -k 5000/tcp 2>/dev/null || true
    sleep 2
fi

# Cambiar al directorio correcto
cd /mnt/c/Users/PC/PYTHON/Auraai2

# Activar entorno virtual
echo "🐍 Activando entorno virtual..."
source venv/bin/activate

# Exportar variables de entorno
echo "🔧 Cargando variables de entorno..."
export $(grep -v '^#' .env.local | xargs) 2>/dev/null || true

# Iniciar NORA en background
echo "🚀 Iniciando NORA..."
nohup python dev_start.py > nora_restart.log 2>&1 &

# Obtener PID del proceso
NORA_PID=$!
echo "✅ NORA iniciado con PID: $NORA_PID"

# Esperar un momento para que inicie
echo "⏳ Esperando que NORA inicie completamente..."
sleep 5

# Verificar que está corriendo
if ps -p $NORA_PID > /dev/null; then
    echo "✅ NORA está corriendo correctamente"
    echo "🌐 Panel WhatsApp Web: http://localhost:5000/panel_cliente/aura/whatsapp"
    echo "📋 Logs en tiempo real: tail -f nora_restart.log"
else
    echo "❌ Error: NORA no está corriendo"
    echo "📋 Últimas líneas del log:"
    tail -10 nora_restart.log
fi

echo ""
echo "🔍 Para verificar que funciona:"
echo "1. Ir a: http://localhost:5000/panel_cliente/aura/whatsapp"
echo "2. Hacer clic en 'Flujo Automático'"
echo "3. Ver el QR generado"
echo ""
echo "🛠️ Para detener NORA: kill $NORA_PID"
