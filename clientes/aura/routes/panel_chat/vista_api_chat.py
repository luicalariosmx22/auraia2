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

@panel_chat_bp.route("/api/chat/<nombre_nora>/<telefono>", methods=["GET"])
def api_chat(nombre_nora, telefono):
    print(f"📥 Cargando historial para {telefono} de {nombre_nora}")
    try:
        offset = int(request.args.get("offset", 0))
        print(f"🔢 Offset recibido: {offset}")
        telefono = normalizar_numero(telefono)
        print(f"📞 Teléfono normalizado: {telefono}")

        contacto_response = supabase.table("contactos").select("*").eq("telefono", telefono).eq("nombre_nora", nombre_nora).limit(1).execute()
        contacto = contacto_response.data[0] if contacto_response.data else {}
        print(f"👤 Contacto encontrado: {contacto}")

        historial = leer_historial(telefono, nombre_nora, limite=20, offset=offset)
        print(f"📨 Historial recuperado: {historial}")

        resumen = generar_resumen_ia(historial)
        print(f"📝 Resumen generado: {resumen}")

        if not contacto.get('nombre'):
            contacto['nombre'] = contacto.get('telefono', 'Sin nombre')

        return jsonify({
            "success": True,
            "contacto": contacto,
            "mensajes": historial,
            "resumen_ia": resumen
        })
    except Exception as e:
        print(f"❌ Error en /api/chat/{nombre_nora}/{telefono}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500