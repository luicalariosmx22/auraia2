# Archivo: debug_boot.py

import traceback

try:
    from app import app  # Importa la app Flask desde app.py
except Exception as e:
    with open("boot_error.log", "w") as f:
        f.write("❌ Error al iniciar la app\n")
        f.write(str(e) + "\n\n")
        f.write(traceback.format_exc())

    # Generar una app mínima de emergencia para que Railway no marque 502
    from flask import Flask
    app = Flask(__name__)

    @app.route("/")
    def fallback():
        return "<h1>❌ Error al arrancar la app principal</h1><pre>" + str(e) + "</pre>"

# Iniciar Gunicorn buscará esta app si corres: gunicorn debug_boot:app