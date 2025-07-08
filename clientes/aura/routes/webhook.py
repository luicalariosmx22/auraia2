# 📁 clientes/aura/routes/webhook.py

import logging
from flask import Blueprint, request
from clientes.aura.handlers.process_message import procesar_mensaje  # 👈 Importamos la función PRO

logging.getLogger("openai").setLevel(logging.WARNING)

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    """
    Webhook que recibe los mensajes entrantes de Twilio.
    Toda la lógica completa está delegada al archivo process_message.py para mantener el código limpio y modular.
    """
    try:
        data = request.form.to_dict()
        print("📩 Mensaje recibido:", data)
        print("📝 [LOG] webhook.py recibió datos:", data)  # <--- Log extra para depuración

        # Usamos la función centralizada para procesar todo el mensaje
        respuesta = procesar_mensaje(data)

        return {"message": respuesta}, 200

    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return {"error": "Error interno"}, 500
