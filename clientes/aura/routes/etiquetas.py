from flask import Blueprint, render_template, request, redirect, url_for, flash
from supabase import create_client
from dotenv import load_dotenv
from utils.config import login_requerido
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

etiquetas_bp = Blueprint("etiquetas", __name__)

# Mostrar etiquetas
@etiquetas_bp.route("/etiquetas")
@login_requerido
def mostrar_etiquetas():
    try:
        response = supabase.table("etiquetas").select("*").execute()
        if response.error:
            print(f"❌ Error al cargar etiquetas: {response.error}")
            etiquetas = []
        else:
            etiquetas = [e["nombre"] for e in response.data]
    except Exception as e:
        print(f"❌ Error al cargar etiquetas: {str(e)}")
        etiquetas = []

    return render_template("etiquetas.html", etiquetas=etiquetas)

# Agregar nueva etiqueta
@etiquetas_bp.route("/etiquetas/agregar", methods=["POST"])
@login_requerido
def agregar_etiqueta():
    nueva = request.form.get("etiqueta", "").strip()
    if not nueva:
        flash("Etiqueta no puede estar vacía", "danger")
        return redirect(url_for("etiquetas.mostrar_etiquetas"))

    try:
        # Verificar si la etiqueta ya existe
        response = supabase.table("etiquetas").select("*").eq("nombre", nueva).execute()
        if response.data:
            flash("Esa etiqueta ya existe", "warning")
            return redirect(url_for("etiquetas.mostrar_etiquetas"))

        # Insertar nueva etiqueta
        response = supabase.table("etiquetas").insert({"nombre": nueva}).execute()
        if response.error:
            print(f"❌ Error al agregar etiqueta: {response.error}")
            flash("Error al agregar etiqueta", "danger")
        else:
            flash("Etiqueta agregada correctamente", "success")
    except Exception as e:
        print(f"❌ Error al agregar etiqueta: {str(e)}")
        flash("Error al agregar etiqueta", "danger")

    return redirect(url_for("etiquetas.mostrar_etiquetas"))

# Editar etiqueta
@etiquetas_bp.route("/etiquetas/editar/<nombre>", methods=["GET", "POST"])
@login_requerido
def editar_etiqueta(nombre):
    if request.method == "POST":
        nueva = request.form.get("nueva_etiqueta", "").strip()
        if not nueva:
            flash("Etiqueta nueva no puede estar vacía", "danger")
            return redirect(url_for("etiquetas.mostrar_etiquetas"))

        try:
            # Verificar si la nueva etiqueta ya existe
            response = supabase.table("etiquetas").select("*").eq("nombre", nueva).execute()
            if response.data and nueva != nombre:
                flash("Ya existe otra etiqueta con ese nombre", "warning")
                return redirect(url_for("etiquetas.mostrar_etiquetas"))

            # Actualizar etiqueta
            response = supabase.table("etiquetas").update({"nombre": nueva}).eq("nombre", nombre).execute()
            if response.error:
                print(f"❌ Error al editar etiqueta: {response.error}")
                flash("Error al editar etiqueta", "danger")
            else:
                flash("Etiqueta editada correctamente", "success")
        except Exception as e:
            print(f"❌ Error al editar etiqueta: {str(e)}")
            flash("Error al editar etiqueta", "danger")

        return redirect(url_for("etiquetas.mostrar_etiquetas"))

    return render_template("editar_etiqueta.html", nombre=nombre)

# Eliminar etiqueta
@etiquetas_bp.route("/etiquetas/eliminar/<nombre>", methods=["POST"])
@login_requerido
def eliminar_etiqueta(nombre):
    try:
        response = supabase.table("etiquetas").delete().eq("nombre", nombre).execute()
        if response.error:
            print(f"❌ Error al eliminar etiqueta: {response.error}")
            flash("Error al eliminar etiqueta", "danger")
        else:
            flash("Etiqueta eliminada correctamente", "success")
    except Exception as e:
        print(f"❌ Error al eliminar etiqueta: {str(e)}")
        flash("Error al eliminar etiqueta", "danger")

    return redirect(url_for("etiquetas.mostrar_etiquetas"))
