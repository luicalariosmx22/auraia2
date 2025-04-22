# clientes/aura/routes/panel_chat/vista_api_chat.py
from flask import Blueprint, request, jsonify
from clientes.aura.utils.chat.leer_contactos import leer_contactos
from clientes.aura.utils.chat.leer_historial import leer_historial
from clientes.aura.utils.chat.generar_resumen import generar_resumen_ia
from clientes.aura.utils.normalizador import normalizar_numero

vista_api_chat_bp = Blueprint("vista_api_chat", __name__)

@vista_api_chat_bp.route("/api/chat/<telefono>")
def api_chat(telefono):
    try:
        offset = int(request.args.get("offset", 0))
        telefono = normalizar_numero(telefono)
        historial = leer_historial(telefono, limite=20, offset=offset)

        contacto = None
        contactos = leer_contactos()
        for c in contactos:
            if normalizar_numero(c["telefono"])[-10:] == telefono[-10:]:
                contacto = c
                break

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