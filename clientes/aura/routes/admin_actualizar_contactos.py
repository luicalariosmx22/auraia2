print("✅ admin_actualizar_contactos.py cargado correctamente")

from flask import Blueprint, redirect, url_for, session, flash
from dotenv import load_dotenv
import os
from supabase import create_client

# Configuración Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

admin_actualizar_contactos_bp = Blueprint("admin_actualizar_contactos", __name__)

@admin_actualizar_contactos_bp.route("/admin/actualizar_contactos/<nombre_nora>")
def actualizar_contactos_admin(nombre_nora):
    if "user" not in session or not session.get("is_admin"):
        flash("Acceso no autorizado.", "error")
        return redirect(url_for("login.login_google"))

    try:
        print(f"🔍 Iniciando actualización de contactos para: {nombre_nora}")
        response = supabase.table("contactos").select("*").eq("nombre_nora", nombre_nora).execute()
        contactos = response.data or []

        for contacto in contactos:
            telefono = contacto.get("telefono")
            if not telefono:
                continue

            historial_response = supabase.table("historial_conversaciones") \
                .select("*") \
                .eq("telefono", telefono) \
                .order("hora", desc=True) \
                .limit(1) \
                .execute()

            historial = historial_response.data

            if historial:
                ultimo = historial[0]
                update_data = {
                    "ultimo_mensaje": ultimo["hora"],
                    "mensaje_reciente": ultimo["mensaje"]
                }
                supabase.table("contactos").update(update_data).eq("telefono", telefono).eq("nombre_nora", nombre_nora).execute()

        flash(f"✅ Contactos de '{nombre_nora}' actualizados exitosamente.", "success")
        return redirect(url_for("admin_dashboard.dashboard_admin"))  # Redirecciona al dashboard admin o donde prefieras

    except Exception as e:
        print(f"❌ Error actualizando contactos: {e}")
        flash("Error actualizando contactos. Revisa la consola.", "error")
        return redirect(url_for("admin_dashboard.dashboard_admin"))
