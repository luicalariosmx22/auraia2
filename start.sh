#!/bin/bash
# Archivo: start.sh (raíz del proyecto)
# � Script de arranque para WhatsApp Web Backend (Node.js) en Railway

echo "--- INICIO DEL SCRIPT start.sh ---"
echo "PORT (asignado por Railway): ${PORT}"
echo "NODE_ENV: ${NODE_ENV}"
echo "Date: $(date)"
echo "---------------------------------------------------"

# Verificar que Node.js esté disponible
echo "🔍 Verificando Node.js..."
if command -v node &> /dev/null; then
    echo "✅ Node.js version: $(node --version)"
else
    echo "❌ Node.js no encontrado!"
    exit 1
fi

# Verificar que NPM esté disponible
echo "🔍 Verificando NPM..."
if command -v npm &> /dev/null; then
    echo "✅ NPM version: $(npm --version)"
else
    echo "❌ NPM no encontrado!"
    exit 1
fi

# Verificar que Chrome esté disponible
echo "🔍 Verificando Chrome..."
if command -v google-chrome-stable &> /dev/null; then
    echo "✅ Chrome version: $(google-chrome-stable --version)"
else
    echo "⚠️  Chrome no encontrado en PATH"
fi

# Verificar que server.js existe
echo "🔍 Verificando server.js..."
if [ -f "server.js" ]; then
    echo "✅ server.js encontrado"
    echo "Tamaño: $(stat -c%s server.js 2>/dev/null || echo "unknown") bytes"
else
    echo "❌ server.js no encontrado!"
    exit 1
fi

# Verificar dependencias
echo "🔍 Verificando node_modules..."
if [ -d "node_modules" ]; then
    echo "✅ node_modules encontrado"
else
    echo "⚠️  node_modules no encontrado, instalando dependencias..."
    npm install
fi

# Establecer puerto por defecto si no está definido
if [ -z "$PORT" ]; then
    echo "⚠️  PORT no definido, usando 3000"
    export PORT=3000
fi

# Iniciar el servidor
echo "🌟 Iniciando WhatsApp Web Backend Server..."
echo "Puerto: $PORT"
echo "Comando: node server.js"
echo "---------------------------------------------------"

# Ejecutar el servidor Node.js
exec node server.js
