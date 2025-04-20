import os
from flask import current_app

def generar_html_rutas(app, output_path="clientes/aura/templates/debug_rutas.html"):
    rutas = []

    for rule in app.url_map.iter_rules():
        rutas.append({
            "endpoint": rule.endpoint,
            "ruta": str(rule),
            "metodos": ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
        })

    # Generar HTML simple
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Debug de Rutas Flask</title>
        <style>
            body { font-family: Arial; background: #f4f4f4; padding: 20px; }
            table { width: 100%; border-collapse: collapse; background: white; }
            th, td { padding: 10px; border: 1px solid #ccc; }
            th { background: #222; color: white; }
            tr:nth-child(even) { background: #f9f9f9; }
        </style>
    </head>
    <body>
        <h2>📍 Rutas registradas en la aplicación</h2>
        <table>
            <thead>
                <tr>
                    <th>Endpoint</th>
                    <th>Ruta</th>
                    <th>Métodos</th>
                </tr>
            </thead>
            <tbody>
    """

    for ruta in rutas:
        html += f"""
        <tr>
            <td>{ruta['endpoint']}</td>
            <td>{ruta['ruta']}</td>
            <td>{ruta['metodos']}</td>
        </tr>
        """

    html += """
            </tbody>
        </table>
    </body>
    </html>
    """

    # Guardar en archivo
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ Archivo generado: {output_path}")
