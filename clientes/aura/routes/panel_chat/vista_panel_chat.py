# clientes/aura/routes/panel_chat/vista_panel_chat.py
from flask import Blueprint, render_template, session, redirect, url_for
from clientes.aura.utils.chat.leer_contactos import leer_contactos
from clientes.aura.utils.chat.leer_historial import leer_historial
from clientes.aura.routes.panel_chat.blueprint import panel_chat_bp  # Updated import

@panel_chat_bp.route("/panel/chat/<nombre_nora>", methods=["GET"])  # Confirm route
def panel_chat(nombre_nora):
    print(f"📥 Recibida solicitud para panel de chat con nombre_nora: {nombre_nora}")
    if "user" not in session:
        print("⚠️ Usuario no autenticado, redirigiendo a login.")
        return redirect(url_for("login.login_google"))

    try:
        contactos = leer_contactos(nombre_nora)
        print(f"✅ Contactos obtenidos: {contactos}")
        lista = []
        for c in contactos:
            mensajes = leer_historial(c["telefono"], nombre_nora, limite=10)
            print(f"📨 Mensajes para {c['telefono']}: {mensajes}")
            lista.append({**c, "mensajes": mensajes})
    except Exception as e:
        print(f"❌ Error al cargar el panel de chat: {e}")
        contactos, lista = [], []

    print(f"📤 Renderizando template con contactos: {lista}")
    return render_template("panel_chat.html", contactos=lista, nombre_nora=nombre_nora)

