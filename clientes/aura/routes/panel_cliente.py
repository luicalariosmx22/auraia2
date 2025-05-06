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

def es_ruta_valida(ruta):
    return ruta and '.' in ruta and len(ruta.split('.')) == 2

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
        modulos_supabase = modulos_query.data if modulos_query.data else []

        # Construir la lista de módulos disponibles con detalles
        modulos_disponibles = [
            {
                "nombre": m["nombre"].strip(),
                "ruta": (m.get("ruta") or "").strip() if es_ruta_valida(m.get("ruta", "")) else "",
                "icono": m.get("icono", ""),
                "descripcion": m.get("descripcion", "")
            }
            for m in modulos_supabase if m["nombre"].strip() in [mod.strip() for mod in modulos_activos]
        ]

        print("🔎 Módulos cargados:", modulos_disponibles)  # Debug print statement

    except Exception as e:
        print(f"❌ Error al obtener módulos para {nombre_nora}: {str(e)}")
        modulos_disponibles = []

    return render_template(
        "panel_cliente.html",
        nombre_nora=nombre_nora,
        user=session["user"],
        modulos=modulos_disponibles
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
