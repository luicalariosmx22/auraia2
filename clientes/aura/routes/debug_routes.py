# clientes/aura/routes/debug_routes.py

from flask import Blueprint, current_app, render_template

debug_routes_bp = Blueprint("debug_routes", __name__)

@debug_routes_bp.route("/debug/rutas-activas")
def listar_rutas_activas():
    rutas = []
    for regla in current_app.url_map.iter_rules():
        rutas.append({
            "ruta": str(regla),
            "endpoint": regla.endpoint,
            "metodos": ", ".join(regla.methods - {"HEAD", "OPTIONS"})
        })

    return render_template("debug_rutas_activas.html", rutas=rutas)
