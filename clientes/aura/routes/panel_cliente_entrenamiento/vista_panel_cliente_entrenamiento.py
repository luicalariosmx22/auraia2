# 👉 Módulo Entrenamiento del cliente para configurar personalidad, respuestas e info

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
from supabase import create_client
import os

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

panel_cliente_entrenamiento_bp = Blueprint("panel_cliente_entrenamiento", __name__)

@panel_cliente_entrenamiento_bp.route("/", methods=["GET", "POST"])
def entrenamiento_cliente():
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    nombre_nora = request.path.split("/")[2]  # ✅ CORREGIDO: estaba en [3]

    response = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()
    config = response.data[0] if response.data else {}

    if not config:
        return f"❌ No se encontró configuración para {nombre_nora}", 404

    if request.method == "POST":
        personalidad = request.form.get("personalidad", "").strip()
        respuestas_rapidas = request.form.get("respuestas_rapidas", "").strip()
        informacion_empresa = request.form.get("informacion_empresa", "").strip()

        try:
            config["personalidad"] = personalidad
            config["respuestas_rapidas"] = [r.strip() for r in respuestas_rapidas.split(",") if r.strip()]
            config["informacion_empresa"] = informacion_empresa

            supabase.table("configuracion_bot").update(config).eq("nombre_nora", nombre_nora).execute()
            flash("✅ Entrenamiento guardado correctamente", "success")
        except Exception as e:
            print(f"❌ Error al guardar entrenamiento: {str(e)}")
            flash("❌ Error al guardar datos", "error")

    return render_template("admin_nora_entrenar.html", nombre_nora=nombre_nora, config=config)