print("✅ admin_nora.py cargado correctamente")

from flask import Blueprint, render_template, request, redirect, url_for, flash
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

admin_nora_bp = Blueprint("admin_nora", __name__)

@admin_nora_bp.route("/admin/nora/<nombre_nora>/editar", methods=["GET", "POST"])
def editar_nora(nombre_nora):
    modulos_disponibles = [
        "contactos", "ia", "respuestas", "envios",
        "qr_whatsapp_web", "multi_nora", "pagos",
        "redes_sociales", "diseño_personalizado",
        "open_table", "google_calendar"
    ]

    # Cargar configuración desde Supabase
    try:
        response = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()
        if not response.data:
            return f"❌ No se encontró la configuración para {nombre_nora}", 404
        config = response.data[0]
    except Exception as e:
        print(f"❌ Error al cargar configuración: {str(e)}")
        return f"❌ Error al cargar configuración para {nombre_nora}", 500

    if request.method == "POST":
        nuevo_nombre = request.form.get("nuevo_nombre", "").strip()
        nuevos_modulos = request.form.getlist("modulos")

        if not nuevo_nombre:
            flash("❌ Debes ingresar un nombre para la Nora", "error")
            return redirect(request.url)

        if not nuevos_modulos:
            flash("❌ Debes seleccionar al menos un módulo", "error")
            return redirect(request.url)

        # Actualizar configuración en Supabase
        try:
            config["nombre_visible"] = nuevo_nombre
            config["modulos"] = nuevos_modulos
            response = supabase.table("configuracion_bot").update(config).eq("nombre_nora", nombre_nora).execute()
            if not response.data:
                flash("❌ Error al actualizar configuración", "error")
                return redirect(request.url)
        except Exception as e:
            print(f"❌ Error al actualizar configuración: {str(e)}")
            flash("❌ Error al actualizar configuración", "error")
            return redirect(request.url)

        print(f"📝 Nora '{nombre_nora}' actualizada:")
        print(f"    ➤ Nombre visible: {nuevo_nombre}")
        print(f"    ➤ Módulos activos: {', '.join(nuevos_modulos)}")

        flash("✅ Configuración actualizada correctamente", "success")
        return redirect(url_for("admin_nora.editar_nora", nombre_nora=nombre_nora))

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

        # Verificar si ya existe en Supabase
        try:
            response = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_interno).execute()
            if response.data:
                flash("❌ Ya existe una Nora con ese nombre interno", "error")
                return redirect(request.url)
        except Exception as e:
            print(f"❌ Error al verificar existencia de Nora: {str(e)}")
            flash("❌ Error al verificar existencia de Nora", "error")
            return redirect(request.url)

        # Crear nueva configuración en Supabase
        try:
            config = {
                "nombre_nora": nombre_interno,
                "nombre_visible": nombre_visible,
                "ia_activada": True,
                "modulos": modulos
            }
            response = supabase.table("configuracion_bot").insert(config).execute()
            if not response.data:
                flash("❌ Error al crear Nora", "error")
                return redirect(request.url)
        except Exception as e:
            print(f"❌ Error al crear Nora: {str(e)}")
            flash("❌ Error al crear Nora", "error")
            return redirect(request.url)

        print(f"🆕 Nueva Nora creada: {nombre_interno} ({nombre_visible}) con módulos: {', '.join(modulos)}")

        flash("✅ Nora creada correctamente", "success")
        return redirect(url_for("admin_nora.editar_nora", nombre_nora=nombre_interno))

    return render_template(
        "admin_nora_nueva.html",
        modulos_disponibles=modulos_disponibles
    )


@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar", methods=["GET", "POST"])
def entrenar_nora(nombre_nora):
    # Cargar configuración existente desde Supabase
    try:
        response = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()
        if not response.data:
            return f"❌ No se encontró la configuración para {nombre_nora}", 404
        config = response.data[0]
    except Exception as e:
        print(f"❌ Error al cargar configuración: {str(e)}")
        return f"❌ Error al cargar configuración para {nombre_nora}", 500

    if request.method == "POST":
        # Obtener datos del formulario
        personalidad = request.form.get("personalidad", "").strip()
        respuestas_rapidas = request.form.get("respuestas_rapidas", "").strip()
        informacion_empresa = request.form.get("informacion_empresa", "").strip()

        # Actualizar configuración en Supabase
        try:
            config["personalidad"] = personalidad
            config["respuestas_rapidas"] = respuestas_rapidas.split(",")  # Convertir a lista
            config["informacion_empresa"] = informacion_empresa
            response = supabase.table("configuracion_bot").update(config).eq("nombre_nora", nombre_nora).execute()
            if not response.data:
                flash("❌ Error al actualizar configuración", "error")
                return redirect(request.url)
        except Exception as e:
            print(f"❌ Error al actualizar configuración: {str(e)}")
            flash("❌ Error al actualizar configuración", "error")
            return redirect(request.url)

        print(f"🧠 Nora '{nombre_nora}' entrenada:")
        print(f"    ➤ Personalidad: {personalidad}")
        print(f"    ➤ Respuestas rápidas: {respuestas_rapidas}")
        print(f"    ➤ Información de la empresa: {informacion_empresa}")

        flash("✅ Nora entrenada correctamente", "success")
        return redirect(url_for("admin_nora.entrenar_nora", nombre_nora=nombre_nora))

    return render_template(
        "admin_nora_entrenar.html",
        nombre_nora=nombre_nora,
        config=config
    )
