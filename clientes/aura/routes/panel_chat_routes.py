# clientes/aura/routes/panel_chat_routes.py

from flask import render_template, session, redirect, url_for
from clientes.aura.routes.panel_chat import panel_chat_bp
from clientes.aura.routes.panel_chat_utils import leer_contactos
import datetime
from dateutil import parser  # ✅ Agregado para mejor manejo de fechas

@panel_chat_bp.route("/panel/chat/<nombre_nora>")
def panel_chat(nombre_nora):
    print("🔍 Cargando contactos para mostrar en el panel...")

    if "user" not in session:
        print("⚠️ Usuario no autenticado. Redirigiendo a login.")
        return redirect(url_for("login.login_google"))

    print("🔍 Leyendo contactos desde la base de datos...")
    contactos = leer_contactos()
    print(f"✅ Contactos obtenidos: {len(contactos)}")

    lista = []
    for contacto in contactos:
        print(f"🔍 Procesando contacto: {contacto.get('telefono', 'desconocido')}")

        ultimo_mensaje = contacto.get("ultimo_mensaje")
        fecha_ultimo = datetime.datetime(1900, 1, 1)  # Default

        if ultimo_mensaje:
            try:
                fecha_ultimo = parser.parse(ultimo_mensaje)
                print(f"✅ Fecha último mensaje parseada: {fecha_ultimo}")
            except Exception as e:
                print(f"⚠️ Error parseando 'ultimo_mensaje': {e}")

        lista.append({
            **contacto,
            "fecha_ultimo_mensaje": fecha_ultimo,
        })

    print("🔍 Ordenando contactos por fecha del último mensaje...")
    contactos_ordenados = sorted(
        lista,
        key=lambda c: c.get("fecha_ultimo_mensaje", datetime.datetime(1900, 1, 1)),
        reverse=True
    )
    print("✅ Contactos ordenados.")

    print("🔍 Extrayendo etiquetas únicas...")
    etiquetas_unicas = set()
    for c in contactos_ordenados:
        etiquetas_unicas.update(c.get("etiquetas", []))
    print(f"✅ Etiquetas únicas extraídas: {sorted(etiquetas_unicas)}")

    print(f"✅ Contactos listos para renderizar en el panel.")
    return render_template(
        "panel_chat.html",
        contactos=contactos_ordenados,
        nombre_nora=nombre_nora,
        etiquetas_unicas=sorted(etiquetas_unicas)
    )
