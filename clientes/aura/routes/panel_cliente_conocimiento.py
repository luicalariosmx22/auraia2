# 📁 clientes/aura/routes/panel_cliente_conocimiento.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

panel_cliente_conocimiento_bp = Blueprint("panel_cliente_conocimiento", __name__)

@panel_cliente_conocimiento_bp.route("/", methods=["GET", "POST"])
def conocimiento_nora():
    if "user" not in session:
        return redirect(url_for("login.login"))
    nombre_nora = request.path.split("/")[3]
    bloques_data = supabase.table("conocimiento").select("*").eq("nombre_nora", nombre_nora).order("fecha", desc=True).execute()
    bloques = bloques_data.data if bloques_data.data else []
    return render_template("panel_cliente_conocimiento.html", bloques=bloques, nombre_nora=nombre_nora, user=session["user"])


@panel_cliente_conocimiento_bp.route("/eliminar/<bloque_id>", methods=["POST"])
def eliminar_bloque(bloque_id):
    nombre_nora = request.path.split("/")[3]
    supabase.table("conocimiento").delete().eq("id", bloque_id).eq("nombre_nora", nombre_nora).execute()
    flash("Bloque eliminado", "success")
    return redirect(url_for("panel_cliente_conocimiento_bp.conocimiento_nora"))
