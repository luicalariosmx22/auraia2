print("✅ panel_cliente_envios.py cargado correctamente")

from flask import Blueprint, render_template, request, redirect, url_for, session
import os
import json

panel_cliente_envios_bp = Blueprint("panel_cliente_envios", __name__)

@panel_cliente_envios_bp.route("/panel/cliente/<nombre_nora>/envios", methods=["GET", "POST"])
def panel_envios(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    ruta_envios = f"clientes/{nombre_nora}/envios_programados.json"

    if not os.path.exists(ruta_envios):
        with open(ruta_envios, "w", encoding="utf-8") as f:
            json.dump([], f)

    with open(ruta_envios, "r", encoding="utf-8") as f:
        envios = json.load(f)

    if request.method == "POST":
        nuevo_envio = {
            "mensaje": request.form.get("mensaje"),
            "fecha": request.form.get("fecha"),
            "hora": request.form.get("hora")
        }
        envios.append(nuevo_envio)
        with open(ruta_envios, "w", encoding="utf-8") as f:
            json.dump(envios, f, indent=4, ensure_ascii=False)
        return redirect(url_for("panel_cliente_envios.panel_envios", nombre_nora=nombre_nora))

    return render_template(
        "panel_cliente_envios.html",
        envios=envios,
        nombre_nora=nombre_nora,
        user=session["user"]
    )
