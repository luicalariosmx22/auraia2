print("✅ admin_noras.py cargado correctamente")

from flask import Blueprint, render_template, redirect, url_for
import os
import json
from datetime import datetime

admin_noras_bp = Blueprint("admin_noras", __name__)

# ✅ Ruta oficial
@admin_noras_bp.route("/admin/noras")
def vista_admin():
    directorio_clientes = "clientes"
    lista_noras = []

    for nombre in os.listdir(directorio_clientes):
        ruta_config = os.path.join(directorio_clientes, nombre, "config.json")
        if os.path.exists(ruta_config):
            try:
                with open(ruta_config, "r", encoding="utf-8") as f:
                    config = json.load(f)
                fecha_mod = datetime.fromtimestamp(os.path.getmtime(ruta_config)).strftime("%Y-%m-%d %H:%M")
                lista_noras.append({
                    "nombre": nombre,
                    "ia_activada": config.get("ia_activada", False),
                    "modulos": config.get("modulos", []),
                    "ultima_actualizacion": fecha_mod
                })
            except:
                pass

    return render_template("admin_noras.html", noras=lista_noras)

# ✅ Redirección desde /admin → /admin/noras
@admin_noras_bp.route("/admin")
def redireccionar_a_noras():
    return redirect(url_for("admin_noras.vista_admin"))
