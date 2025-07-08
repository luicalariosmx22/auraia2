print("✅ panel_cliente_contactos.py cargado correctamente")

from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from supabase import create_client
from dotenv import load_dotenv
import os
import uuid

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

panel_cliente_contactos_bp = Blueprint("panel_cliente_contactos", __name__)

@panel_cliente_contactos_bp.route("/<nombre_nora>", methods=["GET", "POST"])
def panel_contactos(nombre_nora):
    if not session.get("email"):
        return redirect(url_for("login.login"))

    try:
        # Obtener contactos con los campos necesarios
        response = supabase.table("contactos").select(
            "id, nombre, telefono, correo, empresa, rfc, direccion, ciudad, cumpleanos, notas, ultimo_mensaje"
        ).eq("nombre_nora", nombre_nora).execute()
        contactos = response.data or []

        # Obtener etiquetas disponibles
        etiquetas_response = supabase.table("etiquetas").select("id, nombre, color").eq("nombre_nora", nombre_nora).eq("activa", True).execute()
        etiquetas = etiquetas_response.data or []

        # Obtener relaciones contacto-etiqueta
        relacion_response = supabase.table("contacto_etiquetas").select("contacto_id, etiqueta_id").eq("nombre_nora", nombre_nora).execute()
        relaciones = relacion_response.data or []

        # Asociar etiquetas a contactos
        etiquetas_dict = {e["id"]: e for e in etiquetas}
        etiquetas_por_contacto = {}
        for rel in relaciones:
            contacto_id = rel["contacto_id"]
            etiqueta_id = rel["etiqueta_id"]
            etiquetas_por_contacto.setdefault(contacto_id, []).append(etiquetas_dict.get(etiqueta_id, {}))

        for contacto in contactos:
            contacto["etiquetas"] = etiquetas_por_contacto.get(contacto["id"], [])

        return render_template(
            "panel_cliente_contactos.html",
            nombre_nora=nombre_nora,
            contactos=contactos,
            etiquetas=etiquetas,
            user={"name": session.get("name", "Usuario")}
        )
    except Exception as e:
        print(f"❌ Error al cargar contactos para {nombre_nora}: {str(e)}")
        flash("Error al cargar los contactos. Por favor, inténtalo de nuevo.", "error")
        return render_template(
            "panel_cliente_contactos.html",
            nombre_nora=nombre_nora,
            contactos=[],
            etiquetas=[],
            user={"name": session.get("name", "Usuario")}
        )

@panel_cliente_contactos_bp.route("/<nombre_nora>/contactos/asignar_etiqueta", methods=["POST"])
def asignar_etiqueta(nombre_nora):
    if not session.get("email"):
        return redirect(url_for("login.login"))

    contacto_id = request.form.get("contacto_id")
    etiqueta_id = request.form.get("etiqueta_id")
    try:
        supabase.table("contacto_etiquetas").insert({
            "id": str(uuid.uuid4()),
            "contacto_id": contacto_id,
            "etiqueta_id": etiqueta_id,
            "nombre_nora": nombre_nora
        }).execute()
        flash(f"Etiqueta asignada correctamente al contacto.", "success")
        print(f"✅ Etiqueta {etiqueta_id} asignada a contacto {contacto_id}")
    except Exception as e:
        print(f"❌ Error al asignar etiqueta: {str(e)}")
        flash("Error al asignar la etiqueta. Por favor, inténtalo de nuevo.", "error")
    return redirect(url_for("panel_cliente_contactos.panel_contactos", nombre_nora=nombre_nora))

@panel_cliente_contactos_bp.route("/<nombre_nora>/contactos/quitar_etiqueta", methods=["POST"])
def quitar_etiqueta(nombre_nora):
    if not session.get("email"):
        return redirect(url_for("login.login"))

    contacto_id = request.form.get("contacto_id")
    etiqueta_id = request.form.get("etiqueta_id")
    try:
        supabase.table("contacto_etiquetas").delete().eq("contacto_id", contacto_id).eq("etiqueta_id", etiqueta_id).eq("nombre_nora", nombre_nora).execute()
        flash("Etiqueta eliminada correctamente del contacto.", "success")
        print(f"✅ Etiqueta {etiqueta_id} quitada del contacto {contacto_id}")
    except Exception as e:
        print(f"❌ Error al quitar etiqueta: {str(e)}")
        flash("Error al quitar la etiqueta. Por favor, inténtalo de nuevo.", "error")
    return redirect(url_for("panel_cliente_contactos.panel_contactos", nombre_nora=nombre_nora))

print("✅ Blueprint de contactos cargado como '/contactos'")