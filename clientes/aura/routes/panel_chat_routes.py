# clientes/aura/routes/panel_chat_routes.py

from flask import render_template, session, redirect, url_for
from clientes.aura.routes.panel_chat import panel_chat_bp
from clientes.aura.routes.panel_chat_utils import leer_contactos

@panel_chat_bp.route("/panel/chat/<nombre_nora>")
def panel_chat(nombre_nora):
    print("🔍 Cargando contactos para mostrar en el panel...")

    if "user" not in session:
        print("⚠️ Usuario no autenticado. Redirigiendo a login.")
        return redirect(url_for("login.login_google"))

    contactos = leer_contactos()
    print(f"✅ Contactos obtenidos: {len(contactos)}")

    lista = []
    for contacto in contactos:
        ultimo_mensaje = contacto.get("ultimo_mensaje")
        mensaje_reciente = contacto.get("mensaje_reciente")

        try:
            fecha_ultimo = datetime.datetime.strptime(ultimo_mensaje, "%Y-%m-%d %H:%M:%S") if ultimo_mensaje else datetime.datetime(1900, 1, 1)
        except Exception as e:
            print(f"⚠️ Error al parsear fecha: {e}")
            fecha_ultimo = datetime.datetime(1900, 1, 1)

        lista.append({
            **contacto,
            "fecha_ultimo_mensaje": fecha_ultimo,
        })

    # Ordenar los contactos por último mensaje
    contactos_ordenados = sorted(
        lista,
        key=lambda c: c.get("fecha_ultimo_mensaje", datetime.datetime(1900, 1, 1)),
        reverse=True
    )

    # Extraer todas las etiquetas únicas
    etiquetas_unicas = set()
    for c in contactos_ordenados:
        etiquetas_unicas.update(c.get("etiquetas", []))

    print(f"✅ Contactos ordenados listos para mostrar.")

    return render_template(
        "panel_chat.html",
        contactos=contactos_ordenados,
        nombre_nora=nombre_nora,
        etiquetas_unicas=sorted(etiquetas_unicas)
    )
