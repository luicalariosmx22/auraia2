# Archivo: debug_boot.py

import traceback

try:
    from app import app  # Intenta cargar la app normal
except Exception as e:
    with open("boot_error.log", "w") as f:
        f.write("❌ Error al iniciar la app\n")
        f.write(str(e) + "\n\n")
        f.write(traceback.format_exc())

    # Crea una app de emergencia
    from flask import Flask
    app = Flask(__name__)

    @app.route("/")
    def fallback():
        return f"""
            <h1 style='color:red'>❌ Error al arrancar la app principal</h1>
            <p>Ve a <a href='/debug/bootlog'>/debug/bootlog</a> para ver el error completo.</p>
        """

    @app.route("/debug/bootlog")
    def mostrar_log():
        try:
            with open("boot_error.log", "r") as f:
                contenido = f.read()
            return f"<h2>📄 boot_error.log</h2><pre>{contenido}</pre>"
        except FileNotFoundError:
            return "<p>No hay errores registrados. Todo debería funcionar bien.</p>"
