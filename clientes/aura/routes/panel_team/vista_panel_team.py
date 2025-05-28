from flask import Blueprint, render_template, session, redirect
from supabase import create_client, Client

# ...existing code...

@panel_team_bp.route("/panel_team/<nombre_nora>")
def index_team(nombre_nora):
    if not session.get("email") or not session.get("usuario_empresa_id"):
        return redirect("/login")

    session_nora = session.get("nombre_nora")
    if session_nora != nombre_nora:
        return "❌ Acceso denegado para esta Nora", 403

    config = supabase.table("configuracion_bot").select("modulos").eq("nombre_nora", nombre_nora).execute().data

    if not config:
        return "❌ Nora no encontrada", 404

    modulos = config[0].get("modulos", [])
    nombre_usuario = session.get("name", "Miembro del equipo")

    return render_template("panel_team/index.html", modulos=modulos, nombre_nora=nombre_nora, nombre_usuario=nombre_usuario)