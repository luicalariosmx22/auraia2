# clientes/aura/routes/panel_cliente_contactos.py

from flask import Blueprint, render_template, session, request, redirect, url_for
import os
import json

panel_contactos_bp = Blueprint("panel_contactos", __name__)

@panel_contactos_bp.route("/panel_cliente/contactos", methods=["GET", "POST"])
def ver_contactos():
    user = session.get("user")
    if not user:
        return redirect(url_for("login.login_google"))

    carpeta = "aura"  # Esto será dinámico cuando el cliente cambie
    ruta_contactos = f"clientes/{carpeta}/crm/contactos.json"
    os.makedirs(os.path.dirname(ruta_contactos), exist_ok=True)

    # Crear archivo si no existe
    if not os.path.exists(ruta_contactos):
        with open(ruta_contactos, "w", encoding="utf-8") as f:
            json.dump([], f)

    # POST: guardar nuevo contacto
    if request.method == "POST":
        nuevo = {
            "nombre": request.form.get("nombre").strip(),
            "telefono": request.form.get("telefono").strip(),
            "etiquetas": [et.strip() for et in request.form.get("etiquetas", "").split(",") if et.strip()]
        }

        with open(ruta_contactos, "r", encoding="utf-8") as f:
            contactos = json.load(f)

        contactos.append(nuevo)

        with open(ruta_contactos, "w", encoding="utf-8") as f:
            json.dump(contactos, f, indent=4, ensure_ascii=False)

        return redirect(url_for("panel_contactos.ver_contactos"))

    # GET: mostrar contactos
    with open(ruta_contactos, "r", encoding="utf-8") as f:
        contactos = json.load(f)

    return render_template("panel_cliente_contactos.html", user=user, contactos=contactos)
