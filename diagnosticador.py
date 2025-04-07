import os
import json
import requests
import openai
import twilio
from twilio.rest import Client
from utils.config_helper import cargar_configuracion

# Función de verificación de archivos
def verificar_archivos():
    archivos_essenciales = [
        'webhook.py', 'bot_data.json', 'logs_errores.json', 'config.json', 'panel_errores.html', 'login.html'
    ]
    for archivo in archivos_essenciales:
        if not os.path.exists(archivo):
            print(f"❌ El archivo {archivo} NO se encuentra en el proyecto.")
        else:
            print(f"✅ El archivo {archivo} está presente.")

# Función de verificación de Twilio
def verificar_twilio():
    try:
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        client = Client(account_sid, auth_token)
        phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        client.messages.create(
            body="Verificación de conexión Twilio",
            from_=phone_number,
            to=phone_number  # Enviar a tu propio número como prueba
        )
        print("✅ Conexión con Twilio OK.")
    except Exception as e:
        print(f"❌ Error con Twilio: {e}")

# Función de verificación de OpenAI
def verificar_openai():
    try:
        openai.api_key = os.getenv('OPENAI_API_KEY')
        completion = openai.Completion.create(
            engine="text-davinci-003",
            prompt="Verificar conexión de OpenAI",
            max_tokens=5
        )
        print("✅ Conexión con OpenAI OK.")
    except Exception as e:
        print(f"❌ Error con OpenAI: {e}")

# Función de verificación de conexión al webhook
def verificar_webhook():
    try:
        url_webhook = os.getenv('WEBHOOK_URL', 'http://localhost:5000/webhook')  # Reemplazar con la URL real
        response = requests.post(url_webhook, data={'Body': 'hola', 'From': 'whatsapp:+5215593372311'})
        if response.status_code == 200:
            print("✅ Webhook responde correctamente.")
        else:
            print(f"❌ Error en el webhook, status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en la conexión con el webhook: {e}")

# Función de verificación del servidor Flask
def verificar_servidor_flask():
    try:
        url_servidor = os.getenv('FLASK_SERVER_URL', 'http://localhost:5000')
        response = requests.get(url_servidor)
        if response.status_code == 200:
            print("✅ Servidor Flask responde correctamente.")
        else:
            print(f"❌ Error en el servidor Flask, status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en la conexión con el servidor Flask: {e}")

# Función principal
def diagnosticar():
    print("🔍 Iniciando diagnóstico del sistema Aura AI...\n")

    # Verificar archivos esenciales
    verificar_archivos()
    
    # Verificar conexión con Twilio
    verificar_twilio()

    # Verificar conexión con OpenAI
    verificar_openai()

    # Verificar webhook
    verificar_webhook()

    # Verificar servidor Flask
    verificar_servidor_flask()

# Ejecutar el diagnóstico
if __name__ == '__main__':
    diagnosticar()
