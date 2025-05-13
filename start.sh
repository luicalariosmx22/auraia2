#!/bin/sh
# start.sh

echo "VERIFICANDO VARIABLES DE ENTORNO EN start.sh:"
echo "PORT (asignado por Railway, esperamos): $PORT"
echo "WEB_CONCURRENCY (si está definida): $WEB_CONCURRENCY"
echo "---------------------------------------------------"

# Si PORT no está asignado por Railway o está vacío, Gunicorn fallará.
# Puedes añadir un valor por defecto aquí como fallback, aunque es mejor
# que Railway lo provea.
# Ejemplo con fallback (solo si Railway DEFINITIVAMENTE no provee PORT):
# EFFECTIVE_PORT=${PORT:-5000} 
# echo "Puerto efectivo a usar: $EFFECTIVE_PORT"
# Pero primero intenta sin esto, confiando en que Railway SÍ provee PORT.

gunicorn "clientes.aura:create_app()" \
    --bind "0.0.0.0:${PORT}" \ # Asegúrate que PORT tenga un valor numérico aquí
    --workers "${WEB_CONCURRENCY:-4}" \
    --worker-class gevent \
    --timeout 120 \
    --log-level debug \
    --access-logfile - \
    --error-logfile -