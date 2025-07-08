#!/bin/bash

# Script para configurar Railway con variables de entorno correctas
echo "=== CONFIGURACIÓN DE RAILWAY ENVIRONMENT ==="
echo "Fecha: $(date)"
echo ""

# Verificar que estamos en el directorio correcto
PROJECT_DIR="/mnt/c/Users/PC/PYTHON/Auraai2"
cd "$PROJECT_DIR"

echo "📁 Directorio del proyecto: $PROJECT_DIR"
echo ""

# Commit los cambios del Dockerfile actualizado
echo "🔧 ACTUALIZANDO DOCKERFILE CON VARIABLES DE ENTORNO:"
echo "-----------------------------------"

git add Dockerfile RAILWAY_ENVIRONMENT_SETUP.md
git commit -m "Add environment variables to Dockerfile for Railway deployment"

if [ $? -eq 0 ]; then
    echo "✅ Dockerfile actualizado con variables de entorno"
else
    echo "⚠️  No hay cambios en Dockerfile (ya estaba actualizado)"
fi

echo ""
echo "📤 PUSHING CAMBIOS A GITHUB:"
echo "-----------------------------------"

git push origin master

if [ $? -eq 0 ]; then
    echo "✅ Cambios enviados a GitHub"
    echo "🎉 Railway detectará los cambios automáticamente"
else
    echo "❌ Error al enviar cambios"
    exit 1
fi

echo ""
echo "🌐 CONFIGURACIÓN MANUAL EN RAILWAY:"
echo "-----------------------------------"
echo ""
echo "1. 🖥️  VE AL RAILWAY DASHBOARD:"
echo "   https://railway.app/dashboard"
echo ""
echo "2. 🔍 BUSCA TU PROYECTO:"
echo "   - Busca 'auraia2' en la lista de proyectos"
echo "   - Haz clic en el proyecto para abrirlo"
echo ""
echo "3. ⚙️  CONFIGURA VARIABLES DE ENTORNO:"
echo "   - Ve a Settings → Environment"
echo "   - Añade estas variables (haz clic en 'New Variable' para cada una):"
echo ""
echo "   Variables esenciales:"
echo "   NODE_ENV=production"
echo "   PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true"
echo "   PUPPETEER_EXECUTABLE_PATH=/usr/bin/google-chrome-stable"
echo "   CHROME_PATH=/usr/bin/google-chrome-stable"
echo "   WHATSAPP_SESSION_PATH=/home/pptruser/.wwebjs_auth"
echo "   DISABLE_EXTENSIONS=true"
echo "   DISABLE_DEV_SHM_USAGE=true"
echo ""
echo "4. 🔄 REDEPLOY EL PROYECTO:"
echo "   - Ve a la pestaña 'Deployments'"
echo "   - Haz clic en 'Redeploy' en el último deployment"
echo "   - Espera 2-3 minutos a que termine"
echo ""
echo "5. 🧪 VERIFICA QUE FUNCIONE:"
echo "   - Obtén la URL del proyecto (Settings → Domains)"
echo "   - Prueba: curl https://[TU-URL]/health"
echo "   - Debería devolver: {\"status\":\"ok\",\"chrome\":\"available\"}"
echo ""

echo "💡 TIPS IMPORTANTES:"
echo "-----------------------------------"
echo "- Las variables de entorno son críticas para que Chrome funcione"
echo "- Railway necesita un redeploy después de cambiar variables"
echo "- El Dockerfile ya incluye variables por defecto"
echo "- Si algo falla, revisa los logs en Railway"
echo ""

echo "🎯 OBJETIVO:"
echo "Una vez configurado correctamente, deberías ver:"
echo "- Container se inicia sin errores"
echo "- /health devuelve status ok"
echo "- /qr genera un código QR válido"
echo "- Chrome está disponible en el container"
echo ""

echo "⏳ PRÓXIMOS PASOS:"
echo "-----------------------------------"
echo "1. Configura las variables en Railway Dashboard"
echo "2. Haz redeploy del proyecto"
echo "3. Espera a que termine el deployment"
echo "4. Comparte la URL del proyecto para verificar"
echo "5. Prueba los endpoints /health y /qr"
echo ""

echo "🔗 Railway Dashboard: https://railway.app/dashboard"
echo "📖 Guía detallada: cat RAILWAY_ENVIRONMENT_SETUP.md"
