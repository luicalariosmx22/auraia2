# clientes/aura/routes/webhook.py

from flask import Blueprint, request
from clientes.aura.handlers.process_message import procesar_mensaje
from utils.db.historial import guardar_en_historial  # Importar desde el nivel raíz
from datetime import datetime

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.form.to_dict()
        print("📩 Mensaje recibido de Twilio:", data)

        mensaje_usuario = data.get("Body", "")
        telefono = data.get("From", "").replace("whatsapp:", "")
        nombre_nora = "aura"  # Asegúrate de obtener este valor dinámicamente si es necesario

        # ✅ Guardar mensaje del usuario en historial_conversaciones
        print(f"🔍 Guardando mensaje del usuario: {mensaje_usuario}")
        guardar_en_historial(telefono, mensaje_usuario, "usuario", nombre_nora)

        # Obtener respuesta del bot
        print("🔍 Procesando mensaje para generar respuesta...")
        respuesta = procesar_mensaje(data)
        print(f"✅ Respuesta generada: {respuesta}")

        # ✅ Guardar respuesta del bot en historial_conversaciones
        print(f"🔍 Guardando respuesta del bot: {respuesta}")
        guardar_en_historial(telefono, respuesta, "bot", nombre_nora)

        print("✅ Webhook procesado correctamente.")
        return respuesta, 200

    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return "Error interno", 500
