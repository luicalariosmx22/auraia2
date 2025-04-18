# clientes/aura/routes/webhook.py

from flask import Blueprint, request
from clientes.aura.handlers.process_message import procesar_mensaje
from clientes.aura.utils.db.historial import guardar_en_historial  # Ruta corregida si es necesario
from datetime import datetime

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.form.to_dict()
        print("📩 Mensaje recibido de Twilio:", data)

        mensaje_usuario = data.get("Body", "")
        telefono = data.get("From", "").replace("whatsapp:", "")
        nombre_nora = "aura"  # dinámico si luego se requiere

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
        print(f"✅ Respuesta generada: {respuesta}")

        # Guardar respuesta del bot
        print(f"🔍 Guardando respuesta del bot: {respuesta}")
        guardar_en_historial(
            remitente=telefono,
            mensaje=respuesta,
            tipo="enviado",
            nombre=nombre_nora
        )

        print("✅ Webhook procesado correctamente.")
        return respuesta, 200

    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return "Error interno", 500
