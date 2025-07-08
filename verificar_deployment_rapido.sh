#!/bin/bash

# Verificación rápida del estado del deployment
echo "=== VERIFICACIÓN RÁPIDA DE RAILWAY ==="
echo "Fecha: $(date)"
echo ""

# URLs posibles para probar
URLS=(
    "https://auraia2-production.up.railway.app"
    "https://whatsapp-backend-production.up.railway.app"
    "https://nora-whatsapp-production.up.railway.app"
)

# Función para probar una URL
test_url() {
    local url=$1
    local endpoint=${2:-"/health"}
    
    echo "🔍 Probando: $url$endpoint"
    
    RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}\nTIME_TOTAL:%{time_total}" \
        --connect-timeout 5 --max-time 10 "$url$endpoint" 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
        TIME_TOTAL=$(echo "$RESPONSE" | grep "TIME_TOTAL:" | cut -d: -f2)
        CONTENT=$(echo "$RESPONSE" | sed '/HTTP_CODE:/,$d' | head -c 200)
        
        echo "   Status: $HTTP_CODE"
        echo "   Tiempo: ${TIME_TOTAL}s"
        echo "   Contenido: $CONTENT"
        
        if [ "$HTTP_CODE" = "200" ]; then
            echo "   ✅ ¡FUNCIONANDO!"
            return 0
        else
            echo "   ❌ Error: $HTTP_CODE"
            return 1
        fi
    else
        echo "   ❌ Error de conexión"
        return 1
    fi
}

# Probar todas las URLs
echo "🌐 PROBANDO URLS POSIBLES:"
echo "-----------------------------------"

FOUND_WORKING=false

for URL in "${URLS[@]}"; do
    echo ""
    if test_url "$URL" "/health"; then
        echo "🎉 ¡BACKEND ENCONTRADO Y FUNCIONANDO!"
        echo "URL: $URL"
        
        # Probar endpoint QR
        echo ""
        echo "🔍 Probando endpoint QR..."
        if test_url "$URL" "/qr"; then
            echo "✅ Endpoint QR también funciona"
        else
            echo "⚠️  Endpoint QR no funciona"
        fi
        
        FOUND_WORKING=true
        break
    fi
done

echo ""
echo "📊 RESUMEN:"
echo "-----------------------------------"

if [ "$FOUND_WORKING" = true ]; then
    echo "🎉 ¡DEPLOYMENT EXITOSO!"
    echo "✅ El backend está funcionando correctamente"
    echo "✅ Puedes continuar con las pruebas de integración"
else
    echo "❌ No se encontró ningún backend funcionando"
    echo "⚠️  Posibles causas:"
    echo "   - El deployment aún está en progreso"
    echo "   - Hay errores en el build o startup"
    echo "   - La URL del proyecto es diferente"
    echo ""
    echo "📝 Próximos pasos:"
    echo "   1. Revisa el Railway Dashboard"
    echo "   2. Verifica los logs de deployment"
    echo "   3. Confirma la URL correcta del proyecto"
fi

echo ""
echo "🔗 Railway Dashboard: https://railway.app/dashboard"
