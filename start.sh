#!/bin/sh
# Archivo: start.sh (raíz del proyecto)
# 👉 Script de arranque mejorado para capturar errores de boot en Railway

echo "--- INICIO DEL SCRIPT start.sh ---"
echo "PORT (asignado por Railway): ${PORT}"
echo "WEB_CONCURRENCY (si está definida): ${WEB_CONCURRENCY}"
echo "---------------------------------------------------"

# Ejecuta Gunicorn con configuración optimizada:
# - --preload: carga la app antes de forkear, para crash rápido si hay errores de import
# - -w: usa WEB_CONCURRENCY o 4 workers por defecto
# - --worker-class gevent: mantiene tu clase de worker actual
# - --timeout 120: tiempo de arranque / request extendido en debugging
# - --bind: expone en el puerto de Railway
# - --access-logfile -: logs de acceso en stdout
# - --error-logfile -: logs de error en stdout
# - --capture-output: incluye stdout/stderr en los logs de Railway
# - --log-level debug: máxima verbosidad para diagnóstico
exec gunicorn \
  --preload \
  -w ${WEB_CONCURRENCY:-4} \
  --worker-class gevent \
  --timeout 120 \
  --bind 0.0.0.0:${PORT} \
  --access-logfile - \
  --error-logfile - \
  --capture-output \
  --log-level debug \
  "clientes.aura:create_app()"

echo "--- FIN DEL SCRIPT start.sh (Gunicorn debería estar corriendo si no hay errores arriba) ---"
