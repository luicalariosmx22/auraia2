# ✅ Archivo: dev_start.py
from dotenv import load_dotenv
import os

modo = os.getenv("ENTORNO", "local")
if modo == "railway":
    load_dotenv(".env.railway")
else:
    load_dotenv(".env.local")

from gunicorn_patch import app  # asegúrate que esta es tu instancia Flask
app.run(debug=True, port=5000)
