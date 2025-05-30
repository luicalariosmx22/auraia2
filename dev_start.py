# ✅ Archivo: dev_start.py
from dotenv import load_dotenv
import os
import logging

# 🧪 Silenciar solo logs de archivos estáticos (como CSS)
werkzeug_logger = logging.getLogger('werkzeug')
class StaticFilter(logging.Filter):
    def filter(self, record):
        return not (
            "/static/" in record.getMessage()
        )
werkzeug_logger.addFilter(StaticFilter())
werkzeug_logger.setLevel(logging.INFO)

# Cargar variables de entorno
modo = os.getenv("ENTORNO", "local")
if modo == "railway":
    load_dotenv(".env.railway")
else:
    load_dotenv(".env.local")

# Lanzar app Flask
from gunicorn_patch import app
app.run(debug=True, port=5000)
