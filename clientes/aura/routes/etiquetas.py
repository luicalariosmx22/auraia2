from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from supabase import create_client
from dotenv import load_dotenv
from clientes.aura.utils.config import login_requerido
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

etiquetas_bp = Blueprint("panel_cliente_etiquetas", __name__)

@etiquetas_bp.route("/<nombre_nora>/etiquetas", methods=["GET", "POST"])
def panel_etiquetas(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    # Depuración: Verificar el valor de nombre_nora
    print(f"🔍 nombre_nora recibido: {nombre_nora}")

    # Obtener etiquetas desde la base de datos
    try:
        response = supabase.table("etiquetas").select("id, nombre, color").eq("nombre_nora", nombre_nora).eq("activa", True).execute()
        print(f"🔍 Respuesta de la base de datos: {response.data}")  # Depuración: Verificar la respuesta
        etiquetas = response.data or []
    except Exception as e:
        print(f"❌ Error al cargar etiquetas: {str(e)}")
        etiquetas = []

    # Depuración: Verificar las etiquetas obtenidas
    print(f"🔍 Etiquetas obtenidas: {etiquetas}")

    if request.method == "POST":
        nueva_etiqueta = request.form.get("nueva_etiqueta", "").strip()
        print(f"🔍 Nueva etiqueta recibida: {nueva_etiqueta}")  # Depuración: Verificar el valor del formulario
        if nueva_etiqueta:
            try:
                supabase.table("etiquetas").insert({"nombre_nora": nombre_nora, "nombre": nueva_etiqueta}).execute()
                flash(f"Etiqueta '{nueva_etiqueta}' agregada correctamente.", "success")
            except Exception as e:
                print(f"❌ Error al agregar etiqueta: {str(e)}")
                flash("Error al agregar la etiqueta.", "error")
        else:
            flash("El nombre de la etiqueta no puede estar vacío.", "error")

        return redirect(url_for("panel_cliente_etiquetas.panel_etiquetas", nombre_nora=nombre_nora))

    return render_template(
        "panel_cliente_etiquetas.html",
        nombre_nora=nombre_nora,
        etiquetas=etiquetas
    )
