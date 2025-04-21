from flask import current_app

def generar_html_rutas(app, output_path=None):
    """
    Genera un HTML con la lista de rutas registradas en la aplicación Flask.

    Args:
        app (Flask): La instancia de la aplicación Flask.
        output_path (str, optional): Ruta donde se guardará el archivo HTML. Si no se proporciona, solo se devuelve el HTML.

    Returns:
        str: Código HTML con las rutas registradas.
    """
    try:
        with app.app_context():
            rutas = []
            for rule in app.url_map.iter_rules():
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

            # Guardar el HTML en un archivo si se proporciona una ruta
            if output_path:
                with open(output_path, "w", encoding="utf-8") as file:
                    file.write(html)
                print(f"✅ HTML de rutas guardado en: {output_path}")

            return html
    except Exception as e:
        current_app.logger.error(f"❌ Error al generar el HTML de rutas: {str(e)}")
        return f"❌ Error al generar el HTML de rutas: {str(e)}"