from flask import current_app

def generar_html_rutas(output_path=None):
    """
    Genera un HTML con la lista de rutas registradas en la aplicación Flask.

    Args:
        output_path (str, optional): Ruta donde se guardará el archivo HTML. Si no se proporciona, solo se devuelve el HTML.

    Returns:
        str: Código HTML con la información de las rutas.
    """
    rutas = []
    for rule in current_app.url_map.iter_rules():
        rutas.append({
            "ruta": rule.rule,
            "metodos": ", ".join(rule.methods),
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
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f4f4f4; }
            tr:nth-child(even) { background-color: #f9f9f9; }
        </style>
    </head>
    <body>
        <h1>Rutas Registradas en la Aplicación</h1>
        <table>
            <thead>
                <tr>
                    <th>Ruta</th>
                    <th>Métodos</th>
                    <th>Función</th>
                </tr>
            </thead>
            <tbody>
    """
    for ruta in rutas:
        html += f"""
        <tr>
            <td>{ruta['ruta']}</td>
            <td>{ruta['metodos']}</td>
            <td>{ruta['funcion']}</td>
        </tr>
        """
    html += """
            </tbody>
        </table>
    </body>
    </html>
    """

    # Guardar el HTML en un archivo si se proporciona una ruta
    if output_path:
        try:
            with open(output_path, "w", encoding="utf-8") as file:
                file.write(html)
            print(f"✅ HTML de rutas guardado en: {output_path}")
        except Exception as e:
            print(f"❌ Error al guardar el HTML de rutas: {str(e)}")

    return html