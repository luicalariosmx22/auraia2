from twilio.rest import Client
from dotenv import load_dotenv
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.error_logger import registrar_error
import os
import re

load_dotenv()

# 🔐 Configurar credenciales
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(TWILIO_SID, TWILIO_TOKEN)

def normalizar_numero(numero):
    """
    Convierte cualquier formato a 'whatsapp:521XXXXXXXXXX' o similar.
    """
    numero = str(numero).strip().replace("whatsapp:", "").replace("+", "")
    digitos = re.sub(r"\D", "", numero)
    if digitos.startswith("521") and len(digitos) == 13:
        return f"whatsapp:{digitos}"
    if digitos.startswith("52") and len(digitos) == 12:
        return f"whatsapp:521{digitos[2:]}"
    if len(digitos) == 10:
        return f"whatsapp:521{digitos}"
    if digitos.startswith("1") and len(digitos) == 11:
        return f"whatsapp:{digitos}"
    return ""

def registrar_envio(numero, mensaje, sid, tipo="enviado"):
    try:
        # Usar las columnas correctas de la tabla historial_conversaciones
        supabase.table("historial_conversaciones").insert({
            "telefono": numero,
            "mensaje": mensaje,
            "tipo": tipo,
            "emisor": numero,  # Usar emisor en lugar de sid
            # "sid": sid  # Esta columna no existe en la tabla
        }).execute()
    except Exception as e:
        print("❌ Error registrando historial:", e)
        registrar_error("Historial", f"Error al registrar mensaje: {e}")

def enviar_mensaje(destino, mensaje):
    """
    Envía un mensaje normalizando emisor y receptor.
    """
    try:
        from_normalizado = normalizar_numero(TWILIO_WHATSAPP_NUMBER)
        to_normalizado = normalizar_numero(destino)

        print(f"📤 Enviando mensaje:")
        print(f"   ➤ From: {from_normalizado}")
        print(f"   ➤ To:   {to_normalizado}")
        print(f"   ➤ Texto: {mensaje}")

        message = client.messages.create(
            body=mensaje,
            from_=from_normalizado,
            to=to_normalizado
        )

        print(f"✅ Mensaje enviado correctamente. SID: {message.sid}")
        registrar_envio(to_normalizado, mensaje, message.sid, "enviado")

    except Exception as e:
        print(f"❌ Error enviando mensaje a {destino}: {e}")
        registrar_error("Twilio", f"Error al enviar mensaje a {destino}: {e}")
