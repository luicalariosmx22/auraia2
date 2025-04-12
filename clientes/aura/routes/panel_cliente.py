# clientes/aura/routes/panel_cliente.py

from flask import Blueprint, render_template, session, redirect, url_for

panel_cliente_bp = Blueprint("panel_cliente", __name__)

@panel_cliente_bp.route("/panel_cliente", methods=["GET"])
def panel_cliente():
    user = session.get("user")

    if not user:
        return redirect(url_for("login.login_google"))

    if session.get("is_admin"):
        return redirect(url_for("panel_chat_aura.panel_chat"))

    return render_template("panel_cliente.html", user=user)
