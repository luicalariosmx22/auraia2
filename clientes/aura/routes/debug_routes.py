# 📁 Archivo: clientes/aura/routes/debug_routes.py

from flask import Blueprint, current_app

debug_routes_bp = Blueprint("debug_routes", __name__)

@debug_routes_bp.route("/debug/rutas", methods=["GET"])
def mostrar_rutas():
    rutas = []

    for regla in current_app.url_map.iter_rules():
        rutas.append({
            "ruta": str(regla),
            "endpoint": regla.endpoint,
            "metodos": list(regla.methods)
        })

    html = "<h2>🔍 Rutas registradas en la app</h2><table border='1' cellpadding='5'><tr><th>Ruta</th><th>Endpoint</th><th>Métodos</th></tr>"

    for r in rutas:
        html += f"<tr><td>{r['ruta']}</td><td>{r['endpoint']}</td><td>{', '.join(r['metodos'])}</td></tr>"

    html += "</table>"
    return html
