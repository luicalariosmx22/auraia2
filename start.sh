# ✅ Archivo: start.sh
# --- GitHub Copilot EDIT ---
# REWRITE ENTIRE FILE
#!/usr/bin/env bash
# ╭──────────────────────────────────────────────────────────╮
# │   Script de arranque para Railway / Fly / Render, etc.   │
# ╰──────────────────────────────────────────────────────────╯
set -euo pipefail

echo "• Iniciando contenedor — $(date)"

# ▸ Instala wkhtmltopdf + libs solamente si aún no está presente
if ! command -v wkhtmltopdf >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    echo "→ Instalando wkhtmltopdf (apt)…"
    apt-get update -qq \
      && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq wkhtmltopdf libglib2.0-0 \
      && apt-get clean \
      && rm -rf /var/lib/apt/lists/*
  elif command -v apk >/dev/null 2>&1; then
    echo "→ Instalando wkhtmltopdf (apk)…"
    apk add --no-cache wkhtmltopdf ttf-dejavu
  else
    echo "⚠️  No se encontró apt ni apk — instala wkhtmltopdf manualmente." >&2
  fi
fi

echo "→ Lanzando Gunicorn…"
exec gunicorn "clientes.aura:create_app()" \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-4}" \
  --worker-class gevent \
  --timeout 120 \
  --log-level info \
  --access-logfile - \
  --error-logfile -
