print("✅ admin_nora.py cargado correctamente")

from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
import json

admin_nora_bp = Blueprint("admin_nora", __name__)

@admin_nora_bp.route("/admin/nora/<nombre_nora>/editar", methods=["GET", "POST"])
def editar_nora(nombre_nora):
    base_path = f"clientes/{nombre_nora}"
    ruta_config = os.path.join(base_path, "config.json")

    if not os.path.exists(ruta_config):
        return f"❌ No se encontró el archivo config.json para {nombre_nora}", 404

    modulos_disponibles = [
        "contactos", "ia", "respuestas", "envios",
        "qr_whatsapp_web", "multi_nora", "pagos",
        "redes_sociales", "diseño_personalizado",
        "open_table", "google_calendar"
    ]

    with open(ruta_config, "r", encoding="utf-8") as f:
        config = json.load(f)

    if request.method == "POST":
        nuevo_nombre = request.form.get("nuevo_nombre", "").strip()
        nuevos_modulos = request.form.getlist("modulos")

        if not nuevo_nombre:
            flash("❌ Debes ingresar un nombre para la Nora", "error")
            return redirect(request.url)

        if not nuevos_modulos:
            flash("❌ Debes seleccionar al menos un módulo", "error")
            return redirect(request.url)

        config["nombre_visible"] = nuevo_nombre
        config["modulos"] = nuevos_modulos

        with open(ruta_config, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

        print(f"📝 Nora '{nombre_nora}' actualizada:")
        print(f"    ➤ Nombre visible: {nuevo_nombre}")
        print(f"    ➤ Módulos activos: {', '.join(nuevos_modulos)}")

        flash("✅ Configuración actualizada correctamente", "success")
        return redirect(url_for("admin_nora_dashboard.dashboard_nora", nombre_nora=nombre_nora))

    return render_template(
        "admin_nora_editar.html",
        nombre_nora=nombre_nora,
        config=config,
        modulos_disponibles=modulos_disponibles
    )


@admin_nora_bp.route("/admin/nora/nueva", methods=["GET", "POST"])
def crear_nora():
    modulos_disponibles = [
        "contactos", "ia", "respuestas", "envios",
        "qr_whatsapp_web", "multi_nora", "pagos",
        "redes_sociales", "diseño_personalizado",
        "open_table", "google_calendar"
    ]

    if request.method == "POST":
        nombre_interno = request.form.get("nombre_interno", "").strip().lower().replace(" ", "").replace("_", "")
        nombre_visible = request.form.get("nombre_visible", "").strip()
        modulos = request.form.getlist("modulos")

        if not nombre_interno or not nombre_visible:
            flash("❌ Debes completar ambos campos", "error")
            return redirect(request.url)

        carpeta = f"clientes/{nombre_interno}"
        if os.path.exists(carpeta):
            flash("❌ Ya existe una Nora con ese nombre interno", "error")
            return redirect(request.url)

        os.makedirs(carpeta, exist_ok=True)
        config = {
            "nombre_visible": nombre_visible,
            "ia_activada": True,
            "modulos": modulos
        }
        with open(os.path.join(carpeta, "config.json"), "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

        os.makedirs(os.path.join(carpeta, "crm"), exist_ok=True)
        os.makedirs(os.path.join(carpeta, "soporte"), exist_ok=True)
        os.makedirs(os.path.join(carpeta, "database"), exist_ok=True)

        # Crear bot_data.json vacío
        ruta_botdata = os.path.join(carpeta, "database", "bot_data.json")
        with open(ruta_botdata, "w", encoding="utf-8") as f:
            json.dump({}, f)

        print(f"🆕 Nueva Nora creada: {nombre_interno} ({nombre_visible}) con módulos: {', '.join(modulos)}")

        flash("✅ Nora creada correctamente", "success")
        return redirect(url_for("admin_nora.editar_nora", nombre_nora=nombre_interno))

    return render_template(
        "admin_nora_nueva.html",
        modulos_disponibles=modulos_disponibles
    )
