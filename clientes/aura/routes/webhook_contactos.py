from flask import Blueprint, request, jsonify
from clientes.aura.utils.supabase_client import supabase
from datetime import datetime
import pytz

webhook_contactos_bp = Blueprint("webhook_contactos", __name__)

@webhook_contactos_bp.route("/webhook/nora", methods=["POST"])
def webhook_contactos():
    data = request.get_json()
    nombre_nora = data.get("nombre_nora")
    numero = data.get("numero")
    timestamp = data.get("timestamp")

    if not nombre_nora or not numero or not timestamp:
        return jsonify({"error": "Faltan campos requeridos"}), 400

    try:
        # Buscar si ya existe ese contacto
        query = supabase.table("contactos") \
            .select("id") \
            .eq("numero_wa", numero) \
            .eq("nombre_nora", nombre_nora) \
            .execute()

        utc_dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        if query.data:
            # Solo actualiza ultima_interaccion
            contacto_id = query.data[0]["id"]
            supabase.table("contactos").update({
                "ultima_interaccion": utc_dt.isoformat()
            }).eq("id", contacto_id).execute()
            return jsonify({"mensaje": "Contacto actualizado"}), 200
        else:
            # Crear nuevo contacto
            supabase.table("contactos").insert({
                "numero_wa": numero,
                "nombre_nora": nombre_nora,
                "fecha_creacion": utc_dt.isoformat(),
                "ultima_interaccion": utc_dt.isoformat(),
                "estado": "nuevo",
                "etiquetas": []
            }).execute()
            return jsonify({"mensaje": "Contacto creado"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500