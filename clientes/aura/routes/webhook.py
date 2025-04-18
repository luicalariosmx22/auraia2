# clientes/aura/routes/webhook.py

from flask import Blueprint, request
from clientes.aura.handlers.process_message import procesar_mensaje
from utils.db.historial import guardar_mensaje

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.form.to_dict()
        print("📩 Mensaje recibido de Twilio:", data)

        mensaje_usuario = data.get("Body", "")
        telefono = data.get("From", "").replace("whatsapp:", "")
        nombre_nora = "aura"  # Asegúrate de obtener este valor dinámicamente si es necesario

        # ✅ Guardar mensaje del usuario
        guardar_mensaje(telefono, mensaje_usuario, "usuario", nombre_nora)

        # Obtener respuesta del bot
        respuesta = procesar_mensaje(data)

        # ✅ Guardar respuesta del bot
        guardar_mensaje(telefono, respuesta, "bot", nombre_nora)

        return respuesta, 200

    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return "Error interno", 500
