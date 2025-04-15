print("✅ panel_cliente.py cargado correctamente")

from flask import Blueprint, render_template, session, redirect, url_for
import os
import json

panel_cliente_bp = Blueprint("panel_cliente", __name__)

@panel_cliente_bp.route("/panel/cliente/<nombre_nora>")
def panel_cliente(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    session["nombre_nora"] = nombre_nora
    ruta_config = f"clientes/{nombre_nora}/config.json"

    if not os.path.exists(ruta_config):
        return f"❌ No se encontró la configuración de la Nora {nombre_nora}"

    with open(ruta_config, "r", encoding="utf-8") as f:
        config = json.load(f)

    nombre_visible = config.get("nombre_visible", nombre_nora)
    modulos = config.get("modulos", [])

    print(f"🔓 Acceso al panel del cliente: {nombre_nora} – Usuario: {session['user']['name']}")

    return render_template(
        "panel_cliente.html",
        user=session["user"],
        nombre_nora=nombre_nora,
        nombre_visible=nombre_visible,
        modulos=modulos
    )
