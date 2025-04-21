# clientes/aura/routes/webhook.py

import os
from flask import Blueprint, request
from clientes.aura.handlers.process_message import procesar_mensaje
from clientes.aura.utils.validador_nora import validar_nombre_nora  # ✅ Importación del validador
from datetime import datetime

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    try:
        # Obtener datos del mensaje recibido
        data = request.form.to_dict()
        print("📩 Mensaje recibido:", data)

        # Validar y normalizar el nombre de Nora
        nombre_nora = validar_nombre_nora(data.get("NombreNora"))  # ✅ Uso del validador
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
