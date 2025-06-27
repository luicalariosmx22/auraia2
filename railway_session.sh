#!/bin/bash
# 🚀 Railway Session Setup
# Archivo para configurar automáticamente las variables de entorno de Railway
# Uso: source railway_session.sh

echo "🚂 Configurando sesión Railway..."

# Cargar variables de entorno de Railway
if [ -f ".env.local" ]; then
    echo "📁 Cargando variables desde .env.local"
    export $(grep -v '^#' .env.local | xargs)
    echo "✅ Variables de entorno cargadas"
else
    echo "❌ No se encontró .env.local"
    exit 1
fi

# Función para iniciar el servidor
start_server() {
    echo "🚀 Iniciando servidor..."
    python dev_start.py
}

# Función para ejecutar tests
test_endpoints() {
    echo "🧪 Ejecutando tests de endpoints..."
    python test_endpoints_completo.py
}

# Función para ver logs
show_logs() {
    echo "📋 Mostrando logs recientes..."
    tail -f logs/*.log 2>/dev/null || echo "No hay logs disponibles"
}

echo "🎯 Comandos disponibles:"
echo "  start_server     - Iniciar el servidor Flask"
echo "  test_endpoints   - Probar endpoints de conocimiento"
echo "  show_logs        - Ver logs en tiempo real"
echo ""
echo "🔥 Para usar: source railway_session.sh && start_server"
