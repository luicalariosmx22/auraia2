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

def es_ruta_valida(ruta):
    return isinstance(ruta, str) and "panel_cliente/" in ruta

def serializar_config(obj):
    if isinstance(obj, dict):
        return {k: serializar_config(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serializar_config(i) for i in obj]
    elif isinstance(obj, (datetime.timedelta, datetime.datetime)):
        return str(obj)
    else:
        return obj

def crear_blueprint_panel_cliente(nombre_nora):
    bp = Blueprint(f"panel_cliente_{nombre_nora}", __name__)

    @bp.route("/")
    def configuracion_cliente():
        print(f"🧪 Entrando a configuracion_cliente de {nombre_nora}")

        if "user" not in session:
            return redirect(url_for("login.login_google"))

        try:
            # 1. Configuración de la Nora
            result = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()
            config = result.data[0] if result.data else {}

            # 2. Leer módulos activos
            raw_modulos = config.get("modulos", [])
            if isinstance(raw_modulos, str):
                modulos_activos = [m.strip() for m in raw_modulos.split(",")]
            else:
                modulos_activos = raw_modulos

            # 3. Traer definiciones desde modulos_disponibles
            resultado_def = supabase.table("modulos_disponibles").select("*").execute()
            modulos_definidos = resultado_def.data or []

            modulos_dict = {
                m.get("nombre", "").strip().lower(): {
                    "nombre": m.get("nombre", "").strip(),
                    "ruta": m.get("ruta", "").strip() if es_ruta_valida(m.get("ruta", "")) else "",
                    "icono": m.get("icono", ""),
                    "descripcion": m.get("descripcion", "")
                }
                for m in modulos_definidos
            }

            # 4. Filtrar solo los módulos activos y definidos
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
            print(f"❌ Error en configuracion_cliente: {str(e)}")
            config = {}
            modulos_disponibles = []

        config_serializado = serializar_config(config)

        return render_template(
            "panel_cliente.html",
            nombre_nora=nombre_nora,
            nombre_visible=nombre_nora.capitalize(),
            user=session.get("user", {"name": "Usuario"}),
            modulos=modulos_disponibles
        )

    return bp
