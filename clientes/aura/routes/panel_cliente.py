# clientes/aura/routes/panel_cliente.py

from flask import Blueprint, render_template, session, redirect, url_for, request
import os
import json

panel_cliente_bp = Blueprint("panel_cliente", __name__)

# 🧾 Vista principal del cliente
@panel_cliente_bp.route("/panel_cliente", methods=["GET"])
def panel_cliente():
    user = session.get("user")

    if not user:
        return redirect(url_for("login.login_google"))

    if session.get("is_admin"):
        return redirect(url_for("panel_chat_aura.panel_chat"))

    return render_template("panel_cliente.html", user=user)

# 📇 Ver contactos dinámico
@panel_cliente_bp.route("/panel_cliente/contactos/<nombre_nora>")
def ver_contactos(nombre_nora):
    user = session.get("user")
    contactos_path = f"clientes/{nombre_nora}/crm/contactos.json"

    contactos = []
    if os.path.exists(contactos_path):
        with open(contactos_path, "r", encoding="utf-8") as f:
            contactos = json.load(f)

    return render_template("panel_cliente_contactos.html", contactos=contactos, user=user, nombre_nora=nombre_nora)

# 🧠 Control de IA dinámico
@panel_cliente_bp.route("/panel_cliente/ia/<nombre_nora>", methods=["GET", "POST"])
def panel_ia(nombre_nora):
    user = session.get("user")
    if not user:
        return redirect(url_for("login.login_google"))

    config_path = f"clientes/{nombre_nora}/config.json"
    if not os.path.exists(config_path):
        return "❌ No se encontró config.json para esa Nora."

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    if request.method == "POST":
        estado_nuevo = request.form.get("ia_activada") == "true"
        config["ia_activada"] = estado_nuevo
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return redirect(url_for("panel_cliente.panel_ia", nombre_nora=nombre_nora))

    return render_template("panel_cliente_ia.html", user=user, ia_activada=config.get("ia_activada", True), nombre_nora=nombre_nora)
