# clientes/aura/routes/admin_dashboard.py

from flask import Blueprint, render_template
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

admin_dashboard_bp = Blueprint("admin_dashboard", __name__)

@admin_dashboard_bp.route("/admin")
def dashboard_admin():
    total_noras = 0
    total_errores = 0

    # Contar Noras desde Supabase
    try:
        response = supabase.table("configuracion_bot").select("id").execute()
        if not response.data:  # Verifica si no hay datos
            print("⚠️ No se encontraron Noras en la tabla 'configuracion_bot'.")
        else:
            total_noras = len(response.data)
    except Exception as e:
        print(f"❌ Error al contar Noras: {str(e)}")

    # Contar errores desde Supabase
    try:
        response = supabase.table("logs_errores").select("id").execute()
        if not response.data:  # Verifica si no hay datos
            print("⚠️ No se encontraron errores en la tabla 'logs_errores'.")
        else:
            total_errores = len(response.data)
    except Exception as e:
        print(f"❌ Error al contar errores: {str(e)}")

    return render_template("admin_dashboard.html",
        total_noras=total_noras,
        total_errores=total_errores,
        ultimo_deployment="hace 5 minutos"  # puedes actualizar esto después
    )
