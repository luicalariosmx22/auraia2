print("✅ panel_cliente_contactos.py cargado correctamente")

from flask import Blueprint, render_template, session, request, redirect, url_for
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

panel_cliente_contactos_bp = Blueprint("panel_cliente_contactos", __name__)

@panel_cliente_contactos_bp.route("/<nombre_nora>", methods=["GET", "POST"])
def panel_contactos(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    try:
        # Obtener contactos desde Supabase
        response = supabase.table("contactos").select("*").eq("nombre_nora", nombre_nora).execute()
        contactos = response.data if response.data else []

        # Obtener etiquetas únicas
        etiquetas_response = supabase.table("contactos").select("etiquetas").eq("nombre_nora", nombre_nora).execute()
        etiquetas = list(set(et for c in etiquetas_response.data for et in c.get("etiquetas", []) if et)) if etiquetas_response.data else []

        return render_template(
            "panel_cliente_contactos.html",
            nombre_nora=nombre_nora,
            contactos=contactos,
            etiquetas=etiquetas,
            user=session["user"]
        )
    except Exception as e:
        print(f"❌ Error al cargar contactos para {nombre_nora}: {str(e)}")
        return render_template(
            "panel_cliente_contactos.html",
            nombre_nora=nombre_nora,
            contactos=[],
            etiquetas=[],
            user=session["user"]
        )

print("✅ Blueprint de contactos cargado como '/contactos'")
