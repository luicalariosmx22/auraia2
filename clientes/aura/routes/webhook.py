# clientes/aura/routes/webhook.py

import os
from flask import Blueprint, request
from clientes.aura.handlers.process_message import procesar_mensaje
from clientes.aura.utils.validador_nora import validar_nombre_nora
from clientes.aura.utils.normalizador import normalizar_numero  # ✅ Importación de normalizador
from clientes.aura.utils.supabase import supabase  # ✅ Importación de Supabase
from datetime import datetime

webhook_bp = Blueprint("webhook", __name__)

def obtener_nombre_nora_por_numero(numero_nora):
    """
    Obtiene el nombre de Nora desde Supabase utilizando el número de Nora.
    """
    try:
        response = (
            supabase.table("configuracion_bot")
            .select("nombre_nora")
            .eq("numero_nora", numero_nora)
            .execute()
        )
        if response.data:
            return response.data[0]["nombre_nora"]
    except Exception as e:
        print(f"❌ Error al obtener nombre_nora desde Supabase: {e}")
    return "nora"  # Fallback en caso de error o si no se encuentra

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    try:
        # Obtener datos del mensaje recibido
        data = request.form.to_dict()
        print("📩 Mensaje recibido:", data)

        # Obtener el número de destino (Nora) y normalizarlo
        numero_destino = data.get("To", "")  # Este es el número de la Nora (whatsapp:+52155933...)
        numero_nora = normalizar_numero(numero_destino)
        print(f"📞 Número de Nora detectado: {numero_nora}")

        # Buscar el nombre de Nora en Supabase
        nombre_nora = obtener_nombre_nora_por_numero(numero_nora)
        print(f"🎯 Detectado nombre_nora automáticamente: {nombre_nora}")

        # Validar y normalizar el nombre de Nora
        nombre_nora = validar_nombre_nora(nombre_nora)
        print(f"🎯 Procesando mensaje para Nora: {nombre_nora}")

        # Procesar el mensaje (ya gestiona historial, IA, conocimiento y configuración)
        respuesta = procesar_mensaje(data)

        if not respuesta:
            print("🟡 No se generó una respuesta. Posiblemente sin IA o sin conocimiento.")
        else:
            print(f"✅ Respuesta enviada: {respuesta}")

        return respuesta or "", 200

    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return "Error interno", 500
