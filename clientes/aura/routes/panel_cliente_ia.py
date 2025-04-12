# clientes/aura/routes/panel_cliente_ia.py

from flask import Blueprint, render_template, request, redirect, url_for, session
import os
import json

panel_ia_bp = Blueprint("panel_ia", __name__)

@panel_ia_bp.route("/panel_cliente/ia", methods=["GET", "POST"])
def panel_ia():
    user = session.get("user")
    if not user:
        return redirect(url_for("login.login_google"))

    carpeta = "aura"  # Más adelante será dinámico
    config_path = f"clientes/{carpeta}/config.json"

    if not os.path.exists(config_path):
        return "❌ No se encontró el archivo config.json"

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    if request.method == "POST":
        estado_nuevo = request.form.get("ia_activada") == "true"
        config["ia_activada"] = estado_nuevo

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

        return redirect(url_for("panel_ia.panel_ia"))

    return render_template("panel_cliente_ia.html", user=user, ia_activada=config.get("ia_activada", True))
