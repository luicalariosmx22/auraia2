from flask import Blueprint, request
from clientes.aura.handlers.process_message import procesar_mensaje

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.form.to_dict()
        print("📩 Mensaje recibido de Twilio:", data)

        respuesta = procesar_mensaje(data)

        return "OK", 200

    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return "Error interno", 500
