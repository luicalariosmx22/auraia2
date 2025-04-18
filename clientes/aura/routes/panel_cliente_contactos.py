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

@panel_cliente_contactos_bp.route("/panel_cliente/contactos/<nombre_nora>", methods=["GET", "POST"])
def panel_contactos(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    ia_permitida = False
    contactos = []

    # Verificar si el módulo de IA está habilitado
    try:
        response = supabase.table("configuracion_bot").select("modulos").eq("nombre_nora", nombre_nora).execute()
        if not response.data:
            print(f"❌ Error al cargar configuración: {response.error}")
        else:
            modulos = response.data[0].get("modulos", [])
            ia_permitida = "ia" in modulos
    except Exception as e:
        print(f"❌ Error al cargar configuración: {str(e)}")

    # Cargar contactos desde Supabase
    try:
        response = supabase.table("contactos").select("*").eq("nombre_nora", nombre_nora).execute()
        if not response.data:
            print(f"❌ Error al cargar contactos: {response.error}")
        else:
            contactos = response.data
    except Exception as e:
        print(f"❌ Error al cargar contactos: {str(e)}")

    if request.method == "POST":
        nuevo = {
            "nombre": request.form.get("nombre").strip(),
            "telefono": request.form.get("telefono").strip(),
            "etiquetas": [et.strip() for et in request.form.get("etiquetas", "").split(",") if et.strip()],
            "ia": True,
            "nombre_nora": nombre_nora
        }

        # Insertar nuevo contacto en Supabase
        try:
            response = supabase.table("contactos").insert(nuevo).execute()
            if response.error:
                print(f"❌ Error al guardar contacto: {response.error}")
            else:
                print(f"✅ Contacto guardado: {nuevo}")
        except Exception as e:
            print(f"❌ Error al guardar contacto: {str(e)}")

        return redirect(url_for("panel_cliente_contactos.panel_contactos", nombre_nora=nombre_nora))

    return render_template(
        "panel_cliente_contactos.html",
        user=session["user"],
        contactos=contactos,
        nombre_nora=nombre_nora,
        ia_permitida=ia_permitida
    )