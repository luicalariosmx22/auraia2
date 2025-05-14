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
        # 1. Traer la configuración de la Nora
        result = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()
        config = result.data[0] if result.data else {}

        # ✅ Solución: convertir string de módulos en lista
        raw_modulos = config.get("modulos", [])
        if isinstance(raw_modulos, str):
            modulos_activos = [m.strip() for m in raw_modulos.split(",")]
        else:
            modulos_activos = raw_modulos

        print("🧠 Módulos activos (procesados):", modulos_activos)

        # 2. Traer todas las definiciones visuales
        result_disponibles = supabase.table("modulos_disponibles").select("*").execute()
        modulos_definidos = result_disponibles.data or []

        # 3. Indexar disponibles por nombre
        modulos_dict = {
            m.get("nombre", "").strip().lower(): {
                "nombre": m.get("nombre", "").strip(),
                "ruta": m.get("ruta", "").strip() if es_ruta_valida(m.get("ruta", "")) else "",
                "icono": m.get("icono", ""),
                "descripcion": m.get("descripcion", "")
            }
            for m in modulos_definidos
        }

        # 4. Filtrar visuales solo con los módulos activos
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

        print("🔍 DEBUG FINAL:")
        print("🔸 Nombre Nora:", nombre_nora)
        print("🔸 Módulos activos:", modulos_activos)
        print("🔸 Total definidos:", len(modulos_definidos))
        print("🔸 Módulos disponibles para mostrar:", modulos_disponibles)

    except Exception as e:
        print(f"❌ Error al obtener módulos para {nombre_nora}: {str(e)}")
        modulos_disponibles = []

    return render_template(
        "panel_cliente.html",
        nombre_nora=nombre_nora,
        nombre_visible=nombre_nora.capitalize(),
        user=session.get("user", {"name": "Usuario"}),
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
