from flask import current_app

def generar_html_rutas():
    """
    Genera un HTML con la lista de rutas registradas en la aplicación Flask.
    
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

    return html