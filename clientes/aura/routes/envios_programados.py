from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

envios_programados_bp = Blueprint("envios_programados", __name__)

@envios_programados_bp.route("/panel/envios-programados")
@envios_programados_bp.route("/panel/envios-programados/<estado>")
def vista_envios(estado=None):
    return render_template("panel_envios_programados.html", estado=estado)

@envios_programados_bp.route("/api/contactos")
def api_contactos():
    try:
        response = supabase.table("contactos").select("*").execute()
        if not response.data:
            print(f"❌ Error al cargar contactos: {not response.data}")
            return jsonify({"error": "Error al cargar contactos"}), 500
        return jsonify(response.data)
    except Exception as e:
        print(f"❌ Error al cargar contactos: {str(e)}")
        return jsonify({"error": "Error al cargar contactos"}), 500

@envios_programados_bp.route("/api/envios-programados")
def api_envios_programados():
    estado_filtro = request.args.get("estado")
    try:
        query = supabase.table("envios_programados").select("*")
        if estado_filtro:
            query = query.eq("estado", estado_filtro)
        response = query.execute()
        if not response.data:
            print(f"❌ Error al cargar envíos programados: {not response.data}")
            return jsonify({"error": "Error al cargar envíos programados"}), 500
        return jsonify(response.data)
    except Exception as e:
        print(f"❌ Error al cargar envíos programados: {str(e)}")
        return jsonify({"error": "Error al cargar envíos programados"}), 500

@envios_programados_bp.route("/api/programar-envio-masivo", methods=["POST"])
def programar_envio_masivo():
    data = request.json
    mensaje = data.get("mensaje")
    fecha = data.get("fecha")
    hora = data.get("hora")
    destinatarios = data.get("destinatarios", [])

    errores = []
    if not mensaje:
        errores.append("Falta el mensaje.")
    if not fecha:
        errores.append("Falta la fecha.")
    if not hora:
        errores.append("Falta la hora.")
    if not destinatarios:
        errores.append("No se seleccionaron destinatarios.")

    if errores:
        return jsonify({"error": "Datos incompletos", "detalles": errores}), 400

    programado_por = session.get("user", {}).get("email", "admin")

    registros = [
        {
            "numero": numero,
            "mensaje": mensaje,
            "fecha": fecha,
            "hora": hora,
            "programado_por": programado_por,
            "estado": "pendiente",
            "creado_en": datetime.now().isoformat()
        }
        for numero in destinatarios
    ]

    try:
        response = supabase.table("envios_programados").insert(registros).execute()
        if not response.data:
            print(f"❌ Error al programar envíos: {not response.data}")
            return jsonify({"error": "Error al programar envíos"}), 500
        return jsonify({"ok": True})
    except Exception as e:
        print(f"❌ Error al programar envíos: {str(e)}")
        return jsonify({"error": "Error al programar envíos"}), 500

@envios_programados_bp.route("/api/cancelar-envio", methods=["POST"])
def cancelar_envio():
    data = request.json
    numero = data.get("numero")
    fecha = data.get("fecha")
    hora = data.get("hora")

    if not all([numero, fecha, hora]):
        return jsonify({"error": "Faltan datos para cancelar el envío."}), 400

    try:
        response = supabase.table("envios_programados").delete().match({
            "numero": numero,
            "fecha": fecha,
            "hora": hora
        }).execute()
        if not response.data:
            print(f"❌ Error al cancelar envío: {not response.data}")
            return jsonify({"error": "Error al cancelar envío"}), 500
        return jsonify({"ok": True})
    except Exception as e:
        print(f"❌ Error al cancelar envío: {str(e)}")
        return jsonify({"error": "Error al cancelar envío"}), 500
