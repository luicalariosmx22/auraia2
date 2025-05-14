print("✅ panel_cliente.py cargado correctamente")

from flask import Blueprint, render_template, session, redirect, url_for
from supabase import create_client
from dotenv import load_dotenv
import os
import datetime

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

panel_cliente_bp = Blueprint("panel_cliente", __name__)

def es_ruta_valida(ruta):
    return ruta and '.' in ruta and len(ruta.split('.')) == 2

# ✅ Función para evitar error de serialización en HTML
def serializar_config(obj):
    if isinstance(obj, dict):
        return {k: serializar_config(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serializar_config(i) for i in obj]
    elif isinstance(obj, (datetime.timedelta, datetime.datetime)):
        return str(obj)
    else:
        return obj

@panel_cliente_bp.route("/<nombre_nora>")
def panel_cliente(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    try:
        # 1. Configuración de la Nora
        result = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()
        config = result.data[0] if result.data else {}

        # 2. Leer los módulos activos
        raw_modulos = config.get("modulos", [])
        if isinstance(raw_modulos, str):
            modulos_activos = [m.strip() for m in raw_modulos.split(",")]
        else:
            modulos_activos = raw_modulos

        # 3. Traer las definiciones de módulos
        resultado_def = supabase.table("modulos_disponibles").select("*").execute()
        modulos_definidos = resultado_def.data or []

        # 4. Indexar los módulos definidos
        modulos_dict = {
            m.get("nombre", "").strip().lower(): {
                "nombre": m.get("nombre", "").strip(),
                "ruta": m.get("ruta", "").strip() if es_ruta_valida(m.get("ruta", "")) else "",
                "icono": m.get("icono", ""),
                "descripcion": m.get("descripcion", "")
            }
            for m in modulos_definidos
        }

        # 5. Filtrar solo los módulos activos que sí tienen visual definido
        modulos_disponibles = [
            {
                "nombre": modulos_dict[nombre.lower()]["nombre"].replace("_", " ").capitalize(),
                "ruta": modulos_dict[nombre.lower()]["ruta"],
                "icono": modulos_dict[nombre.lower()]["icono"] or "🧩",
                "descripcion": modulos_dict[nombre.lower()]["descripcion"] or "Módulo activo"
            }
            for nombre in modulos_activos
            if nombre.lower() in modulos_dict
        ]

        print("✅ Módulos visibles para panel:", modulos_disponibles)

    except Exception as e:
        print(f"❌ Error en panel_cliente: {str(e)}")
        config = {}
        modulos_disponibles = []

    config_serializado = serializar_config(config)
    print("🧪 Configuración serializada:", config_serializado)

    return render_template(
        "panel_cliente.html",
        nombre_nora=nombre_nora,
        nombre_visible=nombre_nora.capitalize(),
        user=session.get("user", {"name": "Usuario"}),
        modulos=modulos_disponibles,
        config=config_serializado
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
