# clientes/aura/routes/panel_cliente.py

from flask import Blueprint, render_template, session, redirect, url_for, request, flash
import os
import json

panel_cliente_bp = Blueprint("panel_cliente", __name__)

@panel_cliente_bp.route("/panel_cliente", methods=["GET"])
def panel_cliente():
    user = session.get("user")
    if not user:
        return redirect(url_for("login.login_google"))

    if session.get("is_admin"):
        return redirect(url_for("panel_chat_aura.panel_chat"))

    return render_template("panel_cliente.html", user=user)


@panel_cliente_bp.route("/panel_cliente/contactos/<nombre_nora>", methods=["GET", "POST"])
def ver_contactos(nombre_nora):
    user = session.get("user")

    # 🧪 Verifica la sesión
    print("🧪 SESSION INFO:", session)

    if not user:
        return redirect(url_for("login.login_google"))

    # Permite acceso como admin solo si viene el parámetro ?forzar_cliente=1
    if session.get("is_admin") and "forzar_cliente" not in request.args:
        return redirect(url_for("panel_chat_aura.panel_chat"))

    path = f"clientes/{nombre_nora}/contactos.json"
    config_path = f"clientes/{nombre_nora}/config.json"

    contactos = []
    modulo_ia_activo = False

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            contactos = json.load(f)

    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            modulo_ia_activo = "ia" in config.get("modulos", [])

    if request.method == "POST":
        nuevo = {
            "nombre": request.form.get("nombre"),
            "numero": request.form.get("numero"),
            "etiquetas": [e.strip() for e in request.form.get("etiquetas", "").split(",") if e.strip()],
        }
        if modulo_ia_activo:
            nuevo["ia_activada"] = True

        contactos.append(nuevo)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(contactos, f, indent=2, ensure_ascii=False)

        flash("✅ Contacto guardado correctamente.")
        return redirect(url_for("panel_cliente.ver_contactos", nombre_nora=nombre_nora))

    return render_template(
        "panel_cliente_contactos.html",
        contactos=contactos,
        nombre_nora=nombre_nora,
        modulo_ia_activo=modulo_ia_activo
    )


@panel_cliente_bp.route("/panel_cliente/contactos/<nombre_nora>/toggle_ia", methods=["POST"])
def toggle_ia_contacto(nombre_nora):
    numero = request.form.get("numero")
    path = f"clientes/{nombre_nora}/contactos.json"

    if not os.path.exists(path):
        flash("❌ Contactos no encontrados.")
        return redirect(url_for("panel_cliente.ver_contactos", nombre_nora=nombre_nora))

    with open(path, "r", encoding="utf-8") as f:
        contactos = json.load(f)

    for c in contactos:
        if c.get("numero") == numero:
            c["ia_activada"] = not c.get("ia_activada", True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(contactos, f, indent=2, ensure_ascii=False)

    flash("🔄 Estado de IA actualizado.")
    return redirect(url_for("panel_cliente.ver_contactos", nombre_nora=nombre_nora))
