from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from clientes.aura.utils.normalizador import normalizar_numero
from clientes.aura.utils.historial import guardar_en_historial
from clientes.aura.utils.buscar_conocimiento import buscar_conocimiento
from clientes.aura.handlers.handle_ai import manejar_respuesta_ai
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

whatsapp_bp = Blueprint('whatsapp', __name__, url_prefix='/whatsapp')

def obtener_contacto(numero_usuario):
    numero_usuario = normalizar_numero(numero_usuario)

    try:
        response = supabase.table("contactos").select("*").eq("telefono", numero_usuario).execute()
        if not response.data:
            nuevo_contacto = {
                "telefono": numero_usuario,
                "nombre": "Desconocido",
                "ia_activada": True,
                "etiquetas": [],
                "primer_mensaje": datetime.now().isoformat(),
                "ultimo_mensaje": datetime.now().isoformat(),
                "cantidad_mensajes": 1
            }
            supabase.table("contactos").insert(nuevo_contacto).execute()
            return nuevo_contacto
        return response.data[0]
    except Exception as e:
        print(f"❌ Error al obtener contacto: {str(e)}")
        return None

def actualizar_contacto(numero_usuario, datos_actualizados):
    numero_usuario = normalizar_numero(numero_usuario)

    try:
        supabase.table("contactos").update(datos_actualizados).eq("telefono", numero_usuario).execute()
    except Exception as e:
        print(f"❌ Error al actualizar contacto: {str(e)}")

@whatsapp_bp.route('/webhook', methods=['POST'])
def webhook():
    """
    Webhook para recibir mensajes de WhatsApp y responder utilizando Twilio.
    """
    data = request.form.to_dict()
    mensaje_usuario = data.get('Body', '').strip()
    numero_usuario = normalizar_numero(data.get('From'))
    nombre_usuario = data.get('ProfileName', 'Usuario')
    nombre_nora = data.get('NombreNora', 'Nora').lower()  # Normalizar el nombre de Nora a minúsculas

    print(f"📩 Mensaje recibido: {mensaje_usuario} de {numero_usuario} ({nombre_usuario})")

    # Procesar el mensaje y generar una respuesta
    respuesta_texto = procesar_mensaje(data)

    # Crear la respuesta de Twilio
    twilio_resp = MessagingResponse()
    twilio_resp.message(respuesta_texto)

    return str(twilio_resp), 200

@whatsapp_bp.route('/enviar', methods=['POST'])
def enviar_mensaje_api():
    data = request.get_json()
    numero = normalizar_numero(data.get('numero'))
    mensaje = data.get('mensaje')

    try:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=mensaje,
            from_=from_whatsapp_number,
            to=f"whatsapp:{numero}"
        )

        guardar_en_historial(numero, mensaje, tipo="enviado", nombre="Nora")
        return jsonify({"status": "ok", "sid": message.sid})
    except Exception as e:
        print(f"❌ Error al enviar mensaje: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
