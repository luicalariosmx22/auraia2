# clientes/aura/routes/panel_chat/vista_api_chat.py
from flask import request, jsonify
from clientes.aura.routes.panel_chat.blueprint import panel_chat_bp
from clientes.aura.utils.chat.leer_contactos import leer_contactos
from clientes.aura.utils.chat.leer_historial import leer_historial
from clientes.aura.utils.chat.generar_resumen import generar_resumen_ia
from clientes.aura.utils.normalizador import normalizar_numero
from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@panel_chat_bp.route("/api/chat/<telefono>")  # Use panel_chat_bp
def api_chat(telefono):
    try:
        offset = int(request.args.get("offset", 0))
        telefono = normalizar_numero(telefono)
        historial = leer_historial(telefono, limite=20, offset=offset)

        # Consulta directa a Supabase para obtener el contacto
        contacto_response = supabase.table("contactos").select("*").eq("telefono", telefono).execute()
        contacto = contacto_response.data[0] if contacto_response.data else {}

        resumen = generar_resumen_ia(historial)

        return jsonify({
            "success": True,
            "contacto": contacto or {},
            "mensajes": historial,
            "resumen_ia": resumen
        })
    except Exception as e:
        print(f"❌ Error en /api/chat/{telefono}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500