# 📁 Archivo: clientes/aura/utils/twilio_sender.py

import os
from twilio.rest import Client
from dotenv import load_dotenv
from clientes.aura.utils.error_logger import registrar_error

load_dotenv()

# Configurar cliente Twilio
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")  # Debe incluir 'whatsapp:'

client = Client(TWILIO_SID, TWILIO_TOKEN)

def enviar_mensaje(numero, mensaje, nombre_contacto=None):
    try:
        # Asegurar que el número tenga el prefijo correcto
        to_number = numero if numero.startswith("whatsapp:") else f"whatsapp:{numero}"

        print("\n📤 Enviando mensaje...")
        print("👤 Nombre del contacto:", nombre_contacto or "(desconocido)")
        print("👉 De:", FROM_NUMBER)
        print("👉 Para:", to_number)
        print("📨 Contenido:", mensaje)

        message = client.messages.create(
            body=mensaje,
            from_=FROM_NUMBER,
            to=to_number
        )

        print(f"✅ Mensaje enviado. SID: {message.sid}\n")
        return message.sid

    except Exception as e:
        print("❌ Error al enviar mensaje con Twilio:", e)
        registrar_error("Twilio", f"Error al enviar mensaje a {numero}: {e}")
        return None
