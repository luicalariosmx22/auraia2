#!/bin/sh
# start.sh

echo "--- INICIO DEL SCRIPT start.sh ---"
echo "PORT (asignado por Railway): ${PORT}" # Usamos ${PORT} para más seguridad
echo "WEB_CONCURRENCY (si está definida): ${WEB_CONCURRENCY}"
echo "---------------------------------------------------"

# Comando Gunicorn en una sola línea para máxima compatibilidad.
# ASEGÚRATE DE QUE ESTA LÍNEA NO TENGA COMENTARIOS EXTRAÑOS AL FINAL O EN MEDIO.
gunicorn "clientes.aura:create_app()" --bind "0.0.0.0:${PORT}" --workers "${WEB_CONCURRENCY:-4}" --worker-class gevent --timeout 120 --log-level debug --access-logfile - --error-logfile -

echo "--- FIN DEL SCRIPT start.sh (Gunicorn debería estar corriendo si no hay errores arriba) ---"