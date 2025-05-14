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
        # 1. Obtener configuración de la Nora
        result = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()
        config = result.data[0] if result.data else {}
        modulos_activos = config.get("modulos", [])
        print("🧠 Módulos activos:", modulos_activos)

        # 2. Obtener todos los módulos visuales posibles (no por nombre_nora)
        result_modulos = supabase.table("modulos_disponibles").select("*").execute()
        modulos_definidos = result_modulos.data or []

        # 3. Mapeo visual: convertir modulos_definidos a dict por nombre
        modulos_dict = {
            m["nombre"].strip().lower(): {
                "nombre": m["nombre"].strip(),
                "ruta": m.get("ruta", "").strip() if es_ruta_valida(m.get("ruta", "")) else "",
                "icono": m.get("icono", ""),
                "descripcion": m.get("descripcion", "")
            }
            for m in modulos_definidos
        }

        # 4. Construir lista final de módulos activos que coincidan
        modulos_disponibles = [
            modulos_dict[mod.lower()]
            for mod in modulos_activos
            if mod.lower() in modulos_dict
        ]

        print("✅ Módulos visibles para panel:", modulos_disponibles)

    except Exception as e:
        print(f"❌ Error al obtener módulos para {nombre_nora}: {str(e)}")
        modulos_disponibles = []

    return render_template(
        "panel_cliente.html",
        nombre_nora=nombre_nora,
        nombre_visible=nombre_nora,  # ✅ para que se muestre correctamente
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

def crear_blueprint_panel_cliente(nombre_nora):
    bp = Blueprint(f"panel_cliente_{nombre_nora}", __name__)

    @bp.route("/")
    def configuracion_cliente():
        return render_template(
            "panel_cliente.html",
            nombre_nora=nombre_nora,
            nombre_visible=nombre_nora.capitalize(),
            user=session.get("user", {"name": "Usuario"})
        )

    return bp
