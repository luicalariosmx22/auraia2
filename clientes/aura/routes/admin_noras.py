print("✅ admin_noras.py cargado correctamente")

from flask import Blueprint, render_template, redirect, url_for, jsonify
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

# Validar que las rutas estén correctamente registradas
for rule in admin_noras_bp.url_map.iter_rules():
    print(f"Ruta registrada: {rule.rule} - Métodos: {rule.methods}")

@admin_noras_bp.route("/admin/noras")
def vista_admin():
    lista_noras = []

    # Consultar todas las Noras desde Supabase
    try:
        response = supabase.table("configuracion_bot").select("*").execute()
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
                "nombre": nombre,
                "ia_activada": ia_activada,
                "modulos": modulos,
                "ultima_actualizacion": ultima_actualizacion,
                "tickets_pendientes": pendientes
            })

    except Exception as e:
        print(f"❌ Error al procesar Noras: {str(e)}")

    # ✅ Agregar Noras falsas para vista previa
    lista_noras.append({
        "nombre": "noraai",
        "ia_activada": True,
        "modulos": ["contactos", "respuestas", "ia"],
        "ultima_actualizacion": datetime.now().isoformat(),
        "tickets_pendientes": 0
    })

    lista_noras.append({
        "nombre": "dani20",
        "ia_activada": False,
        "modulos": ["diseño_personalizado"],
        "ultima_actualizacion": datetime.now().isoformat(),
        "tickets_pendientes": 0
    })

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
