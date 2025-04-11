import os
from dotenv import load_dotenv
from twilio.rest import Client
from clientes.aura.utils.error_logger import registrar_error

load_dotenv()

def enviar_mensaje(numero, mensaje):
    try:
        cuenta_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        numero_twilio = os.getenv("TWILIO_PHONE_NUMBER")

        cliente = Client(cuenta_sid, auth_token)

        cliente.messages.create(
            from_=f"whatsapp:{numero_twilio}",
            body=mensaje,
            to=f"whatsapp:{numero}"
        )
    except Exception as e:
        registrar_error("Twilio", f"Error al enviar mensaje: {e}")
