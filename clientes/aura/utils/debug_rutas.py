from flask import current_app

def generar_html_rutas():
    """
    Genera un HTML con la lista de rutas registradas en la aplicación Flask.

    Returns:
        str: Código HTML con las rutas registradas.
    """
    try:
        # Asegurarse de que se ejecute dentro del contexto de la aplicación
        with current_app.app_context():
            rutas = []
            for rule in current_app.url_map.iter_rules():
                rutas.append({
                    "ruta": rule.rule,
                    "metodos": ", ".join(rule.methods - {"HEAD", "OPTIONS"}),  # Excluir métodos no relevantes
                    "funcion": rule.endpoint
                })

            # Generar el HTML
            html = """
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Rutas Registradas</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    ul { list-style-type: none; padding: 0; }
                    li { margin: 5px 0; }
                </style>
            </head>
            <body>
                <h1>Rutas Registradas</h1>
                <ul>
            """
            for ruta in rutas:
                html += f"<li><strong>{ruta['ruta']}</strong> - Métodos: {ruta['metodos']} - Función: {ruta['funcion']}</li>"
            html += """
                </ul>
            </body>
            </html>
            """
            return html
    except Exception as e:
        return f"❌ Error al generar el HTML de rutas: {str(e)}"