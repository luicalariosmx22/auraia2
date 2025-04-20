from flask import Blueprint, render_template
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

admin_debug_rutas_bp = Blueprint("admin_debug_rutas", __name__)

@admin_debug_rutas_bp.route("/admin/debug/rutas")
def ver_rutas_registradas():
    try:
        response = supabase.table("rutas_registradas").select("*").order("registrado_en", desc=True).execute()
        rutas = response.data if response.data else []
        return render_template("admin_debug_rutas.html", rutas=rutas)
    except Exception as e:
        return f"<h3>❌ Error al obtener rutas: {e}</h3>"
