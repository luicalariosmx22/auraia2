from flask import Blueprint, render_template, session, request, redirect, url_for
import os
import json

panel_contactos_bp = Blueprint("panel_cliente_contactos", __name__)

@panel_contactos_bp.route("/panel_cliente/contactos/<nombre_nora>", methods=["GET", "POST"])
def panel_contactos(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    # Ruta base de la Nora AI
    carpeta = f"clientes/{nombre_nora}"
    ruta_contactos = f"{carpeta}/crm/contactos.json"
    ruta_config = f"{carpeta}/config.json"

    os.makedirs(os.path.dirname(ruta_contactos), exist_ok=True)

    # Si no existe el archivo de contactos, lo crea vacío
    if not os.path.exists(ruta_contactos):
        with open(ruta_contactos, "w", encoding="utf-8") as f:
            json.dump([], f)

    # Carga el archivo de configuración para saber si tiene activada la IA
    ia_permitida = False
    if os.path.exists(ruta_config):
        with open(ruta_config, "r", encoding="utf-8") as f:
            config = json.load(f)
            modulos = config.get("modulos", [])
            ia_permitida = "ia" in modulos

    # POST: guardar nuevo contacto
    if request.method == "POST":
        nuevo = {
            "nombre": request.form.get("nombre").strip(),
            "telefono": request.form.get("telefono").strip(),
            "etiquetas": [et.strip() for et in request.form.get("etiquetas", "").split(",") if et.strip()],
            "ia": True  # Por defecto, la IA está activa por contacto
        }

        with open(ruta_contactos, "r", encoding="utf-8") as f:
            contactos = json.load(f)

        contactos.append(nuevo)

        with open(ruta_contactos, "w", encoding="utf-8") as f:
            json.dump(contactos, f, indent=4, ensure_ascii=False)

        return redirect(url_for("panel_cliente_contactos.panel_contactos", nombre_nora=nombre_nora))

    # GET: cargar contactos
    with open(ruta_contactos, "r", encoding="utf-8") as f:
        contactos = json.load(f)

    return render_template(
        "panel_cliente_contactos.html",
        user=session["user"],
        contactos=contactos,
        nombre_nora=nombre_nora,
        ia_permitida=ia_permitida
    )
