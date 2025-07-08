# clientes/aura/routes/panel_chat/vista_gestion_etiqueta.py

from flask import Blueprint, request, jsonify
from clientes.aura.utils.normalizador import normalizar_numero
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

vista_gestion_etiqueta_bp = Blueprint("vista_gestion_etiqueta", __name__)

@vista_gestion_etiqueta_bp.route("/api/etiqueta/<telefono>", methods=["POST", "DELETE"])
def api_gestion_etiqueta(telefono):
    try:
        body = request.get_json()
        etiqueta = body.get("etiqueta", "").strip().lower()
        telefono = normalizar_numero(telefono)

        # Buscar el contacto en la base de datos
        response = supabase.table("contactos").select("*").eq("telefono", telefono).execute()
        if not response.data:
            return jsonify({"success": False, "error": "Contacto no encontrado"}), 404

        contacto = response.data[0]
        etiquetas = set(contacto.get("etiquetas", []))

        # Agregar o eliminar la etiqueta según el método HTTP
        if request.method == "POST":
            etiquetas.add(etiqueta)
        elif request.method == "DELETE":
            etiquetas.discard(etiqueta)

        # Actualizar las etiquetas en la base de datos
        supabase.table("contactos").update({"etiquetas": list(etiquetas)}).eq("telefono", telefono).execute()
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error en la gestión de etiquetas para {telefono}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
