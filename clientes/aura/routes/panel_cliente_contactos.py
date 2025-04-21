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

@panel_cliente_contactos_bp.route("/<nombre_nora>/agregar", methods=["POST"])
def agregar_contacto(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    try:
        # Agregar contacto a Supabase
        data = {
            "nombre_nora": nombre_nora,
            "telefono": request.form.get("telefono"),
            "nombre": request.form.get("nombre"),
            "correo": request.form.get("correo"),
            "celular": request.form.get("celular"),
            "etiquetas": [request.form.get("etiqueta")] if request.form.get("etiqueta") else []
        }
        supabase.table("contactos").insert(data).execute()
        print(f"✅ Contacto agregado: {data}")
    except Exception as e:
        print(f"❌ Error al agregar contacto: {str(e)}")
    return redirect(url_for("panel_cliente_contactos.panel_contactos", nombre_nora=nombre_nora))

@panel_cliente_contactos_bp.route("/<nombre_nora>/acciones", methods=["POST"])
def acciones_contactos(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    try:
        accion = request.form.get("accion")
        contactos_seleccionados = request.form.getlist("contactos_seleccionados")

        if accion == "eliminar":
            for telefono in contactos_seleccionados:
                supabase.table("contactos").delete().eq("nombre_nora", nombre_nora).eq("telefono", telefono).execute()
            print(f"✅ Contactos eliminados: {contactos_seleccionados}")
        elif accion == "editar":
            # Redirigir a la página de edición del primer contacto seleccionado
            if contactos_seleccionados:
                return redirect(url_for("panel_cliente_contactos.editar_contacto", nombre_nora=nombre_nora, telefono=contactos_seleccionados[0]))
    except Exception as e:
        print(f"❌ Error al realizar acción en contactos: {str(e)}")
    return redirect(url_for("panel_cliente_contactos.panel_contactos", nombre_nora=nombre_nora))

@panel_cliente_contactos_bp.route("/<nombre_nora>/editar/<telefono>", methods=["GET", "POST"])
def editar_contacto(nombre_nora, telefono):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    if request.method == "POST":
        try:
            # Actualizar contacto en Supabase
            data = {
                "nombre": request.form.get("nombre"),
                "correo": request.form.get("correo"),
                "celular": request.form.get("celular"),
                "etiquetas": [request.form.get("etiqueta")] if request.form.get("etiqueta") else []
            }
            supabase.table("contactos").update(data).eq("nombre_nora", nombre_nora).eq("telefono", telefono).execute()
            print(f"✅ Contacto actualizado: {data}")
        except Exception as e:
            print(f"❌ Error al actualizar contacto: {str(e)}")
        return redirect(url_for("panel_cliente_contactos.panel_contactos", nombre_nora=nombre_nora))

    try:
        # Obtener contacto desde Supabase
        response = supabase.table("contactos").select("*").eq("nombre_nora", nombre_nora).eq("telefono", telefono).execute()
        contacto = response.data[0] if response.data else {}
        return render_template(
            "editar_contacto.html",
            nombre_nora=nombre_nora,
            contacto=contacto,
            user=session["user"]
        )
    except Exception as e:
        print(f"❌ Error al cargar contacto para edición: {str(e)}")
        return redirect(url_for("panel_cliente_contactos.panel_contactos", nombre_nora=nombre_nora))

print("✅ Blueprint de contactos cargado como '/contactos'")
