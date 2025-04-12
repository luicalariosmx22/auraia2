# 📁 clientes/aura/routes/admin_nora.py

from flask import Blueprint, render_template, abort
import os
import json

admin_nora_bp = Blueprint("admin_nora", __name__)

@admin_nora_bp.route("/admin/nora/<nombre_carpeta>")
def ver_nora(nombre_carpeta):
    ruta_config = f"clientes/{nombre_carpeta}/config.json"

    if not os.path.exists(ruta_config):
        return abort(404, description="Nora no encontrada")

    with open(ruta_config, "r", encoding="utf-8") as f:
        datos = json.load(f)

    return render_template("admin_nora.html", nora=datos, carpeta=nombre_carpeta)
