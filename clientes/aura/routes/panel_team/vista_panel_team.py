from flask import Blueprint, render_template, session, redirect
from supabase import create_client
import os

panel_team_bp = Blueprint("panel_team", __name__)  # ✅ Esto debe estar ANTES del @route

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@panel_team_bp.route("/<nombre_nora>", endpoint="index_team")
def index_team(nombre_nora):
    if not session.get("email") or not session.get("usuario_empresa_id"):
        return redirect("/login")

    session_nora = session.get("nombre_nora")
    if session_nora != nombre_nora:
        return "❌ Acceso denegado para esta Nora", 403

    usuario_id = session.get("usuario_empresa_id")

    # 🔍 Obtener datos del usuario (incluye modulos)
    empleado = supabase.table("usuarios_clientes").select("nombre, modulos").eq("id", usuario_id).single().execute().data
    nombre_usuario = empleado.get("nombre", "Miembro del equipo")
    modulos_personales = empleado.get("modulos")

    # 🔁 Si no hay módulos personalizados, usar los globales de la Nora
    if not modulos_personales:
        config = supabase.table("configuracion_bot").select("modulos").eq("nombre_nora", nombre_nora).execute().data
        modulos_personales = config[0].get("modulos", []) if config else []

    return render_template("panel_team/index.html", modulos=modulos_personales, nombre_nora=nombre_nora, nombre_usuario=nombre_usuario)