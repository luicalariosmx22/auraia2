print("✅ panel_cliente.py cargado correctamente")

from flask import Blueprint, render_template, session, redirect, url_for
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

panel_cliente_bp = Blueprint("panel_cliente", __name__)

@panel_cliente_bp.route("/panel/cliente/<nombre_nora>")
def panel_cliente(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    session["nombre_nora"] = nombre_nora

    # Cargar configuración desde Supabase
    try:
        response = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()
        if not response.data:
            print(f"❌ Error al cargar configuración: {response.error}")
            return f"❌ No se encontró la configuración de la Nora {nombre_nora}"
        config = response.data[0]
    except Exception as e:
        print(f"❌ Error al cargar configuración: {str(e)}")
        return f"❌ Error al cargar configuración de la Nora {nombre_nora}"

    nombre_visible = config.get("nombre_visible", nombre_nora)
    modulos = config.get("modulos", [])

    print(f"🔓 Acceso al panel del cliente: {nombre_nora} – Usuario: {session['user']['name']}")

    return render_template(
        "panel_cliente.html",
        user=session["user"],
        nombre_nora=nombre_nora,
        nombre_visible=nombre_visible,
        modulos=modulos
    )
