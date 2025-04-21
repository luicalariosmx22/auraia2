print("✅ admin_noras.py cargado correctamente")

from flask import Blueprint, render_template, redirect, url_for, jsonify, request, current_app
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

admin_noras_bp = Blueprint("admin_noras", __name__)

@admin_noras_bp.route("/admin/noras")
def vista_admin():
    lista_noras = []

    # Consultar todas las Noras desde Supabase
    try:
        response = supabase.table("configuracion_bot").select("*").execute()
        print(f"Respuesta de Supabase: {response.data}")
        if not response or not response.data:
            print(f"❌ No se encontraron Noras en la tabla configuracion_bot.")
            return render_template("admin_noras.html", noras=lista_noras)

        configuraciones = response.data

        # Consultar tickets pendientes desde Supabase
        tickets_response = supabase.table("tickets").select("*").eq("estado", "pendiente").execute()
        tickets_pendientes = tickets_response.data if tickets_response and tickets_response.data else []

        # Procesar cada Nora
        for config in configuraciones:
            nombre = config.get("nombre_nora", "Desconocido")
            ia_activada = config.get("ia_activada", False)
            modulos = config.get("modulos", [])
            ultima_actualizacion = config.get("ultima_actualizacion", datetime.now().isoformat())

            # Contar tickets pendientes para esta Nora
            pendientes = len([t for t in tickets_pendientes if t.get("nombre_nora") == nombre])

            lista_noras.append({
                "nombre": nombre,  # Este es el nombre_nora
                "ia_activada": ia_activada,
                "modulos": modulos,
                "ultima_actualizacion": ultima_actualizacion,
                "tickets_pendientes": pendientes
            })

    except Exception as e:
        print(f"❌ Error al procesar Noras: {str(e)}")

    return render_template("admin_noras.html", noras=lista_noras)


@admin_noras_bp.route("/admin")
def redireccionar_a_noras():
    return redirect(url_for("admin_noras.vista_admin"))


@admin_noras_bp.route("/debug_info", methods=["GET"])
def debug_info():
    try:
        rutas = [rule.rule for rule in admin_noras_bp.url_map.iter_rules()]
        return jsonify({"rutas_registradas": rutas, "estado": "OK"})
    except Exception as e:
        return jsonify({"error": str(e), "estado": "ERROR"})


@admin_noras_bp.route("/admin/debug/rutas", methods=["GET"])
def debug_rutas():
    """
    Devuelve todas las rutas registradas en la aplicación Flask.
    """
    rutas = []
    for rule in current_app.url_map.iter_rules():
        rutas.append({
            "ruta": rule.rule,
            "endpoint": rule.endpoint,
            "metodos": list(rule.methods)
        })
    return jsonify(rutas)


@admin_noras_bp.route("/editar_nora", methods=["GET"])
def editar_nora():
    nombre = request.args.get("nombre")
    # Aquí puedes agregar lógica para obtener los detalles de la Nora y renderizar un formulario de edición
    return render_template("editar_nora.html", nombre=nombre)


@admin_noras_bp.route("/borrar_nora", methods=["POST"])
def borrar_nora():
    data = request.get_json()
    nombre = data.get("nombre")
    try:
        # Aquí puedes agregar lógica para borrar la Nora de la base de datos
        print(f"Nora borrada: {nombre}")
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error al borrar la Nora: {str(e)}")
        return jsonify({"success": False, "error": str(e)})
