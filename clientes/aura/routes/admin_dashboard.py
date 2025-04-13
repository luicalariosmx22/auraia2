# clientes/aura/routes/admin_dashboard.py

from flask import Blueprint, render_template
import os
import json

admin_dashboard_bp = Blueprint("admin_dashboard", __name__)

@admin_dashboard_bp.route("/admin")
def dashboard_admin():
    base_path = "clientes"
    total_noras = 0

    # Contar carpetas de Noras (proyectos/clientes)
    if os.path.exists(base_path):
        total_noras = len([
            nombre for nombre in os.listdir(base_path)
            if os.path.isdir(os.path.join(base_path, nombre))
        ])

    # Contar errores del log si existe
    errores_path = "logs_errores.json"
    errores = []
    if os.path.exists(errores_path):
        with open(errores_path, "r", encoding="utf-8") as f:
            try:
                errores = json.load(f)
            except Exception:
                errores = []

    return render_template("admin_dashboard.html",
        total_noras=total_noras,
        total_errores=len(errores),
        ultimo_deployment="hace 5 minutos"  # puedes actualizar esto después
    )
