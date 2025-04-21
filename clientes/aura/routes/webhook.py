# clientes/aura/routes/webhook.py

import os  # ✅ Importación agregada
from flask import Blueprint, request
from clientes.aura.handlers.process_message import procesar_mensaje
from clientes.aura.utils.historial import guardar_en_historial  # Ruta corregida si es necesario
from clientes.aura.utils.normalizador import normalizar_numero  # ✅ Importación agregada
from datetime import datetime

# Configuración de variables de entorno
NORA_NUMERO = os.getenv("NORA_NUMERO")  # ✅ Variable de entorno para el número de Nora

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    try:
        # Obtener datos del mensaje recibido
        data = request.form.to_dict()
        print("📩 Mensaje recibido de Twilio:", data)

        mensaje_usuario = data.get("Body", "")
        telefono = normalizar_numero(data.get("From", ""))  # ✅ Línea actualizada
        nombre_nora = "aura"  # dinámico si luego se requiere

        print(f"🔍 Datos procesados: mensaje_usuario='{mensaje_usuario}', telefono='{telefono}', nombre_nora='{nombre_nora}'")

        # Guardar mensaje del usuario
        print(f"🔍 Guardando mensaje del usuario: {mensaje_usuario}")
        guardar_en_historial(
            remitente=telefono,
            mensaje=mensaje_usuario,
            tipo="recibido",
            nombre=nombre_nora
        )

        # Procesar y generar respuesta
        print("🔍 Procesando mensaje para generar respuesta...")
        respuesta = procesar_mensaje(data)
        print(f"✅ Respuesta generada por Nora: {respuesta}")

        # Guardar respuesta del bot
        print(f"🔍 Guardando respuesta del bot: {respuesta}")
        guardar_en_historial(
            remitente=NORA_NUMERO,  # ✅ Usar el número de Nora desde la variable de entorno
            mensaje=respuesta,
            tipo="enviado",
            nombre=nombre_nora
        )

        print("✅ Webhook procesado correctamente. Respuesta enviada a Twilio.")
        return respuesta, 200

    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return "Error interno", 500
