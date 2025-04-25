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

@panel_cliente_bp.route("/<nombre_nora>")
def panel_cliente(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    try:
        # Obtener los módulos activos desde la configuración de la Nora
        response = supabase.table("configuracion_bot").select("modulos").eq("nombre_nora", nombre_nora).execute()
        modulos_activos = response.data[0]["modulos"] if response.data else []

        # Consultar la tabla de módulos disponibles para obtener detalles
        modulos_query = supabase.table("modulos_disponibles").select("*").execute()
        modulos_definidos = [m for m in modulos_query.data if m["nombre"] in modulos_activos]

    except Exception as e:
        print(f"❌ Error al obtener módulos para {nombre_nora}: {str(e)}")
        modulos_definidos = []

    return render_template(
        "panel_cliente.html",
        nombre_nora=nombre_nora,
        user=session["user"],
        modulos=modulos_definidos
    )

@panel_cliente_bp.route("/<nombre_nora>/entrenamiento", methods=["GET", "POST"])
def panel_entrenamiento(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    try:
        response = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()
        config = response.data[0] if response.data else {}
    except Exception as e:
        print(f"❌ Error al cargar configuración: {str(e)}")
        config = {}

    return render_template(
        "entrena_nora.html",
        nombre_nora=nombre_nora,
        config=config,
        user=session["user"]
    )
