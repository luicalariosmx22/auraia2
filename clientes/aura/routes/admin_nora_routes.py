from flask import Blueprint, request, redirect, url_for, session
from clientes.aura.utils.supabase import supabase

admin_nora_bp = Blueprint("admin_nora", __name__)

# Ruta para guardar estado de IA
@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/estado_ia", methods=["POST"])
def guardar_estado_ia(nombre_nora):
    ia_activa = request.form.get("ia_activa") == "true"
    supabase.table("configuracion_bot").update({"ia_activa": ia_activa}).eq("nombre_nora", nombre_nora).execute()
    return redirect(url_for("admin_nora.mostrar_entrenamiento", nombre_nora=nombre_nora))

# Ruta para cambiar nombre
@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/cambiar_nombre", methods=["POST"])
def cambiar_nombre_nora(nombre_nora):
    nuevo_nombre = request.form.get("nuevo_nombre")
    if nuevo_nombre and nuevo_nombre != nombre_nora:
        supabase.table("configuracion_bot").update({"nombre_nora": nuevo_nombre}).eq("nombre_nora", nombre_nora).execute()
        return redirect(url_for("admin_noras.mostrar_lista"))
    return redirect(url_for("admin_nora.mostrar_entrenamiento", nombre_nora=nombre_nora))

# Ruta para guardar personalidad
@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/personalidad", methods=["POST"])
def guardar_personalidad(nombre_nora):
    personalidad = request.form.get("personalidad")
    supabase.table("configuracion_bot").update({"personalidad": personalidad}).eq("nombre_nora", nombre_nora).execute()
    return redirect(url_for("admin_nora.mostrar_entrenamiento", nombre_nora=nombre_nora))

# Ruta para guardar instrucciones
@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/instrucciones", methods=["POST"])
def guardar_instrucciones(nombre_nora):
    instrucciones = request.form.get("instrucciones")
    supabase.table("configuracion_bot").update({"instrucciones": instrucciones}).eq("nombre_nora", nombre_nora).execute()
    return redirect(url_for("admin_nora.mostrar_entrenamiento", nombre_nora=nombre_nora))

# Ruta para guardar conocimiento
@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar/conocimiento", methods=["POST"])
def guardar_conocimiento(nombre_nora):
    conocimiento = request.form.get("base_conocimiento")
    supabase.table("configuracion_bot").update({"base_conocimiento": conocimiento}).eq("nombre_nora", nombre_nora).execute()
    return redirect(url_for("admin_nora.mostrar_entrenamiento", nombre_nora=nombre_nora))

# Ruta principal de entrenamiento
@admin_nora_bp.route("/admin/nora/<nombre_nora>/entrenar")
def mostrar_entrenamiento(nombre_nora):
    config = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).single().execute().data
    return render_template("entrena_nora.html", nombre_nora=nombre_nora, config=config)
