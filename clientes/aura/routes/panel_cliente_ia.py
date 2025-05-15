print("✅ panel_cliente_ia.py cargado correctamente")

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

panel_cliente_ia_bp = Blueprint("panel_cliente_ia", __name__)

@panel_cliente_ia_bp.route("/", methods=["GET", "POST"])
def panel_ia():
    if not session.get("email"):
        return redirect(url_for("login.login"))
    nombre_nora = request.path.split("/")[3]
    resultados = supabase.table("ia_ajustes").select("*").eq("nombre_nora", nombre_nora).execute()
    ajustes = resultados.data[0] if resultados.data else {}
    return render_template("panel_cliente_ia.html", ajustes=ajustes, nombre_nora=nombre_nora, user={"name": session.get("name", "Usuario")})


@panel_cliente_ia_bp.route("/editar_conocimiento/<id>", methods=["POST"])
def editar_conocimiento(id):
    nombre_nora = request.path.split("/")[3]
    nuevo_texto = request.form.get("nuevo_texto", "")
    supabase.table("ia_conocimiento").update({"texto": nuevo_texto}).eq("id", id).eq("nombre_nora", nombre_nora).execute()
    flash("Conocimiento actualizado", "success")
    return redirect(url_for("panel_cliente_ia.panel_ia"))


@panel_cliente_ia_bp.route("/borrar_conocimiento/<id>")
def borrar_conocimiento(id):
    nombre_nora = request.path.split("/")[3]
    supabase.table("ia_conocimiento").delete().eq("id", id).eq("nombre_nora", nombre_nora).execute()
    flash("Conocimiento eliminado", "success")
    return redirect(url_for("panel_cliente_ia.panel_ia"))
