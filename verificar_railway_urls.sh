#!/bin/bash

# Script para verificar diferentes URLs de Railway
echo "=== VERIFICACIÓN DE URLS DE RAILWAY ==="
echo "Fecha: $(date)"

# URLs posibles de Railway
URLS=(
    "https://whatsapp-backend-production-8a3a.up.railway.app"
    "https://auraia2-production.up.railway.app"
    "https://whatsapp-web-backend-production.up.railway.app"
    "https://nora-whatsapp-backend-production.up.railway.app"
)

# Endpoints a probar
ENDPOINTS=(
    "/health"
    "/qr"
    "/status"
    "/"
)

for URL in "${URLS[@]}"; do
    echo ""
    echo "==========================================="
    echo "🔍 Probando URL base: $URL"
    echo "==========================================="
    
    for ENDPOINT in "${ENDPOINTS[@]}"; do
        echo ""
        echo "--- Endpoint: $ENDPOINT ---"
        FULL_URL="$URL$ENDPOINT"
        
        # Test con timeout de 5 segundos
        RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}\nTIME_TOTAL:%{time_total}" --connect-timeout 5 --max-time 10 "$FULL_URL" 2>/dev/null)
        
        if [ $? -eq 0 ]; then
            echo "✅ Respuesta recibida para: $FULL_URL"
            
            # Extraer status y tiempo
            HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
            TIME_TOTAL=$(echo "$RESPONSE" | grep "TIME_TOTAL:" | cut -d: -f2)
            
            echo "Status: $HTTP_STATUS"
            echo "Tiempo: ${TIME_TOTAL}s"
            
            # Mostrar contenido (primeras 500 chars)
            CONTENT=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/,$d' | head -c 500)
            echo "Contenido: $CONTENT"
            
            # Si es 200, marcar como exitoso
            if [ "$HTTP_STATUS" = "200" ]; then
                echo "🎉 ¡ENDPOINT FUNCIONAL ENCONTRADO!"
                echo "URL exitosa: $FULL_URL"
            fi
        else
            echo "❌ Error de conexión: $FULL_URL"
        fi
    done
done

echo ""
echo "==========================================="
echo "🔍 Verificando dominio principal Railway"
echo "==========================================="

# Verificar si el dominio principal responde
echo "Probando dominio railway.app..."
curl -s -w "\nHTTP Status: %{http_code}\n" --connect-timeout 5 "https://railway.app" | head -1

echo ""
echo "==========================================="
echo "📝 RESUMEN"
echo "==========================================="
echo "- Si algún endpoint respondió con 200, el backend está funcionando"
echo "- Si todos dan 404, puede que la app no esté desplegada correctamente"
echo "- Si hay errores de conexión, verifica la URL de Railway"
echo "- Revisa los logs de Railway para más detalles"
