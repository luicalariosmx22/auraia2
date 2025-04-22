# clientes/aura/routes/panel_chat/vista_panel_chat.py
from flask import Blueprint, render_template, session, redirect, url_for
from clientes.aura.utils.chat.leer_contactos import leer_contactos
from clientes.aura.utils.chat.leer_historial import leer_historial

vista_panel_chat_bp = Blueprint("vista_panel_chat", __name__)

@vista_panel_chat_bp.route("/panel/chat/<nombre_nora>")
def panel_chat(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    contactos = leer_contactos()
    lista = []
    for c in contactos:
        mensajes = leer_historial(c["telefono"], limite=10)
        lista.append({**c, "mensajes": mensajes})

    return render_template("panel_chat.html", contactos=lista, nombre_nora=nombre_nora)

