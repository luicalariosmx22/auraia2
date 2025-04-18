# routes/panel_chat.py
from flask import Blueprint, render_template, session, redirect, url_for

panel_chat_bp = Blueprint("panel_chat", __name__)

# Ruta para el panel principal
@panel_chat_bp.route("/panel")
def panel_chat():
    if "user" not in session:
        return redirect(url_for("google_login.login"))

    if session.get("is_admin"):
        return render_template("panel_chat.html", user=session["user"])
    else:
        return redirect(url_for("panel_cliente"))

# Ruta para el panel limitado (clientes)
@panel_chat_bp.route("/panel_cliente")
def panel_cliente():
    if "user" not in session:
        return redirect(url_for("google_login.login"))

    # Variables adicionales para estadísticas y configuración
    nombre_nora = "aura"  # Ejemplo, reemplazar con lógica dinámica si es necesario
    nombre_visible = "Nora AI"  # Ejemplo, reemplazar con lógica dinámica si es necesario
    modulos = ["contactos", "respuestas", "ia", "envios"]  # Ejemplo, reemplazar con datos reales
    total_contactos = 120  # Ejemplo, reemplazar con consulta real
    sin_ia = 30  # Ejemplo, reemplazar con consulta real
    sin_etiquetas = 50  # Ejemplo, reemplazar con consulta real
    total_respuestas = 15  # Ejemplo, reemplazar con consulta real

    return render_template(
        "panel_cliente.html",
        user=session["user"],
        nombre_nora=nombre_nora,
        nombre_visible=nombre_visible,
        modulos=modulos,
        total_contactos=total_contactos,
        sin_ia=sin_ia,
        sin_etiquetas=sin_etiquetas,
        total_respuestas=total_respuestas
    )
