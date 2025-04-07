from flask_socketio import emit
from flask import request
import traceback
import os
import json
import openai
from utils.error_logger import registrar_error

# Configurar OpenAI desde .env
openai.api_key = os.getenv("OPENAI_API_KEY")

# Cargar conocimiento desde JSON
def cargar_bot_data():
    try:
        with open("bot_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        registrar_error("Carga JSON", "Error al cargar bot_data.json", str(e))
        return {}

# Buscar coincidencia por palabra clave
def buscar_respuesta_json(mensaje, bot_data):
    mensaje = mensaje.lower()
    for clave, respuesta in bot_data.items():
        if clave.lower() in mensaje:
            return respuesta
    return None

# Leer el contenido del archivo de conocimiento
def leer_conocimiento_txt():
    try:
        with open("servicios_conocimiento.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        registrar_error("Lectura TXT", "Error al leer servicios_conocimiento.txt", str(e))
        return ""

# Generar respuesta usando OpenAI
def generar_respuesta_con_ia(mensaje_usuario, contexto):
    try:
        print("🧠 Enviando pregunta a OpenAI...")
        prompt = f"""
Contexto:
{contexto}

Pregunta:
{mensaje_usuario}

Respuesta clara, útil y amable:
"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=400
        )
        respuesta_generada = response.choices[0].message["content"].strip()
        print("✅ Respuesta de OpenAI:", respuesta_generada)
        return respuesta_generada

    except Exception as e:
        registrar_error("OpenAI", "Error al generar respuesta de IA", traceback.format_exc())
        return None

def register_socketio_handlers(socketio):

    @socketio.on('connect')
    def handle_connect():
        print('✅ Cliente conectado')
        emit('response', {'mensaje': 'Conectado al servidor'})

    @socketio.on('disconnect')
    def handle_disconnect():
        print('❌ Cliente desconectado')

    @socketio.on('enviar_mensaje')
    def handle_enviar_mensaje(data):
        try:
            print('📨 Mensaje recibido:', data)

            numero = data.get('numero')
            mensaje = data.get('mensaje')

            # Emitir mensaje del usuario
            emit('nuevo_mensaje', {
                'mensaje': mensaje,
                'remitente': numero,
                'nombre': "Tú"
            }, broadcast=True)

            # Buscar en JSON
            bot_data = cargar_bot_data()
            respuesta = buscar_respuesta_json(mensaje, bot_data)

            # Si no hay, usar IA
            if not respuesta:
                contexto = leer_conocimiento_txt()
                respuesta = generar_respuesta_con_ia(mensaje, contexto)

            # Si no hay respuesta, fallback
            if not respuesta:
                respuesta = "⚠️ Lo siento, no pude generar una respuesta en este momento."

            emit('nuevo_mensaje', {
                'mensaje': respuesta,
                'remitente': 'bot',
                'nombre': "Aura AI"
            }, broadcast=True)

        except Exception as e:
            registrar_error("SocketIO", "Error general al procesar mensaje", traceback.format_exc())
            emit('nuevo_mensaje', {
                'mensaje': "❌ Error interno del bot. Por favor intenta más tarde.",
                'remitente': 'bot',
                'nombre': "Aura AI"
            }, broadcast=True)
