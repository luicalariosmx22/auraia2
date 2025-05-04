# clientes/aura/routes/panel_chat/vista_panel_chat.py
from flask import Blueprint, render_template, session, redirect, url_for
from clientes.aura.utils.chat.leer_contactos import leer_contactos
from clientes.aura.utils.chat.leer_historial import leer_historial
from clientes.aura.routes.panel_chat.blueprint import panel_chat_bp  # Updated import

@panel_chat_bp.route("/panel/chat/<nombre_nora>", methods=["GET"])  # Added methods=["GET"]
def panel_chat(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    try:
        contactos = leer_contactos(nombre_nora)
        lista = [
            {**c, "mensajes": leer_historial(c["telefono"], nombre_nora, limite=10)}
            for c in contactos
        ]
    except Exception as e:
        print(f"❌ Error al cargar el panel de chat: {e}")
        contactos, lista = [], []

    return render_template("panel_chat.html", contactos=lista, nombre_nora=nombre_nora)

