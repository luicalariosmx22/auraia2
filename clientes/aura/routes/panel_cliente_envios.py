print("✅ panel_cliente_envios.py cargado correctamente")

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

panel_cliente_envios_bp = Blueprint("panel_cliente_envios", __name__)

@panel_cliente_envios_bp.route("/panel/cliente/<nombre_nora>/envios", methods=["GET", "POST"])
def panel_envios(nombre_nora):
    if not session.get("email"):
        return redirect(url_for("login.login"))

    try:
        # Obtener envíos programados desde Supabase
        response = supabase.table("envios_programados").select("*").eq("nombre_nora", nombre_nora).execute()
        if not response.data:
            print(f"❌ Error al cargar envíos programados: {not response.data}")
            envios = []
        else:
            envios = response.data
    except Exception as e:
        print(f"❌ Error al cargar envíos programados: {str(e)}")
        envios = []

    if request.method == "POST":
        nuevo_envio = {
            "mensaje": request.form.get("mensaje"),
            "fecha": request.form.get("fecha"),
            "hora": request.form.get("hora"),
            "nombre_nora": nombre_nora,
            "creado_por": session.get("user", {}).get("email", "admin")
        }

        try:
            # Insertar nuevo envío en Supabase
            response = supabase.table("envios_programados").insert(nuevo_envio).execute()
            if not response.data:
                print(f"❌ Error al programar envío: {not response.data}")
                return jsonify({"success": False, "error": "Error al programar envío"}), 500
        except Exception as e:
            print(f"❌ Error al programar envío: {str(e)}")
            return jsonify({"success": False, "error": "Error al programar envío"}), 500

        return redirect(url_for("panel_cliente_envios.panel_envios", nombre_nora=nombre_nora))

    return render_template(
        "panel_cliente_envios.html",
        envios=envios,
        nombre_nora=nombre_nora,
        user={"name": session.get("name", "Usuario")}
    )

@panel_cliente_envios_bp.route("/", methods=["GET", "POST"])
def panel_envios():
    if not session.get("email"):
        return redirect(url_for("login.login"))
    nombre_nora = request.path.split("/")[3]
    resultados = supabase.table("envios_programados").select("*").eq("nombre_nora", nombre_nora).order("fecha_envio", desc=True).execute()
    envios = resultados.data if resultados.data else []
    return render_template("panel_cliente_envios.html", envios=envios, nombre_nora=nombre_nora, user={"name": session.get("name", "Usuario")})
