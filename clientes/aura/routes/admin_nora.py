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


@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/bienvenida", methods=["POST"])
def entrenar_bienvenida(nombre_nora):
    # Obtener el mensaje de bienvenida del formulario
    bienvenida = request.form.get("bienvenida", "").strip()

    if not bienvenida:
        flash("❌ El mensaje de bienvenida no puede estar vacío.", "error")
        return redirect(url_for("admin_nora.entrenar_nora", nombre_nora=nombre_nora))

    # Guardar el mensaje de bienvenida en la base de datos
    try:
        response = supabase.table("configuracion_bot").update({
            "bienvenida": bienvenida
        }).eq("nombre_nora", nombre_nora).execute()

        if not response.data:
            flash("❌ Error al guardar el mensaje de bienvenida.", "error")
            return redirect(url_for("admin_nora.entrenar_nora", nombre_nora=nombre_nora))

        flash("✅ Mensaje de bienvenida guardado correctamente.", "success")
    except Exception as e:
        print(f"❌ Error al guardar el mensaje de bienvenida: {str(e)}")
        flash("❌ Error al guardar el mensaje de bienvenida.", "error")

    return redirect(url_for("admin_nora.entrenar_nora", nombre_nora=nombre_nora))


# Ruta para guardar estado de IA
@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/estado_ia", methods=["POST"])
def guardar_estado_ia(nombre_nora):
    try:
        ia_activa = request.form.get("ia_activa") == "true"
        supabase.table("configuracion_bot").update({"ia_activa": ia_activa}).eq("nombre_nora", nombre_nora).execute()
        flash("✅ Estado de IA actualizado correctamente", "success")
    except Exception as e:
        print(f"❌ Error al actualizar estado de IA: {str(e)}")
        flash("❌ Error al actualizar estado de IA", "error")
    return redirect(url_for("admin_nora.mostrar_entrenamiento", nombre_nora=nombre_nora))


# Ruta para cambiar nombre
@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/cambiar_nombre", methods=["POST"])
def cambiar_nombre_nora(nombre_nora):
    try:
        nuevo_nombre = request.form.get("nuevo_nombre", "").strip()
        if nuevo_nombre and nuevo_nombre != nombre_nora:
            supabase.table("configuracion_bot").update({"nombre_nora": nuevo_nombre}).eq("nombre_nora", nombre_nora).execute()
            flash("✅ Nombre de Nora actualizado correctamente", "success")
            return redirect(url_for("admin_nora.mostrar_lista"))
        flash("⚠️ El nuevo nombre no puede estar vacío o ser igual al actual", "warning")
    except Exception as e:
        print(f"❌ Error al cambiar nombre de Nora: {str(e)}")
        flash("❌ Error al cambiar nombre de Nora", "error")
    return redirect(url_for("admin_nora.mostrar_entrenamiento", nombre_nora=nombre_nora))


# Ruta para guardar personalidad
@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/personalidad", methods=["POST"])
def guardar_personalidad(nombre_nora):
    try:
        personalidad = request.form.get("personalidad", "").strip()
        supabase.table("configuracion_bot").update({"personalidad": personalidad}).eq("nombre_nora", nombre_nora).execute()
        flash("✅ Personalidad actualizada correctamente", "success")
    except Exception as e:
        print(f"❌ Error al actualizar personalidad: {str(e)}")
        flash("❌ Error al actualizar personalidad", "error")
    return redirect(url_for("admin_nora.mostrar_entrenamiento", nombre_nora=nombre_nora))


# Ruta para guardar instrucciones
@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/instrucciones", methods=["POST"])
def guardar_instrucciones(nombre_nora):
    try:
        instrucciones = request.form.get("instrucciones", "").strip()
        supabase.table("configuracion_bot").update({"instrucciones": instrucciones}).eq("nombre_nora", nombre_nora).execute()
        flash("✅ Instrucciones actualizadas correctamente", "success")
    except Exception as e:
        print(f"❌ Error al actualizar instrucciones: {str(e)}")
        flash("❌ Error al actualizar instrucciones", "error")
    return redirect(url_for("admin_nora.mostrar_entrenamiento", nombre_nora=nombre_nora))


# Ruta para guardar conocimiento
@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/conocimiento", methods=["POST"])
def guardar_conocimiento(nombre_nora):
    try:
        conocimiento = request.form.get("base_conocimiento", "").strip()
        supabase.table("configuracion_bot").update({"base_conocimiento": conocimiento}).eq("nombre_nora", nombre_nora).execute()
        flash("✅ Base de conocimiento actualizada correctamente", "success")
    except Exception as e:
        print(f"❌ Error al actualizar base de conocimiento: {str(e)}")
        flash("❌ Error al actualizar base de conocimiento", "error")
    return redirect(url_for("admin_nora.mostrar_entrenamiento", nombre_nora=nombre_nora))


# Ruta principal de entrenamiento
@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar")
def mostrar_entrenamiento(nombre_nora):
    try:
        config = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).single().execute().data
        if not config:
            flash("❌ No se encontró la configuración de Nora", "error")
            return redirect(url_for("admin_nora.mostrar_lista"))
        return render_template("entrena_nora.html", nombre_nora=nombre_nora, config=config)
    except Exception as e:
        print(f"❌ Error al cargar configuración de Nora: {str(e)}")
        flash("❌ Error al cargar configuración de Nora", "error")
        return redirect(url_for("admin_nora.mostrar_lista"))
