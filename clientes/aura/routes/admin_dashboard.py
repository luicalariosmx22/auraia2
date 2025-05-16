# clientes/aura/routes/admin_dashboard.py

from flask import Blueprint, render_template, session, redirect, url_for, current_app
from supabase import create_client
from dotenv import load_dotenv
import os
from clientes.aura.utils.verificador_rutas_runtime import verificar_rutas_vs_html
import traceback

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

admin_dashboard_bp = Blueprint("admin_dashboard", __name__)

@admin_dashboard_bp.route("/")
def dashboard_admin():
    print("✅ Entrando al dashboard_admin")

    total_noras = 0
    total_errores = 0
    total_modulos = 0
    lista_noras = []

    # Contar Noras desde Supabase
    try:
        response = supabase.table("configuracion_bot").select("*").execute()
        if not response or not response.data:
            print("❌ No se encontraron Noras.")
        else:
            total_noras = len(response.data)
            lista_noras = []
            for item in response.data:
                lista_noras.append({
                    "nombre": item.get("nombre_nora", "Sin nombre"),
                    "ia_activada": item.get("ia_activada", False),
                    "modulos": item.get("modulos", []) or [],  # Ensure modulos defaults to an empty list
                    "ultima_actualizacion": item.get("updated_at", "Sin fecha")
                })
            print(f"✅ Total de Noras encontradas: {total_noras}")
    except Exception as e:
        print(f"❌ Error al obtener Noras: {str(e)}")
        traceback.print_exc()

    # Contar errores desde Supabase
    try:
        errores = supabase.table("logs_errores").select("*").execute()
        if errores and errores.data:
            total_errores = len(errores.data)
            print(f"✅ Total de errores registrados: {total_errores}")
    except Exception as e:
        print(f"❌ Error al obtener errores: {str(e)}")

    # Contar módulos disponibles
    try:
        mod_response = supabase.table("modulos_disponibles").select("id").execute()
        if mod_response and mod_response.data:
            total_modulos = len(mod_response.data)
            print(f"✅ Total de módulos: {total_modulos}")
    except Exception as e:
        print(f"❌ Error al contar módulos: {str(e)}")

    print("✅ Mostrando admin_dashboard.html con datos")

    return render_template("admin_dashboard.html",
        total_noras=total_noras,
        total_errores=total_errores,
        ultimo_deployment="hace 5 minutos",
        total_modulos=total_modulos,
        noras=lista_noras
    )

@admin_dashboard_bp.route("/admin/debug/rutas")
def debug_rutas():
    rutas_erroneas = verificar_rutas_vs_html(current_app)
    return render_template("debug_rutas.html", rutas=rutas_erroneas)
