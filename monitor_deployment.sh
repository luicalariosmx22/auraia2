#!/bin/bash

# Monitor Railway deployment progress
echo "🔄 MONITOREANDO DEPLOYMENT DE RAILWAY"
echo "======================================"
echo "Fecha: $(date)"
echo ""

# URLs a probar
URLS=(
    "https://auraia2-production.up.railway.app"
    "https://whatsapp-backend-production.up.railway.app"
    "https://nora-whatsapp-production.up.railway.app"
    "https://luicalariosmx22-auraia2-production.up.railway.app"
)

echo "🎯 CAMBIOS REALIZADOS:"
echo "- ✅ Eliminado start.sh problemático"
echo "- ✅ Usando 'npm start' directamente"
echo "- ✅ Chrome configurado en /usr/bin/google-chrome-stable"
echo "- ✅ Código ya pusheado a GitHub"
echo ""

echo "⏰ ESPERANDO DEPLOYMENT (puede tardar 2-5 minutos)..."
echo ""

# Función para probar URL
check_url() {
    local url=$1
    local response=$(curl -s -w "%{http_code}" --connect-timeout 3 --max-time 5 "$url/health" 2>/dev/null)
    local http_code="${response: -3}"
    
    if [ "$http_code" = "200" ]; then
        echo "🎉 ¡FUNCIONANDO! - $url"
        echo "   Status: $http_code"
        
        # Probar QR también
        local qr_response=$(curl -s -w "%{http_code}" --connect-timeout 3 --max-time 5 "$url/qr" 2>/dev/null)
        local qr_code="${qr_response: -3}"
        
        if [ "$qr_code" = "200" ]; then
            echo "   ✅ QR endpoint también funciona"
        else
            echo "   ⚠️  QR endpoint: $qr_code"
        fi
        
        return 0
    elif [ "$http_code" = "404" ]; then
        echo "❌ 404 - $url"
        return 1
    else
        echo "⏳ $http_code - $url"
        return 1
    fi
}

# Monitorear por 5 minutos
for i in {1..10}; do
    echo "🔍 Intento $i/10 - $(date +%H:%M:%S)"
    
    found=false
    for url in "${URLS[@]}"; do
        if check_url "$url"; then
            found=true
            break
        fi
    done
    
    if [ "$found" = true ]; then
        echo ""
        echo "🎉 ¡DEPLOYMENT EXITOSO!"
        echo "✅ El backend está funcionando correctamente"
        echo "✅ Chrome está disponible"
        echo "✅ Endpoints responden correctamente"
        echo ""
        echo "🎯 PRÓXIMOS PASOS:"
        echo "1. Integrar la URL en NORA"
        echo "2. Probar el panel de WhatsApp Web"
        echo "3. Escanear el QR con WhatsApp real"
        exit 0
    fi
    
    if [ $i -lt 10 ]; then
        echo "⏳ Esperando 30 segundos..."
        sleep 30
    fi
done

echo ""
echo "⚠️  DEPLOYMENT AÚN NO ESTÁ LISTO"
echo "📋 VERIFICA MANUALMENTE:"
echo "1. Railway Dashboard: https://railway.app/dashboard"
echo "2. Busca tu proyecto 'auraia2'"
echo "3. Revisa los logs de deployment"
echo "4. Verifica que no haya errores"
echo ""
echo "💡 EL DEPLOYMENT PUEDE TARDAR MÁS DE 5 MINUTOS"
echo "   Vuelve a ejecutar este script en unos minutos"
