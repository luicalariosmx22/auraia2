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
    print(f"🔍 Cargando dashboard para Nora: {nombre_nora}")
    datos = {
        "nombre_nora": nombre_nora,
        "config": {},
        "contactos": [],
        "respuestas": [],
        "tickets": []
    }

    # Cargar configuración desde Supabase
    try:
        print("🔍 Cargando configuración desde la tabla 'configuracion_bot'...")
        response = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()
        if not response.data:
            print(f"⚠️ No se encontró configuración para {nombre_nora}.")
        else:
            datos["config"] = response.data[0]
            print(f"✅ Configuración cargada: {datos['config']}")
    except Exception as e:
        print(f"❌ Error al cargar configuración: {str(e)}")

    # Cargar contactos desde Supabase
    try:
        print("🔍 Cargando contactos desde la tabla 'contactos'...")
        response = supabase.table("contactos").select("*").eq("nombre_nora", nombre_nora).execute()
        if not response.data:
            print(f"⚠️ No se encontraron contactos para {nombre_nora}.")
        else:
            datos["contactos"] = response.data
            print(f"✅ Contactos cargados: {len(datos['contactos'])}")
    except Exception as e:
        print(f"❌ Error al cargar contactos: {str(e)}")

    # Cargar respuestas desde Supabase
    try:
        print("🔍 Cargando respuestas desde la tabla 'respuestas_bot'...")
        response = supabase.table("respuestas_bot").select("*").eq("nombre_nora", nombre_nora).execute()
        if not response.data:
            print(f"⚠️ No se encontraron respuestas para {nombre_nora}.")
        else:
            datos["respuestas"] = response.data
            print(f"✅ Respuestas cargadas: {len(datos['respuestas'])}")
    except Exception as e:
        print(f"❌ Error al cargar respuestas: {str(e)}")

    # Cargar tickets desde Supabase
    try:
        print("🔍 Cargando tickets desde la tabla 'tickets'...")
        response = supabase.table("tickets").select("*").eq("nombre_nora", nombre_nora).execute()
        if not response.data:
            print(f"⚠️ No se encontraron tickets para {nombre_nora}.")
        else:
            datos["tickets"] = response.data
            print(f"✅ Tickets cargados: {len(datos['tickets'])}")
    except Exception as e:
        print(f"❌ Error al cargar tickets: {str(e)}")

    # Calcular métricas
    total_contactos = len(datos["contactos"])
    sin_ia = len([c for c in datos["contactos"] if not c.get("ia", True)])
    sin_etiquetas = len([c for c in datos["contactos"] if not c.get("etiquetas")])
    respuestas_claves = [r.get("keyword") for r in datos["respuestas"] if isinstance(r, dict) and "keyword" in r]

    print(f"✅ Métricas calculadas: Total contactos: {total_contactos}, Sin IA: {sin_ia}, Sin etiquetas: {sin_etiquetas}, Total respuestas: {len(datos['respuestas'])}")

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
    print(f"🔍 Resolviendo ticket {ticket_id} para Nora: {nombre_nora}")
    try:
        response = supabase.table("tickets").update({"estado": "resuelto", "resuelto_en": datetime.now().isoformat()}).eq("id", ticket_id).execute()
        if not response.data:
            print(f"⚠️ No se pudo resolver el ticket {ticket_id}.")
        else:
            print(f"✅ Ticket {ticket_id} resuelto correctamente.")
    except Exception as e:
        print(f"❌ Error al resolver ticket {ticket_id}: {str(e)}")

    return redirect(url_for("admin_nora_dashboard.dashboard_nora", nombre_nora=nombre_nora))
