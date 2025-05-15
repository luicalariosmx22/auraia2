# ✅ Archivo: start.sh
# --- GitHub Copilot EDIT ---
@@
 echo "---------------------------------------------------"
 
+# ▸ Instalar wkhtmltopdf y librerías (soporta Debian/Ubuntu o Alpine en Railway)
+if command -v apt-get >/dev/null 2>&1; then
+  echo "→ Instalando wkhtmltopdf vía apt-get…"
+  apt-get update -qq \
+    && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq wkhtmltopdf libglib2.0-0 \
+    && apt-get clean \
+    && rm -rf /var/lib/apt/lists/*
+elif command -v apk >/dev/null 2>&1; then
+  echo "→ Instalando wkhtmltopdf vía apk…"
+  apk add --no-cache wkhtmltopdf ttf-dejavu
+else
+  echo "⚠️  Gestor de paquetes desconocido: instala wkhtmltopdf manualmente"
+fi
+
 # Comando Gunicorn en una sola línea para máxima compatibilidad.
 # ASEGÚRATE DE QUE ESTA LÍNEA NO TENGA COMENTARIOS EXTRAÑOS AL FINAL O EN MEDIO.
 gunicorn "clientes.aura:create_app()" --bind "0.0.0.0:${PORT}" --workers "${WEB_CONCURRENCY:-4}" --worker-class gevent --timeout 120 --log-level debug --access-logfile - --error-logfile -
 
 echo "--- FIN DEL SCRIPT start.sh (Gunicorn debería estar corriendo si no hay errores arriba) ---"
