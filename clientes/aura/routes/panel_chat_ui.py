print("✅ panel_chat_ui.py cargado correctamente")

from flask import render_template, session, redirect, url_for
from clientes.aura.routes.panel_chat import panel_chat_bp
from clientes.aura.routes.utils.leer_contactos import leer_contactos

import datetime

@panel_chat_bp.route("/<nombre_nora>")
def panel_chat(nombre_nora):
    """
    Renderiza el panel de chat para una Nora específica.
    """
    print(f"🔍 Iniciando función panel_chat para Nora: {nombre_nora}")
    if "user" not in session:
        print("⚠️ Usuario no autenticado. Redirigiendo al login.")
        return redirect(url_for("login.login_google"))

    print("🔍 Leyendo contactos...")
    contactos = leer_contactos()
    print(f"✅ Contactos leídos: {len(contactos)}")

    # Crear la lista de contactos con su ultimo_mensaje ya formateado
    lista = []
    for c in contactos:
        print(f"🔍 Procesando contacto: {c.get('telefono', 'desconocido')}")
        ultimo_mensaje_str = c.get("ultimo_mensaje")

        try:
            # Parseamos la fecha del último mensaje o asignamos una fecha mínima
            fecha_ultimo = datetime.datetime.strptime(ultimo_mensaje_str, "%Y-%m-%d %H:%M:%S") if ultimo_mensaje_str else datetime.datetime(1900, 1, 1)
            print(f"✅ Fecha parseada: {fecha_ultimo}")
        except Exception as e:
            print(f"❌ Error al parsear fecha en {c.get('telefono', 'desconocido')}: {e}")
            fecha_ultimo = datetime.datetime(1900, 1, 1)

        lista.append({
            **c,
            "fecha_ultimo_mensaje": fecha_ultimo,
        })

    print("🔍 Ordenando contactos por fecha del último mensaje...")
    contactos_ordenados = sorted(
        lista,
        key=lambda c: c.get("fecha_ultimo_mensaje", datetime.datetime(1900, 1, 1)),
        reverse=True
    )
    print("✅ Contactos ordenados.")

    # Extraer etiquetas únicas
    print("🔍 Extrayendo etiquetas únicas...")
    etiquetas_unicas = set()
    for c in contactos_ordenados:
        etiquetas_unicas.update(c.get("etiquetas", []))
    print(f"✅ Etiquetas únicas extraídas: {sorted(etiquetas_unicas)}")

    print(f"✅ Panel de chat renderizado para {len(contactos)} contactos.")
    return render_template(
        "panel_chat.html",
        contactos=contactos_ordenados,
        nombre_nora=nombre_nora,
        etiquetas_unicas=sorted(etiquetas_unicas)
    )
