# 📁 Archivo: clientes/aura/utils/twilio_sender.py

import os
import json
from twilio.rest import Client
from dotenv import load_dotenv
from datetime import datetime
from supabase import create_client
from .error_logger import registrar_error  # 👈 Import relativo corregido

# Configurar entorno y Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🚀 Configuración Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

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
            "from_number": TWILIO_WHATSAPP_NUMBER
        }
        response = supabase.table("twilio_logs").insert(log_entry).execute()
        if not response.data:
            print(f"❌ Error al registrar el envío en Supabase: {not response.data}")
        else:
            print(f"✅ Envío registrado en Supabase: {log_entry}")
    except Exception as e:
        print(f"❌ Error al registrar el envío en Supabase: {str(e)}")
        registrar_error("Supabase", f"Error al registrar envío en Supabase: {e}")

def enviar_mensaje(destino, mensaje):
    """
    Envía un mensaje de WhatsApp utilizando Twilio, normalizando los números.
    """
    try:
        def normalizar_numero(numero):
            numero = str(numero).strip().replace("whatsapp:", "").replace("+", "")
            digitos = ''.join(filter(str.isdigit, numero))
            if digitos.startswith("521") and len(digitos) == 13:
                return f"whatsapp:{digitos}"
            if digitos.startswith("52") and len(digitos) == 12:
                return f"whatsapp:521{digitos[2:]}"
