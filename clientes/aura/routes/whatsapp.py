from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from utils.config import cargar_configuracion
from utils.historial import guardar_en_historial
from utils.normalizador import normalizar_numero
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
    """
    Obtiene la información de un contacto desde Supabase.
    Si no existe, lo crea con valores predeterminados.
    """
    try:
        response = supabase.table("contactos").select("*").eq("numero", numero_usuario).execute()
        if not response.data:
            # Crear contacto si no existe
            nuevo_contacto = {
                "numero": numero_usuario,
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
    """
    Actualiza la información de un contacto en Supabase.
    """
    try:
        response = supabase.table("contactos").update(datos_actualizados).eq("numero", numero_usuario).execute()
        if not response.data:
            print(f"❌ Error al actualizar contacto: {not response.data}")
    except Exception as e:
        print(f"❌ Error al actualizar contacto: {str(e)}")

@whatsapp_bp.route('/webhook', methods=['POST'])
def webhook():
    mensaje_usuario = request.form.get('Body', '').strip().lower()
    numero_usuario = normalizar_numero(request.form.get('From'))
    nombre_usuario = request.form.get('ProfileName', '')

    respuesta = MessagingResponse()
    print(f"📩 Mensaje recibido: {mensaje_usuario} de {numero_usuario} ({nombre_usuario})")

    # Obtener o crear contacto en Supabase
    contacto = obtener_contacto(numero_usuario)
    if not contacto:
        respuesta.message("❌ Error al procesar el mensaje. Inténtalo más tarde.")
        return str(respuesta)

    # Actualizar información del contacto
    actualizar_contacto(numero_usuario, {
        "ultimo_mensaje": datetime.now().isoformat(),
        "cantidad_mensajes": contacto.get("cantidad_mensajes", 0) + 1
    })

    # Si IA está desactivada
    if not contacto.get("ia_activada", True):
        respuesta.message("La IA está desactivada. ¿En qué puedo ayudarte de manera manual?")
        guardar_en_historial(numero_usuario, mensaje_usuario, tipo="recibido", nombre=nombre_usuario, ia_activada=False)
        guardar_en_historial(numero_usuario, "La IA está desactivada. ¿En qué puedo ayudarte de manera manual?", tipo="enviado", nombre="Aura AI", ia_activada=False)
        return str(respuesta)

    # Respuestas automatizadas
    if mensaje_usuario in ['hola', 'buenas', 'hi', 'hello']:
        texto_bienvenida = "👋 ¡Hola! Soy *Aura AI*..."
        respuesta.message(texto_bienvenida)
        guardar_en_historial(numero_usuario, mensaje_usuario, tipo="recibido", nombre=nombre_usuario, ia_activada=True)
        guardar_en_historial(numero_usuario, texto_bienvenida, tipo="enviado", nombre="Aura AI", ia_activada=True)
    else:
        respuesta.message("🤖 Lo siento, no tengo información sobre eso todavía.")
        guardar_en_historial(numero_usuario, mensaje_usuario, tipo="recibido", nombre=nombre_usuario, ia_activada=True)
        guardar_en_historial(numero_usuario, "🤖 Lo siento, no tengo información sobre eso todavía.", tipo="enviado", nombre="Aura AI", ia_activada=True)

    return str(respuesta)

@whatsapp_bp.route('/enviar', methods=['POST'])
def enviar_mensaje():
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
            to=numero
        )

        guardar_en_historial(numero, mensaje, tipo="enviado", nombre="Aura AI")
        return jsonify({"status": "ok", "sid": message.sid})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500