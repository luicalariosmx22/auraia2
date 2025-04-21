# clientes/aura/routes/webhook.py

import os
from flask import Blueprint, request
from clientes.aura.handlers.process_message import procesar_mensaje
from clientes.aura.utils.historial import guardar_en_historial
from clientes.aura.utils.normalizador import normalizar_numero
from clientes.aura.utils.supabase import supabase
from datetime import datetime

webhook_bp = Blueprint("webhook", __name__)

def obtener_config_nora(nombre_nora):
    """
    Obtiene la configuración de Nora desde la tabla 'configuracion_bot' en Supabase.
    """
    try:
        print(f"🔍 Buscando configuración para Nora: {nombre_nora}")
        response = (
            supabase.table("configuracion_bot")
            .select("*")
            .eq("nombre_nora", nombre_nora.lower())
            .execute()
        )
        data = response.data or []
        if not data:
            print(f"⚠️ No se encontró configuración para Nora: {nombre_nora}")
            return {}
        print(f"✅ Configuración encontrada para Nora: {data[0]}")
        return data[0]
    except Exception as e:
        print(f"❌ Error al obtener configuración de Nora ({nombre_nora}): {e}")
        return {}

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    try:
        # Obtener datos del mensaje recibido
        data = request.form.to_dict()
        print("📩 Mensaje recibido:", data)

        # Normalizar el nombre de Nora y obtener su configuración
        nombre_nora = data.get("NombreNora", "nora").lower()
        config = obtener_config_nora(nombre_nora)

        if not config:
            print("🛑 No hay configuración válida para esta Nora.")
            return "", 200

        nora_numero = config.get("numero_nora", "5210000000000")
        print(f"🔧 Configuración de Nora ({nombre_nora}):", config)
        print(f"📞 Número de Nora: {nora_numero}")

        # Procesar el mensaje y generar una respuesta
        respuesta = procesar_mensaje(data)
        print(f"✅ Respuesta generada: {respuesta}")

        # Guardar el mensaje del usuario en el historial
        telefono = normalizar_numero(data.get("From", ""))
        mensaje_usuario = data.get("Body", "")
        guardar_en_historial(
            remitente=telefono,
            mensaje=mensaje_usuario,
            tipo="recibido",
            nombre=nombre_nora
        )

        # Guardar la respuesta generada por Nora en el historial
        guardar_en_historial(
            remitente=nora_numero,
            mensaje=respuesta,
            tipo="enviado",
            nombre=nombre_nora
        )

        print("✅ Webhook procesado correctamente.")
        return respuesta, 200

    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return "Error interno", 500
