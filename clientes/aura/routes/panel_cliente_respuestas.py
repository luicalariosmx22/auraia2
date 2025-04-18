print("✅ panel_cliente_respuestas.py cargado correctamente")

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

panel_cliente_respuestas_bp = Blueprint("panel_cliente_respuestas", __name__)

@panel_cliente_respuestas_bp.route("/panel_cliente/respuestas/<nombre_nora>", methods=["GET", "POST"])
def panel_respuestas(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    if request.method == "POST":
        palabra_clave = request.form.get("palabra_clave", "").strip().lower()
        respuesta = request.form.get("respuesta", "").strip()
        index = request.form.get("index")

        if not palabra_clave or not respuesta:
            flash("❌ Completa ambos campos", "error")
            return redirect(request.url)

        try:
            if index:
                # Actualizar respuesta existente
                idx = int(index)
                response = supabase.table("bot_data").update({
                    "keyword": palabra_clave,
                    "respuesta": respuesta
                }).eq("id", idx).execute()
                if response.error:
                    flash("❌ No se pudo editar", "error")
                else:
                    flash("✅ Respuesta actualizada", "success")
            else:
                # Agregar nueva respuesta
                response = supabase.table("bot_data").insert({
                    "nombre_nora": nombre_nora,
                    "keyword": palabra_clave,
                    "respuesta": respuesta
                }).execute()
                if response.error:
                    flash("❌ No se pudo agregar la respuesta", "error")
                else:
                    flash("✅ Respuesta agregada", "success")
        except Exception as e:
            print(f"❌ Error al guardar respuesta: {str(e)}")
            flash("❌ Error al guardar respuesta", "error")

        return redirect(url_for("panel_cliente_respuestas.panel_respuestas", nombre_nora=nombre_nora))

    eliminar = request.args.get("eliminar")
    if eliminar is not None:
        try:
            idx = int(eliminar)
            response = supabase.table("bot_data").delete().eq("id", idx).execute()
            if response.error:
                flash("❌ No se pudo eliminar", "error")
            else:
                flash("✅ Respuesta eliminada", "success")
        except Exception as e:
            print(f"❌ Error al eliminar respuesta: {str(e)}")
            flash("❌ Error al eliminar respuesta", "error")
        return redirect(url_for("panel_cliente_respuestas.panel_respuestas", nombre_nora=nombre_nora))

    try:
        # Cargar respuestas desde Supabase
        response = supabase.table("bot_data").select("*").eq("nombre_nora", nombre_nora).execute()
        if response.error:
            print(f"❌ Error al cargar respuestas: {response.error}")
            respuestas = []
        else:
            respuestas = response.data
    except Exception as e:
        print(f"❌ Error al cargar respuestas: {str(e)}")
        respuestas = []

    return render_template(
        "panel_cliente_respuestas.html",
        nombre_nora=nombre_nora,
        respuestas=respuestas,
        user=session["user"]
    )
