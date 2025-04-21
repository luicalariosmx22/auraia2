from flask import Blueprint, render_template, request, redirect, url_for, flash
from clientes.aura.utils.supabase import supabase
import uuid

panel_conocimiento_bp = Blueprint("panel_conocimiento", __name__)

# Ruta para mostrar el panel de conocimiento
@panel_conocimiento_bp.route("/admin/nora/<nombre_nora>/conocimiento")
def panel_conocimiento(nombre_nora):
    try:
        registros = supabase.table("base_conocimiento").select("*").eq("nombre_nora", nombre_nora).order("tema").execute().data
        return render_template("panel_conocimiento.html", nombre_nora=nombre_nora, registros=registros)
    except Exception as e:
        print(f"❌ Error al cargar el conocimiento: {e}")
        flash("❌ Error al cargar el conocimiento", "error")
        return redirect(url_for("admin_nora.mostrar_lista"))

# Ruta para agregar nuevo conocimiento
@panel_conocimiento_bp.route("/admin/nora/<nombre_nora>/conocimiento/agregar", methods=["POST"])
def agregar_conocimiento(nombre_nora):
    try:
        tema = request.form.get("tema")
        pregunta = request.form.get("pregunta")
        respuesta = request.form.get("respuesta")
        prioridad = request.form.get("prioridad", 1)

        if not respuesta.strip():
            flash("⚠️ La respuesta es obligatoria", "warning")
            return redirect(url_for("panel_conocimiento.panel_conocimiento", nombre_nora=nombre_nora))

        supabase.table("base_conocimiento").insert({
            "id": str(uuid.uuid4()),
            "nombre_nora": nombre_nora,
            "tema": tema,
            "pregunta": pregunta,
            "respuesta": respuesta.strip(),
            "prioridad": int(prioridad)
        }).execute()

        flash("✅ Conocimiento agregado correctamente", "success")
    except Exception as e:
        print(f"❌ Error al agregar conocimiento: {e}")
        flash("❌ Error al agregar conocimiento", "error")
    return redirect(url_for("panel_conocimiento.panel_conocimiento", nombre_nora=nombre_nora))

# Ruta para eliminar conocimiento
@panel_conocimiento_bp.route("/admin/nora/<nombre_nora>/conocimiento/eliminar/<id>", methods=["POST"])
def eliminar_conocimiento(nombre_nora, id):
    try:
        supabase.table("base_conocimiento").delete().eq("id", id).execute()
        flash("✅ Conocimiento eliminado correctamente", "success")
    except Exception as e:
        print(f"❌ Error al eliminar conocimiento: {e}")
        flash("❌ Error al eliminar conocimiento", "error")
    return redirect(url_for("panel_conocimiento.panel_conocimiento", nombre_nora=nombre_nora))

# Ruta para mostrar el formulario de edición
@panel_conocimiento_bp.route("/admin/nora/<nombre_nora>/conocimiento/editar/<id>")
def editar_conocimiento(nombre_nora, id):
    try:
        registro = supabase.table("base_conocimiento").select("*").eq("id", id).single().execute().data
        if not registro:
            flash("⚠️ No se encontró el registro solicitado", "warning")
            return redirect(url_for("panel_conocimiento.panel_conocimiento", nombre_nora=nombre_nora))
        return render_template("editar_conocimiento.html", nombre_nora=nombre_nora, registro=registro)
    except Exception as e:
        print(f"❌ Error al cargar el registro para edición: {e}")
        flash("❌ Error al cargar el registro para edición", "error")
        return redirect(url_for("panel_conocimiento.panel_conocimiento", nombre_nora=nombre_nora))

# Ruta para actualizar conocimiento
@panel_conocimiento_bp.route("/admin/nora/<nombre_nora>/conocimiento/editar/<id>", methods=["POST"])
def actualizar_conocimiento(nombre_nora, id):
    try:
        datos = {
            "tema": request.form.get("tema"),
            "pregunta": request.form.get("pregunta"),
            "respuesta": request.form.get("respuesta").strip(),
            "prioridad": int(request.form.get("prioridad", 1))
        }

        if not datos["respuesta"]:
            flash("⚠️ La respuesta es obligatoria", "warning")
            return redirect(url_for("panel_conocimiento.editar_conocimiento", nombre_nora=nombre_nora, id=id))

        supabase.table("base_conocimiento").update(datos).eq("id", id).execute()
        flash("✅ Conocimiento actualizado correctamente", "success")
    except Exception as e:
        print(f"❌ Error al actualizar conocimiento: {e}")
        flash("❌ Error al actualizar conocimiento", "error")
    return redirect(url_for("panel_conocimiento.panel_conocimiento", nombre_nora=nombre_nora))
