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
        print("⚠️ Usuario no autenticado. Redirigiendo al login.")
        return redirect(url_for("login.login_google"))

    ia_permitida = False
    contactos = []

    # Verificar si el módulo de IA está habilitado
    try:
        print(f"🔍 Verificando módulos habilitados para {nombre_nora}...")
        response = supabase.table("configuracion_bot").select("modulos").eq("nombre_nora", nombre_nora).execute()
        if not response.data:
            print(f"⚠️ No se encontró configuración para {nombre_nora}.")
        else:
            modulos = response.data[0].get("modulos", [])
            ia_permitida = "ia" in modulos
            print(f"✅ Módulos habilitados: {modulos}")
    except Exception as e:
        print(f"❌ Error al cargar configuración: {str(e)}")

    # Cargar contactos desde Supabase
    try:
        print(f"🔍 Cargando contactos para {nombre_nora}...")
        busqueda = request.args.get("busqueda", "").strip().lower()
        fecha_inicio = request.args.get("fecha_inicio", None)
        fecha_fin = request.args.get("fecha_fin", None)
        etiqueta = request.args.get("etiqueta", "").strip()

        # Imprimir los parámetros recibidos
        print(f"📩 Parámetros recibidos: busqueda={busqueda}, fecha_inicio={fecha_inicio}, fecha_fin={fecha_fin}, etiqueta={etiqueta}")

        # Construir la consulta base
        query = supabase.table("contactos").select("*").eq("nombre_nora", nombre_nora)

        # Filtro por nombre o teléfono
        if busqueda:
            query = query.or_("nombre.ilike.*{0}*,telefono.ilike.*{0}*".format(busqueda))

        # Filtro por rango de fechas
        if fecha_inicio:
            query = query.gte("ultimo_mensaje", fecha_inicio)
        if fecha_fin:
            query = query.lte("ultimo_mensaje", fecha_fin)

        # Filtro por etiqueta
        if etiqueta:
            query = query.contains("etiquetas", [etiqueta])

        # Ejecutar la consulta
        response = query.execute()
        if not response.data:
            print(f"⚠️ No se encontraron contactos para {nombre_nora}.")
        else:
            contactos = response.data
            print(f"✅ Contactos cargados: {len(contactos)}")
    except Exception as e:
        print(f"❌ Error al cargar contactos: {str(e)}")

    return render_template(
        "panel_cliente_contactos.html",
        user=session["user"],
        contactos=contactos,
        nombre_nora=nombre_nora,
        ia_permitida=ia_permitida
    )
print("✅ Blueprint de contactos cargado como '/contactos'")
