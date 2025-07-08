# clientes/aura/routes/panel_chat/vista_toggle_ia.py
from flask import Blueprint, request, jsonify
from clientes.aura.utils.normalizador import normalizar_numero
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

vista_toggle_ia_bp = Blueprint("vista_toggle_ia", __name__)

@vista_toggle_ia_bp.route("/api/toggle-ia/<telefono>", methods=["POST"])
def api_toggle_ia(telefono):
    telefono = normalizar_numero(telefono)
    try:
        response = supabase.table("contactos").select("*").eq("telefono", telefono).execute()
        if not response.data:
            return jsonify({"success": False, "error": "Contacto no encontrado"}), 404

        contacto = response.data[0]
        nuevo_estado = not contacto.get("ia_activada", True)

        supabase.table("contactos").update({"ia_activada": nuevo_estado}).eq("telefono", telefono).execute()

        return jsonify({"success": True, "nuevo_estado": nuevo_estado})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
