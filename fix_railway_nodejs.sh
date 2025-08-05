#!/bin/bash

# Script para forzar Railway a usar Node.js en lugar de Python
echo "=== CONFIGURACIÓN DEFINITIVA PARA RAILWAY NODE.JS ==="
echo "Fecha: $(date)"
echo ""

# Verificar que estamos en el directorio correcto
PROJECT_DIR="/mnt/c/Users/PC/PYTHON/Auraai2"
cd "$PROJECT_DIR"

echo "📁 Directorio del proyecto: $PROJECT_DIR"
echo ""

# Activar entorno virtual si es necesario
if [ -f ".venv/bin/activate" ]; then
    echo "🐍 Activando entorno virtual..."
    source .venv/bin/activate
    echo "✅ Entorno virtual activado"
else
    echo "⚠️  Entorno virtual no encontrado, continuando..."
fi

echo ""
echo "🔧 CONFIGURANDO RAILWAY PARA NODE.JS:"
echo "-----------------------------------"

# Crear archivo .nvmrc para especificar versión de Node.js
echo "18" > .nvmrc
echo "✅ Archivo .nvmrc creado (Node.js 18)"

# Crear archivo railway.json para configuración específica
cat > railway.json << 'EOF'
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "npm start"
  }
}
EOF
echo "✅ Archivo railway.json creado"

# Verificar que package.json esté configurado correctamente
if [ -f "package.json" ]; then
    echo "✅ package.json existe"
    if grep -q '"start"' package.json; then
        echo "✅ Script 'start' encontrado en package.json"
    else
        echo "❌ Script 'start' no encontrado en package.json"
    fi
else
    echo "❌ package.json no encontrado"
fi

# Verificar que Dockerfile esté configurado correctamente
if [ -f "Dockerfile" ]; then
    echo "✅ Dockerfile existe"
    if grep -q "CMD.*npm.*start" Dockerfile; then
        echo "✅ CMD npm start encontrado en Dockerfile"
    else
        echo "❌ CMD npm start no encontrado en Dockerfile"
    fi
else
    echo "❌ Dockerfile no encontrado"
fi

# Verificar que no hay Procfile que interfiera
if [ -f "Procfile" ]; then
    echo "⚠️  Procfile encontrado - puede interferir con Node.js"
    echo "🗑️  Eliminando Procfile..."
    rm Procfile
    echo "✅ Procfile eliminado"
else
    echo "✅ No hay Procfile que interfiera"
fi

echo ""
echo "📝 ACTUALIZANDO DOCKERFILE PARA RAILWAY:"
echo "-----------------------------------"

# Verificar que el Dockerfile use npm start
if ! grep -q "CMD.*npm.*start" Dockerfile; then
    echo "🔧 Actualizando Dockerfile para usar npm start..."
    
    # Backup del Dockerfile actual
    cp Dockerfile Dockerfile.backup
    
    # Actualizar el CMD en el Dockerfile
    sed -i 's/CMD \[.*\]/CMD ["npm", "start"]/' Dockerfile
    echo "✅ Dockerfile actualizado"
else
    echo "✅ Dockerfile ya usa npm start"
fi

echo ""
echo "🔍 VERIFICANDO CONFIGURACIÓN:"
echo "-----------------------------------"

echo "📋 Archivos presentes:"
ls -la server.js package.json Dockerfile .nvmrc railway.json 2>/dev/null || echo "❌ Algunos archivos faltan"

echo ""
echo "📋 Contenido de package.json (scripts):"
grep -A 5 '"scripts"' package.json || echo "❌ Scripts no encontrados"

echo ""
echo "📋 Contenido de Dockerfile (CMD):"
grep "CMD" Dockerfile || echo "❌ CMD no encontrado"

echo ""
echo "📤 COMMITTING CAMBIOS:"
echo "-----------------------------------"

# Agregar todos los archivos de configuración
git add .nvmrc railway.json Dockerfile package.json server.js

# Commit con mensaje específico
git commit -m "Fix Railway deployment: Force Node.js detection and npm start"

if [ $? -eq 0 ]; then
    echo "✅ Cambios commiteados exitosamente"
else
    echo "⚠️  No hay cambios para commitear (ya estaba actualizado)"
fi

echo ""
echo "📤 PUSHING A GITHUB:"
echo "-----------------------------------"

git push origin master

if [ $? -eq 0 ]; then
    echo "✅ Push exitoso a GitHub"
    echo "🎉 Railway detectará los cambios y usará Node.js"
else
    echo "❌ Error al hacer push"
    exit 1
fi

echo ""
echo "⏳ ESPERANDO DEPLOYMENT:"
echo "-----------------------------------"
echo "Railway ahora debería:"
echo "1. Detectar el proyecto como Node.js"
echo "2. Usar el Dockerfile para build"
echo "3. Ejecutar 'npm start' para iniciar"
echo "4. Instalar Chrome correctamente"
echo ""
echo "🕐 Esperando 60 segundos para que Railway procese..."
sleep 60

echo ""
echo "🔍 PROBANDO DEPLOYMENT:"
echo "-----------------------------------"

# URLs posibles para probar
POSSIBLE_URLS=(
    "https://auraia2-production.up.railway.app"
    "https://whatsapp-backend-production.up.railway.app"
    "https://nora-whatsapp-production.up.railway.app"
)

for URL in "${POSSIBLE_URLS[@]}"; do
    echo "🔍 Probando: $URL/health"
    
    RESPONSE=$(curl -s -w "%{http_code}" --connect-timeout 10 --max-time 20 "$URL/health" 2>/dev/null)
    HTTP_CODE="${RESPONSE: -3}"
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "🎉 ¡BACKEND FUNCIONANDO!"
        echo "✅ URL: $URL"
        echo "✅ Status: $HTTP_CODE"
        
        # Mostrar respuesta
        CONTENT=$(echo "$RESPONSE" | sed 's/...$//')
        echo "📋 Respuesta: $CONTENT"
        
        # Probar endpoint QR
        echo ""
        echo "🔍 Probando endpoint QR..."
        QR_RESPONSE=$(curl -s -w "%{http_code}" --connect-timeout 10 --max-time 20 "$URL/qr" 2>/dev/null)
        QR_HTTP_CODE="${QR_RESPONSE: -3}"
        
        if [ "$QR_HTTP_CODE" = "200" ]; then
            echo "✅ Endpoint QR funcionando"
            echo "🎉 ¡DEPLOYMENT COMPLETAMENTE EXITOSO!"
        else
            echo "⚠️  Endpoint QR: $QR_HTTP_CODE"
        fi
        
        break
    elif [ "$HTTP_CODE" = "404" ]; then
        echo "❌ 404 - Aún no desplegado en esta URL"
    else
        echo "⚠️  Status: $HTTP_CODE"
    fi
done

echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "-----------------------------------"
echo ""
echo "Si el deployment no funciona aún:"
echo "1. 🖥️  Ve al Railway Dashboard: https://railway.app/dashboard"
echo "2. 🔍 Busca tu proyecto 'auraia2'"
echo "3. 📋 Revisa la pestaña 'Deployments'"
echo "4. 📝 Revisa los logs para errores"
echo "5. ⚙️  Verifica Settings → Environment variables"
echo ""
echo "Variables de entorno necesarias:"
echo "NODE_ENV=production"
echo "PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true"
echo "PUPPETEER_EXECUTABLE_PATH=/usr/bin/google-chrome-stable"
echo ""
echo "🎯 Una vez funcionando, integra con NORA usando la URL correcta"
