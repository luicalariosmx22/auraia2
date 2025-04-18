print("✅ admin_nora_dashboard.py cargado correctamente")

from flask import Blueprint, render_template, request, redirect, url_for
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

admin_nora_dashboard_bp = Blueprint("admin_nora_dashboard", __name__)

@admin_nora_dashboard_bp.route("/admin/nora/<nombre_nora>/dashboard")
def dashboard_nora(nombre_nora):
    datos = {
        "nombre_nora": nombre_nora,
        "config": {},
        "contactos": [],
        "respuestas": [],
        "tickets": []
    }

    # Cargar configuración desde Supabase
    try:
        response = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()
        if response.error or not response.data:
            print(f"❌ Error al cargar configuración: {response.error}")
        else:
            datos["config"] = response.data[0]
    except Exception as e:
        print(f"❌ Error al cargar configuración: {str(e)}")

    # Cargar contactos desde Supabase
    try:
        response = supabase.table("contactos").select("*").eq("nombre_nora", nombre_nora).execute()
        if response.error or not response.data:
            print(f"❌ Error al cargar contactos: {response.error}")
        else:
            datos["contactos"] = response.data
    except Exception as e:
        print(f"❌ Error al cargar contactos: {str(e)}")

    # Cargar respuestas desde Supabase
    try:
        response = supabase.table("respuestas_bot").select("*").eq("nombre_nora", nombre_nora).execute()
        if response.error or not response.data:
            print(f"❌ Error al cargar respuestas: {response.error}")
        else:
            datos["respuestas"] = response.data
    except Exception as e:
        print(f"❌ Error al cargar respuestas: {str(e)}")

    # Cargar tickets desde Supabase
    try:
        response = supabase.table("tickets").select("*").eq("nombre_nora", nombre_nora).execute()
        if response.error or not response.data:
            print(f"❌ Error al cargar tickets: {response.error}")
        else:
            datos["tickets"] = response.data
    except Exception as e:
        print(f"❌ Error al cargar tickets: {str(e)}")

    # Calcular métricas
    total_contactos = len(datos["contactos"])
    sin_ia = len([c for c in datos["contactos"] if not c.get("ia", True)])
    sin_etiquetas = len([c for c in datos["contactos"] if not c.get("etiquetas")])
    respuestas_claves = [r.get("keyword") for r in datos["respuestas"] if isinstance(r, dict) and "keyword" in r]

    return render_template("admin_nora_dashboard.html",
        nombre_nora=nombre_nora,
        ia_activada=datos["config"].get("ia_activada", False),
        modulos=datos["config"].get("modulos", []),
        total_contactos=total_contactos,
        sin_ia=sin_ia,
        sin_etiquetas=sin_etiquetas,
        total_respuestas=len(datos["respuestas"]),
        respuestas_claves=respuestas_claves,
        tickets=datos["tickets"]
    )

@admin_nora_dashboard_bp.route("/admin/nora/<nombre_nora>/ticket/<ticket_id>/resolver", methods=["POST"])
def resolver_ticket(nombre_nora, ticket_id):
    # Resolver ticket en Supabase
    try:
        response = supabase.table("tickets").update({"estado": "resuelto", "resuelto_en": datetime.now().isoformat()}).eq("id", ticket_id).execute()
        if response.error:
            print(f"❌ Error al resolver ticket: {response.error}")
    except Exception as e:
        print(f"❌ Error al resolver ticket: {str(e)}")

    return redirect(url_for("admin_nora_dashboard.dashboard_nora", nombre_nora=nombre_nora))
