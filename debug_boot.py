# Archivo: debug_boot.py

import traceback

try:
    # Importa el módulo completo (no solo la variable app)
    import app
    app = app.app
except Exception as e:
    # Si falla el arranque de app.py, guarda el error
    with open("boot_error.log", "w") as f:
        f.write("❌ Error al iniciar la app\n")
        f.write(str(e) + "\n\n")
        f.write(traceback.format_exc())

    # Crea una app mínima de emergencia
    from flask import Flask
    app = Flask(__name__)

    @app.route("/")
    def fallback():
        return f"""
        <h1 style='color:red'>❌ Error al arrancar la app principal</h1>
        <p><strong>Consulta el log en:</strong> <a href='/debug/bootlog'>/debug/bootlog</a></p>
        """

    @app.route("/debug/bootlog")
    def mostrar_log():
        try:
            with open("boot_error.log", "r") as f:
                contenido = f.read()
            return f"<h2>📄 boot_error.log</h2><pre>{contenido}</pre>"
        except FileNotFoundError:
            return "<p>No se encontró ningún error guardado.</p>"
