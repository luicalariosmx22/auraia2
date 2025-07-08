#!/bin/bash

# Script para triggerar nuevo deployment en Railway
echo "=== TRIGGERING NUEVO DEPLOYMENT EN RAILWAY ==="
echo "Fecha: $(date)"
echo ""

# Verificar que estamos en el directorio correcto
PROJECT_DIR="/mnt/c/Users/PC/PYTHON/Auraai2"
cd "$PROJECT_DIR"

echo "📁 Directorio del proyecto: $PROJECT_DIR"
echo ""

# Verificar estado del repositorio
echo "🔍 VERIFICANDO ESTADO DEL REPOSITORIO:"
echo "-----------------------------------"

# Verificar que no hay cambios sin commit
STATUS=$(git status --porcelain)
if [ -n "$STATUS" ]; then
    echo "⚠️  Hay cambios sin commit:"
    echo "$STATUS"
    echo ""
    echo "🔧 Añadiendo cambios al commit..."
    git add .
    git commit -m "Update Railway deployment configuration - $(date)"
else
    echo "✅ No hay cambios pendientes"
fi

echo ""
echo "🚀 TRIGGERING DEPLOYMENT:"
echo "-----------------------------------"

# Hacer un commit vacío para triggerar el deployment
echo "📝 Creando commit vacío para triggerar rebuild..."
git commit --allow-empty -m "Trigger Railway rebuild - $(date)"

if [ $? -eq 0 ]; then
    echo "✅ Commit vacío creado exitosamente"
else
    echo "❌ Error al crear commit vacío"
    exit 1
fi

echo ""
echo "📤 PUSHING A GITHUB:"
echo "-----------------------------------"

# Push a GitHub
echo "📤 Enviando cambios a GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Push exitoso a GitHub"
    echo "🎉 Railway debería detectar el cambio y iniciar un nuevo deployment"
else
    echo "❌ Error al hacer push"
    echo "⚠️  Verifica tu conexión a internet y credenciales de GitHub"
    exit 1
fi

echo ""
echo "⏳ ESPERANDO DEPLOYMENT:"
echo "-----------------------------------"
echo "El deployment puede tardar 2-5 minutos."
echo "Mientras tanto, puedes:"
echo ""
echo "1. 📱 Abrir Railway Dashboard:"
echo "   https://railway.app/dashboard"
echo ""
echo "2. 🔍 Buscar tu proyecto (probablemente llamado 'auraia2')"
echo ""
echo "3. 📋 Ir a la pestaña 'Deployments' para ver el progreso"
echo ""
echo "4. 📝 Revisar los logs en tiempo real"
echo ""

echo "🕐 Esperando 30 segundos antes de verificar..."
sleep 30

echo ""
echo "🔍 VERIFICANDO DEPLOYMENT:"
echo "-----------------------------------"

# Intentar encontrar la URL correcta
echo "🌐 Buscando la URL correcta del proyecto..."

# URLs posibles basadas en el nombre del repo
POSSIBLE_URLS=(
    "https://auraia2-production.up.railway.app"
    "https://auraia2-production-$(date +%s | tail -c 5).up.railway.app"
    "https://luicalariosmx22-auraia2-production.up.railway.app"
)

for URL in "${POSSIBLE_URLS[@]}"; do
    echo "🔍 Probando: $URL"
    
    RESPONSE=$(curl -s -w "%{http_code}" --connect-timeout 5 --max-time 10 "$URL/health" 2>/dev/null)
    HTTP_CODE="${RESPONSE: -3}"
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "🎉 ¡PROYECTO ENCONTRADO Y FUNCIONANDO!"
        echo "✅ URL exitosa: $URL"
        echo "✅ Status: $HTTP_CODE"
        
        # Probar endpoint QR
        echo "🔍 Probando endpoint QR..."
        QR_RESPONSE=$(curl -s -w "%{http_code}" --connect-timeout 5 --max-time 10 "$URL/qr" 2>/dev/null)
        QR_HTTP_CODE="${QR_RESPONSE: -3}"
        
        if [ "$QR_HTTP_CODE" = "200" ]; then
            echo "✅ Endpoint QR funcionando"
        else
            echo "⚠️  Endpoint QR: $QR_HTTP_CODE"
        fi
        
        break
    elif [ "$HTTP_CODE" = "404" ]; then
        echo "❌ 404 - Proyecto no encontrado en esta URL"
    else
        echo "⚠️  Respuesta inesperada: $HTTP_CODE"
    fi
done

echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "-----------------------------------"
echo ""
echo "1. 🖥️  VE AL RAILWAY DASHBOARD:"
echo "   https://railway.app/dashboard"
echo ""
echo "2. 🔍 BUSCA TU PROYECTO:"
echo "   - Busca 'auraia2' en la lista de proyectos"
echo "   - Verifica que esté conectado a tu repositorio GitHub"
echo ""
echo "3. 📋 REVISA EL DEPLOYMENT:"
echo "   - Ve a la pestaña 'Deployments'"
echo "   - Verifica el estado del último deployment"
echo "   - Revisa los logs si hay errores"
echo ""
echo "4. 🌐 OBTÉN LA URL CORRECTA:"
echo "   - Ve a Settings → Domains"
echo "   - Copia la URL asignada por Railway"
echo ""
echo "5. 🧪 PRUEBA LA URL:"
echo "   - Usa la URL correcta para probar /health y /qr"
echo ""

echo "💡 TIPS:"
echo "-----------------------------------"
echo "- Si el deployment falla, revisa los logs en Railway"
echo "- Asegúrate de que Chrome se instale correctamente"
echo "- Verifica que no haya errores de dependencias"
echo "- El deployment puede tardar hasta 5 minutos"
echo ""
echo "🎯 OBJETIVO:"
echo "Una vez que el deployment esté listo, deberías ver:"
echo "- /health devuelve {\"status\": \"ok\"}"
echo "- /qr devuelve un QR código válido"
echo "- El QR se muestra correctamente en el panel de NORA"
