print("✅ admin_verificador_rutas.py cargado correctamente")

from flask import Blueprint, render_template, current_app
from flask import session, redirect, url_for

admin_verificador_bp = Blueprint("admin_verificador_rutas", __name__)

@admin_verificador_bp.route("/admin/verificador_rutas")
def verificador_rutas():
    if "user" not in session or not session.get("is_admin"):
        return redirect(url_for("login.login_google"))

    rutas = []
    for rule in current_app.url_map.iter_rules():
        rutas.append({
            "endpoint": rule.endpoint,
            "ruta": str(rule),
            "métodos": ", ".join(rule.methods - {"HEAD", "OPTIONS"})
        })

    rutas.sort(key=lambda x: x["ruta"])  # Ordenar alfabéticamente por ruta

    return render_template("admin_verificador_rutas.html", rutas=rutas)
