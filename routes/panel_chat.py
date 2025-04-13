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

    return render_template("panel_cliente.html", user=session["user"])
