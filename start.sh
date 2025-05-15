# ✅ Archivo: start.sh
# --- GitHub Copilot EDIT ---
@@
-#!/bin/sh
-# start.sh
-
-echo "--- INICIO DEL SCRIPT start.sh ---"
-echo "PORT (asignado por Railway): ${PORT}" # Usamos ${PORT} para más seguridad
-echo "WEB_CONCURRENCY (si está definida): ${WEB_CONCURRENCY}"
-echo "---------------------------------------------------"
-
-# Comando Gunicorn en una sola línea para máxima compatibilidad.
-# ASEGÚRATE DE QUE ESTA LÍNEA NO TENGA COMENTARIOS EXTRAÑOS AL FINAL O EN MEDIO.
-gunicorn "clientes.aura:create_app()" --bind "0.0.0.0:${PORT}" --workers "${WEB_CONCURRENCY:-4}" --worker-class gevent --timeout 120 --log-level debug --access-logfile - --error-logfile -
-
-echo "--- FIN DEL SCRIPT start.sh (Gunicorn debería estar corriendo si no hay errores arriba) ---"
+#!/bin/sh
+# start.sh – arranque de Nora AI
+set -euo pipefail
+
+echo "--- INICIO DEL SCRIPT start.sh ---"
+echo "PORT (asignado por Railway): ${PORT}"
+echo "WEB_CONCURRENCY (si está definida): ${WEB_CONCURRENCY}"
+echo "---------------------------------------------------"
+
+# ▸ Instala wkhtmltopdf + libglib2.0-0 solo si aún no está
+if ! command -v wkhtmltopdf >/dev/null 2>&1; then
+  if command -v apt-get >/dev/null 2>&1; then
+    echo "→ Instalando wkhtmltopdf vía apt-get…"
+    apt-get update -qq \
+      && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq wkhtmltopdf libglib2.0-0 \
+      && apt-get clean \
+      && rm -rf /var/lib/apt/lists/*
+  elif command -v apk >/dev/null 2>&1; then
+    echo "→ Instalando wkhtmltopdf vía apk…"
+    apk add --no-cache wkhtmltopdf ttf-dejavu
+  else
+    echo "⚠️  wkhtmltopdf no instalado (no apt / no apk). Continúo…" >&2
+  fi
+fi
+
+echo "→ Lanzando Gunicorn…"
+exec gunicorn "clientes.aura:create_app()" \
+  --bind "0.0.0.0:${PORT:-8000}" \
+  --workers "${WEB_CONCURRENCY:-4}" \
+  --worker-class gevent \
+  --timeout 120 \
+  --log-level info \
+  --access-logfile - \
+  --error-logfile -
