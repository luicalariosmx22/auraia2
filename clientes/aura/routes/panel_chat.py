from flask import Blueprint, render_template, request, session, redirect, url_for
import os
import json

panel_chat_bp = Blueprint('panel_chat_aura', __name__)

@panel_chat_bp.route("/panel/chat/aura", methods=["GET"])
def panel_chat():
    if "user" not in session:
        return redirect(url_for("google_login.login"))

    if not session.get("is_admin"):
        return redirect(url_for("panel_chat_aura.panel_cliente"))

    historial_dir = "clientes/aura/database/historial"
    contactos = []

    if os.path.exists(historial_dir):
        for archivo in os.listdir(historial_dir):
            if archivo.endswith(".json"):
                ruta = os.path.join(historial_dir, archivo)
                with open(ruta, "r", encoding="utf-8") as f:
                    mensajes = json.load(f)
                    if mensajes:
                        nombre = mensajes[-1].get("nombre", "Sin Nombre")
                        contactos.append({
                            "numero": archivo.replace(".json", ""),
                            "nombre": nombre,
                            "ultimo": mensajes[-1]["mensaje"],
                            "hora": mensajes[-1]["hora"]
                        })

    return render_template("panel_chat.html", contactos=contactos, user=session["user"])

@panel_chat_bp.route("/panel_cliente", methods=["GET"])
def panel_cliente():
    if "user" not in session:
        return redirect(url_for("google_login.login"))

    return render_template("panel_cliente.html", user=session["user"])
