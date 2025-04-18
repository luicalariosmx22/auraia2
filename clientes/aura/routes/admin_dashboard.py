# clientes/aura/routes/admin_dashboard.py

from flask import Blueprint, render_template, session, redirect, url_for
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
    # Verificar si el usuario tiene una sesión activa
    if "user" not in session:
        print("⚠️ Usuario no autenticado. Redirigiendo al login.")
        return redirect(url_for("login.login_google"))

    # Verificar si el usuario es administrador
    if not session.get("is_admin", False):
        print("⚠️ Usuario no es administrador. Redirigiendo al panel del cliente.")
        return redirect(url_for("panel_cliente.panel_cliente", nombre_nora="aura"))

    total_noras = 0
    total_errores = 0

    # Contar Noras desde Supabase
    try:
        print("🔍 Contando Noras en la tabla 'configuracion_bot'...")
        response = supabase.table("configuracion_bot").select("id").execute()
        if not response.data:  # Verifica si no hay datos
            print("⚠️ No se encontraron Noras en la tabla 'configuracion_bot'.")
        else:
            total_noras = len(response.data)
            print(f"✅ Total de Noras encontradas: {total_noras}")
    except Exception as e:
        print(f"❌ Error al contar Noras: {str(e)}")

    # Contar errores desde Supabase
    try:
        print("🔍 Contando errores en la tabla 'logs_errores'...")
        response = supabase.table("logs_errores").select("id").execute()
        if not response.data:  # Verifica si no hay datos
            print("⚠️ No se encontraron errores en la tabla 'logs_errores'.")
        else:
            total_errores = len(response.data)
            print(f"✅ Total de errores encontrados: {total_errores}")
    except Exception as e:
        print(f"❌ Error al contar errores: {str(e)}")

    print("✅ Renderizando la plantilla 'admin_dashboard.html'...")
    return render_template("admin_dashboard.html",
        total_noras=total_noras,
        total_errores=total_errores,
        ultimo_deployment="hace 5 minutos"  # puedes actualizar esto después
    )
