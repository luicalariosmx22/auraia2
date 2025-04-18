# 📁 Archivo: clientes/aura/utils/twilio_sender.py

import os
import json
from twilio.rest import Client
from dotenv import load_dotenv
from datetime import datetime
from supabase import create_client
from clientes.aura.utils.error_logger import registrar_error

# Configurar entorno y Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configurar Twilio
FROM_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(TWILIO_SID, TWILIO_TOKEN)

# Asegurar que el número de envío tenga el formato correcto
if FROM_NUMBER.startswith("whatsapp:+52") and not FROM_NUMBER.startswith("whatsapp:+521"):
    FROM_NUMBER = FROM_NUMBER.replace("whatsapp:+52", "whatsapp:+521", 1)

def registrar_envio(numero, mensaje, sid, estado):
    """
    Registra el mensaje enviado en la tabla `twilio_logs` en Supabase.
    """
    try:
        log_entry = {
            "numero": numero,
            "mensaje": mensaje,
            "sid": sid,
            "estado": estado,
            "fecha_envio": datetime.now().isoformat(),
            "from_number": FROM_NUMBER
        }
        response = supabase.table("twilio_logs").insert(log_entry).execute()
        if response.error:
            print(f"❌ Error al registrar el envío en Supabase: {response.error}")
        else:
            print(f"✅ Envío registrado en Supabase: {log_entry}")
    except Exception as e:
        print(f"❌ Error al registrar el envío en Supabase: {str(e)}")
        registrar_error("Supabase", f"Error al registrar envío en Supabase: {e}")

def enviar_mensaje(numero, mensaje, nombre_contacto=None):
    """
    Envía un mensaje a través de Twilio y registra el envío en Supabase.
    """
    try:
        # Asegurar formato correcto del número destino
        to_number = numero if numero.startswith("whatsapp:") else f"whatsapp:{numero}"

        print("\n📤 Enviando mensaje...")
        print("👤 Nombre del contacto:", nombre_contacto or "(desconocido)")
        print("👉 De:", FROM_NUMBER)
        print("👉 Para:", to_number)
        print("📨 Contenido:", mensaje)

        # Enviar mensaje con Twilio
        message = client.messages.create(
            body=mensaje,
            from_=FROM_NUMBER,
            to=to_number
        )

        print(f"✅ Mensaje enviado. SID: {message.sid}\n")

        # Registrar el envío en Supabase
        registrar_envio(numero, mensaje, message.sid, "enviado")

        return message.sid

    except Exception as e:
        print("❌ Error al enviar mensaje con Twilio:", e)
        registrar_error("Twilio", f"Error al enviar mensaje a {numero}: {e}")

        # Registrar el error en Supabase
        registrar_envio(numero, mensaje, None, "error")

        return None
