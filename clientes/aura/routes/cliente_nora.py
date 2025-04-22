print("✅ cliente_nora.py cargado correctamente")

from flask import Blueprint, render_template, request, redirect, url_for, flash
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

cliente_nora_bp = Blueprint("cliente_nora", __name__)

# Ruta para mostrar la página de configuración del cliente
@cliente_nora_bp.route("/panel_cliente/<nombre_nora>/configuracion", methods=["GET", "POST"])
def configuracion_cliente(nombre_nora):
    try:
        # Cargar configuración desde Supabase
        response = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()
        if not response.data:
            return f"❌ No se encontró la configuración para {nombre_nora}", 404
        config = response.data[0]
    except Exception as e:
        print(f"❌ Error al cargar configuración: {str(e)}")
        return f"❌ Error al cargar configuración para {nombre_nora}", 500

    if request.method == "POST":
        # Obtener datos del formulario
        nombre_visible = request.form.get("nombre_visible", "").strip()
        respuestas_rapidas = request.form.get("respuestas_rapidas", "").strip()
        informacion_empresa = request.form.get("informacion_empresa", "").strip()
        bienvenida = request.form.get("bienvenida", "").strip()

        # Actualizar configuración en Supabase
        try:
            config["nombre_visible"] = nombre_visible
            config["respuestas_rapidas"] = respuestas_rapidas.split(",")  # Convertir a lista
            config["informacion_empresa"] = informacion_empresa
            config["bienvenida"] = bienvenida
            response = supabase.table("configuracion_bot").update(config).eq("nombre_nora", nombre_nora).execute()
            if not response.data:
                flash("❌ Error al actualizar configuración", "error")
                return redirect(request.url)
        except Exception as e:
            print(f"❌ Error al actualizar configuración: {str(e)}")
            flash("❌ Error al actualizar configuración", "error")
            return redirect(request.url)

        print(f"✅ Configuración de cliente '{nombre_nora}' actualizada:")
        print(f"    ➤ Nombre visible: {nombre_visible}")
        print(f"    ➤ Respuestas rápidas: {respuestas_rapidas}")
        print(f"    ➤ Información de la empresa: {informacion_empresa}")
        print(f"    ➤ Bienvenida: {bienvenida}")

        flash("✅ Configuración actualizada correctamente", "success")
        return redirect(url_for("cliente_nora.configuracion_cliente", nombre_nora=nombre_nora))

    return render_template(
        "cliente_configuracion.html",
        nombre_nora=nombre_nora,
        config=config
    )

# Ruta para actualizar el estado de la IA
@cliente_nora_bp.route("/panel_cliente/<nombre_nora>/entrenar/estado_ia", methods=["POST"])
def estado_ia(nombre_nora):
    try:
        ia_activa = request.form.get("ia_activa") == "true"
        supabase.table("configuracion_bot").update({"ia_activa": ia_activa}).eq("nombre_nora", nombre_nora).execute()
        flash("✅ Estado de IA actualizado correctamente", "success")
    except Exception as e:
        print(f"❌ Error al actualizar estado de IA: {str(e)}")
        flash("❌ Error al actualizar estado de IA", "error")
    return redirect(url_for("panel_cliente.panel_entrenamiento", nombre_nora=nombre_nora))

# Ruta para manejar la personalidad
@cliente_nora_bp.route("/panel_cliente/<nombre_nora>/entrenar/personalidad", methods=["POST"])
def personalidad(nombre_nora):
    try:
        personalidad = request.form.get("personalidad", "").strip()
        supabase.table("configuracion_bot").update({"personalidad": personalidad}).eq("nombre_nora", nombre_nora).execute()
        flash("✅ Personalidad actualizada correctamente", "success")
    except Exception as e:
        print(f"❌ Error al actualizar personalidad: {str(e)}")
        flash("❌ Error al actualizar personalidad", "error")
    return redirect(url_for("panel_cliente.panel_entrenamiento", nombre_nora=nombre_nora))

# Ruta para manejar las instrucciones
@cliente_nora_bp.route("/panel_cliente/<nombre_nora>/entrenar/instrucciones", methods=["POST"])
def instrucciones(nombre_nora):
    try:
        instrucciones = request.form.get("instrucciones", "").strip()
        supabase.table("configuracion_bot").update({"instrucciones": instrucciones}).eq("nombre_nora", nombre_nora).execute()
        flash("✅ Instrucciones actualizadas correctamente", "success")
    except Exception as e:
        print(f"❌ Error al actualizar instrucciones: {str(e)}")
        flash("❌ Error al actualizar instrucciones", "error")
    return redirect(url_for("panel_cliente.panel_entrenamiento", nombre_nora=nombre_nora))

# Ruta para manejar el conocimiento (ahora en tabla conocimiento_nora)
@cliente_nora_bp.route("/panel_cliente/<nombre_nora>/entrenar/conocimiento", methods=["GET", "POST"])
def gestionar_conocimiento(nombre_nora):
    try:
        # Buscar el número asociado a esa Nora
        config_res = supabase.table("configuracion_bot").select("numero_nora").eq("nombre_nora", nombre_nora).single().execute()
        if not config_res.data:
            flash("❌ No se encontró el número de Nora para gestionar conocimiento", "error")
            return redirect(url_for("panel_cliente.panel_entrenamiento", nombre_nora=nombre_nora))

        numero_nora = config_res.data["numero_nora"]

        if request.method == "POST":
            # Obtener el contenido del conocimiento desde el formulario
            conocimiento = request.form.get("base_conocimiento", "").strip()
            titulo = request.form.get("titulo", "").strip()

            if not titulo:
                flash("❌ Debes proporcionar un título para la tabla de conocimiento", "error")
                return redirect(url_for("cliente_nora.gestionar_conocimiento", nombre_nora=nombre_nora))

            # Dividir el nuevo contenido en bloques por párrafo
            bloques = [b.strip() for b in conocimiento.split("\n\n") if b.strip()]
            inserts = [{"numero_nora": numero_nora, "titulo": titulo, "contenido": bloque} for bloque in bloques]

            # Insertar nuevos bloques en la tabla 'conocimiento_nora'
            if inserts:
                supabase.table("conocimiento_nora").insert(inserts).execute()
                flash("✅ Conocimiento agregado correctamente", "success")

        # Obtener todas las tablas de conocimiento existentes para este cliente
        tablas_res = supabase.table("conocimiento_nora").select("id, titulo").eq("numero_nora", numero_nora).execute()
        tablas = tablas_res.data or []

    except Exception as e:
        # Manejo de errores
        print(f"❌ Error al gestionar conocimiento: {str(e)}")
        flash("❌ Error al gestionar conocimiento", "error")
        tablas = []

    # Renderizar la página con las tablas existentes
    return render_template(
        "entrena_nora.html",
        nombre_nora=nombre_nora,
        tablas=tablas
    )


@cliente_nora_bp.route("/panel_cliente/<nombre_nora>/entrenar/conocimiento/eliminar/<int:tabla_id>", methods=["POST"])
def eliminar_conocimiento(nombre_nora, tabla_id):
    try:
        # Eliminar la tabla de conocimiento por ID
        supabase.table("conocimiento_nora").delete().eq("id", tabla_id).execute()
        flash("✅ Tabla de conocimiento eliminada correctamente", "success")
    except Exception as e:
        print(f"❌ Error al eliminar tabla de conocimiento: {str(e)}")
        flash("❌ Error al eliminar tabla de conocimiento", "error")

    return redirect(url_for("cliente_nora.gestionar_conocimiento", nombre_nora=nombre_nora))