from flask import Blueprint, request
from clientes.aura.handlers.process_message import procesar_mensaje
from clientes.aura.utils.error_logger import registrar_error

webhook_bp = Blueprint('webhook_aura', __name__)

@webhook_bp.route("/webhook/aura", methods=["POST"])
def webhook():
    try:
        data = request.form
        respuesta = procesar_mensaje(data)
        return "ok", 200
    except Exception as e:
        registrar_error("Webhook", str(e))
        return "error", 500
