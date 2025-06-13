# clientes/aura/routes/admin_dashboard.py
# 👉 Protege el dashboard con verificación de sesión

from flask import Blueprint, render_template, current_app, session, redirect, url_for
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.verificador_rutas_runtime import verificar_rutas_vs_html
from clientes.aura.middlewares.verificar_login import admin_login_required
import traceback

admin_dashboard_bp = Blueprint("admin_dashboard", __name__)

@admin_dashboard_bp.route("/")
@admin_login_required
def dashboard_admin():
    # ✅ Verificación de login
    if "email" not in session or not session.get("is_admin"):
        return redirect(url_for("login.login"))

    print("✅ Entrando al dashboard_admin")

    total_noras = 0
    total_errores = 0
    total_modulos = 0
    lista_noras = []

    # Obtener Noras desde Supabase
    try:
        response = supabase.table("configuracion_bot").select("nombre_nora, ia_activa, modulos").execute()
        if response and response.data:
            total_noras = len(response.data)
            lista_noras = [
                {
                    "nombre": item.get("nombre_nora", "Sin nombre"),
                    "ia_activada": item.get("ia_activa", False),
                    "modulos": item.get("modulos", []) or [],
                    "ultima_actualizacion": "No disponible vía API"
                }
                for item in response.data
            ]
            print(f"✅ Total de Noras encontradas: {total_noras}")
        else:
            print("❌ No se encontraron Noras.")
    except Exception as e:
        print(f"❌ Error al obtener Noras: {str(e)}")
        traceback.print_exc()

    # Obtener errores desde Supabase
    try:
        errores = supabase.table("logs_errores").select("*").execute()
        if errores and errores.data:
            total_errores = len(errores.data)
            print(f"✅ Total de errores registrados: {total_errores}")
    except Exception as e:
        print(f"❌ Error al obtener errores: {str(e)}")

    # Obtener módulos disponibles
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
