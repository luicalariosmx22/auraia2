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

# Ruta para entrenamiento (personalidad, instrucciones, IA, nombre_nora)
@cliente_nora_bp.route("/panel_cliente/<nombre_nora>/entrenamiento", methods=["GET"])
def panel_entrenamiento(nombre_nora):
    try:
        config_res = supabase.table("configuracion_bot") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .single() \
            .execute()

        if not config_res.data:
            flash("❌ No se encontró la configuración de esta Nora", "error")
            return redirect(url_for("cliente_nora.configuracion_cliente", nombre_nora=nombre_nora))

        config = config_res.data
        return render_template("entrena_nora.html", nombre_nora=nombre_nora, config=config)

    except Exception as e:
        print(f"❌ Error al cargar entrenamiento: {e}")
        flash("❌ Error al cargar entrenamiento", "error")
        return redirect(url_for("cliente_nora.configuracion_cliente", nombre_nora=nombre_nora))

# Ruta para actualizar la personalidad
@cliente_nora_bp.route("/panel_cliente/<nombre_nora>/entrenar/personalidad", methods=["POST"])
def personalidad(nombre_nora):
    try:
        personalidad = request.form.get("personalidad", "").strip()
        supabase.table("configuracion_bot").update({"personalidad": personalidad}).eq("nombre_nora", nombre_nora).execute()
        flash("✅ Personalidad actualizada correctamente", "success")
    except Exception as e:
        print(f"❌ Error al actualizar personalidad: {str(e)}")
        flash("❌ Error al actualizar personalidad", "error")
    return redirect(url_for("cliente_nora.panel_entrenamiento", nombre_nora=nombre_nora))

# Ruta para actualizar las instrucciones
@cliente_nora_bp.route("/panel_cliente/<nombre_nora>/entrenar/instrucciones", methods=["POST"])
def instrucciones(nombre_nora):
    try:
        instrucciones = request.form.get("instrucciones", "").strip()
        supabase.table("configuracion_bot").update({"instrucciones": instrucciones}).eq("nombre_nora", nombre_nora).execute()
        flash("✅ Instrucciones actualizadas correctamente", "success")
    except Exception as e:
        print(f"❌ Error al actualizar instrucciones: {str(e)}")
        flash("❌ Error al actualizar instrucciones", "error")
    return redirect(url_for("cliente_nora.panel_entrenamiento", nombre_nora=nombre_nora))

# Ruta para activar o desactivar la IA
@cliente_nora_bp.route("/panel_cliente/<nombre_nora>/entrenar/estado_ia", methods=["POST"])
def estado_ia(nombre_nora):
    try:
        ia_activa = request.form.get("ia_activa") == "true"
        supabase.table("configuracion_bot").update({"ia_activa": ia_activa}).eq("nombre_nora", nombre_nora).execute()
        flash("✅ Estado de IA actualizado correctamente", "success")
    except Exception as e:
        print(f"❌ Error al actualizar estado de IA: {str(e)}")
        flash("❌ Error al actualizar estado de IA", "error")
    return redirect(url_for("cliente_nora.panel_entrenamiento", nombre_nora=nombre_nora))
