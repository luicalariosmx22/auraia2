# clientes/aura/routes/panel_chat/vista_programar_envio.py
from flask import Blueprint, request, jsonify
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

vista_programar_envio_bp = Blueprint("vista_programar_envio", __name__)

@vista_programar_envio_bp.route("/api/programar-envio", methods=["POST"])
def api_programar_envio():
    try:
        data = request.json
        numero = data.get("numero")
        mensaje = data.get("mensaje")
        fecha = data.get("fecha")
        hora = data.get("hora")

        if not all([numero, mensaje, fecha, hora]):
            return jsonify({"success": False, "error": "Faltan datos"}), 400

        response = supabase.table("envios_programados").insert({
            "numero": numero,
            "mensaje": mensaje,
            "fecha": fecha,
            "hora": hora
        }).execute()

        if not response.data:
            return jsonify({"success": False, "error": "No se pudo guardar"}), 500

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
