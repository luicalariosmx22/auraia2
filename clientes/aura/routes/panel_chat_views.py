print("✅ panel_chat_views.py cargado correctamente")

from flask import render_template, session, redirect, url_for
from clientes.aura.routes.panel_chat_utils import (
    leer_contactos,
    parse_fecha
)
from clientes.aura.routes.panel_chat import panel_chat_bp
import datetime

@panel_chat_bp.route("/<nombre_nora>")
def panel_chat(nombre_nora):
    """
    Renderiza el panel de chat para una Nora específica.
    """
    print(f"\U0001F50D Iniciando función panel_chat para Nora: {nombre_nora}")
    if "user" not in session:
        print("⚠️ Usuario no autenticado. Redirigiendo al login.")
        return redirect(url_for("login.login_google"))

    contactos = leer_contactos()

    # Crear la lista de contactos con su ultimo_mensaje ya formateado
    lista = []
    for c in contactos:
        ultimo_mensaje_str = c.get("ultimo_mensaje")

        try:
            # Parseamos la fecha del último mensaje o asignamos una fecha mínima
            fecha_ultimo = datetime.datetime.strptime(ultimo_mensaje_str, "%Y-%m-%d %H:%M:%S") if ultimo_mensaje_str else datetime.datetime(1900, 1, 1)
        except Exception as e:
            print(f"❌ Error al parsear fecha en {c.get('telefono', 'desconocido')}: {e}")
            fecha_ultimo = datetime.datetime(1900, 1, 1)

        lista.append({
            **c,
            "fecha_ultimo_mensaje": fecha_ultimo.strftime("%d %b %H:%M") if fecha_ultimo else None  # ✅ FECHA FORMATEADA
        })

    # Ordenar contactos por la fecha parseada del campo 'ultimo_mensaje'
    contactos_ordenados = sorted(
        lista,
        key=lambda c: c.get("fecha_ultimo_mensaje", datetime.datetime(1900, 1, 1)),
        reverse=True
    )

    # Extraer etiquetas únicas
    etiquetas_unicas = set()
    for c in contactos_ordenados:
        etiquetas_unicas.update(c.get("etiquetas", []))

    print(f"✅ Panel de chat renderizado para {len(contactos)} contactos.")
    return render_template(
        "panel_chat.html",
        contactos=contactos_ordenados,
        nombre_nora=nombre_nora,
        etiquetas_unicas=sorted(etiquetas_unicas)
    )
