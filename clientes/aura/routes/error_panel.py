from flask import Blueprint, render_template, redirect, url_for
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

panel_errores_bp = Blueprint("panel_errores", __name__)

@panel_errores_bp.route("/panel/errores", endpoint="ver_errores")
def ver_errores():
    """
    Mostrar los errores desde la tabla logs_errores en Supabase.
    """
    try:
        response = supabase.table("logs_errores").select("*").execute()
        if not response.data:
            print(f"❌ Error al cargar errores: {not response.data}")
            errores = []
        else:
            errores = response.data
    except Exception as e:
        print(f"❌ Error al cargar errores: {str(e)}")
        errores = []

    return render_template("panel_errores.html", errores=errores)

@panel_errores_bp.route("/panel/errores/limpiar", methods=["POST"])
def limpiar_errores():
    """
    Eliminar todos los errores de la tabla logs_errores en Supabase.
    """
    try:
        response = supabase.table("logs_errores").delete().execute()
        if not response.data:
            print(f"❌ Error al limpiar errores: {not response.data}")
    except Exception as e:
        print(f"❌ Error al limpiar errores: {str(e)}")

    return redirect(url_for("panel_errores.ver_errores"))

# Función auxiliar para usar en el context processor
def contar_errores():
    """
    Contar el número de errores en la tabla logs_errores en Supabase.
    """
    try:
        response = supabase.table("logs_errores").select("id").execute()
        if not response.data:
            print(f"❌ Error al contar errores: {not response.data}")
            return 0
        return len(response.data)
    except Exception as e:
        print(f"❌ Error al contar errores: {str(e)}")
        return 0

# ✅ Alias para importar como 'error_panel_bp' desde app.py
error_panel_bp = panel_errores_bp
