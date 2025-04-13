# 📁 Archivo: clientes/aura/utils/twilio_sender.py

import os
import json
from twilio.rest import Client
from dotenv import load_dotenv
from clientes.aura.utils.error_logger import registrar_error

load_dotenv()

# Cargar y corregir número de envío (FROM)
FROM_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Asegurar que tenga el +521 (WhatsApp México)
if FROM_NUMBER.startswith("whatsapp:+52") and not FROM_NUMBER.startswith("whatsapp:+521"):
    FROM_NUMBER = FROM_NUMBER.replace("whatsapp:+52", "whatsapp:+521", 1)

# Configurar cliente Twilio
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(TWILIO_SID, TWILIO_TOKEN)

def enviar_mensaje(numero, mensaje, nombre_contacto=None):
    try:
        # Asegurar formato correcto del número destino
        to_number = numero if numero.startswith("whatsapp:") else f"whatsapp:{numero}"

        print("\n📤 Enviando mensaje...")
        print("👤 Nombre del contacto:", nombre_contacto or "(desconocido)")
        print("👉 De:", FROM_NUMBER)
        print("👉 Para:", to_number)
        print("📨 Contenido:", mensaje)

        # Guardar último FROM usado
        with open("clientes/aura/config/twilio_last_sent.json", "w", encoding="utf-8") as f:
            json.dump({"from": FROM_NUMBER}, f, indent=2)

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
