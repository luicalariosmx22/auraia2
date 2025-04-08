import os
import json
import requests
from dotenv import load_dotenv
import openai

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Función para verificar las variables de entorno necesarias
def verificar_variables_entorno():
    print("🔍 Verificando variables de entorno...")
    required_vars = [
        'OPENAI_API_KEY', 
        'TWILIO_AUTH_TOKEN', 
        'TWILIO_ACCOUNT_SID', 
        'TWILIO_PHONE_NUMBER', 
        'ADMIN_PASSWORD', 
        'TWILIO_WHATSAPP_NUMBER', 
        'LOGIN_PASSWORD'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Falta la(s) siguiente(s) variable(s) de entorno: {', '.join(missing_vars)}")
    else:
        print("✅ Todas las variables de entorno están configuradas correctamente.")

# Función para verificar los archivos esenciales
def verificar_archivos_esenciales():
    print("\n🔍 Verificando archivos esenciales...")
    required_files = ['bot_data.json', 'logs_errores.json']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Falta el archivo: {file}")
        else:
            print(f"✅ El archivo {file} está presente.")

# Función para verificar la conexión al webhook
def verificar_webhook():
    print("\n🔍 Verificando Webhook...")
    url = "https://auraia2-production.up.railway.app/webhook"  # URL actualizada del webhook en Railway
    try:
        response = requests.post(url, data={"Body": "hola", "From": "whatsapp:+5215593372311"})
        if response.status_code == 200:
            print("✅ Webhook conectado correctamente.")
        else:
            print(f"❌ Error al conectar con el webhook: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al conectar con el webhook: {e}")

# Función para verificar la accesibilidad de la base de datos
def verificar_base_de_datos():
    print("\n🔍 Verificando conexión a la base de datos...")
    try:
        with open('bot_data.json', 'r', encoding='utf-8') as f:
            json.load(f)  # Intentamos leer el archivo para ver si es accesible.
        print("✅ La base de datos 'bot_data.json' es accesible.")
    except Exception as e:
        print(f"❌ Error al leer la base de datos: {e}")

# Función para verificar que la IA está funcionando
def verificar_ia():
    print("\n🔍 Verificando Inteligencia Artificial (IA)...")
    url = "https://auraia2-production.up.railway.app/webhook"  # URL del webhook de la IA

    # Enviar un mensaje de prueba para que la IA responda
    data = {
        "Body": "¿Cuál es tu nombre?",  # Mensaje de prueba
        "From": "whatsapp:+5215593372311"
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            # Imprimir la respuesta completa de la IA para diagnóstico
            print("Respuesta de la IA: ", response.text)

            if "Soy Aura AI" in response.text:  # Aseguramos que la IA responde correctamente
                print("✅ La IA está funcionando correctamente.")
            else:
                print("❌ La respuesta de la IA no es la esperada.")
                print("Respuesta recibida: ", response.text)  # Mostramos la respuesta completa para diagnóstico
        else:
            print(f"❌ Error al conectar con la IA: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al verificar la IA: {e}")

# Función para verificar que el sistema principal está funcionando correctamente
def verificar_funciones_principales():
    print("\n🔍 Verificando Funciones Principales del Robot...")
    
    # Verificar si las respuestas están funcionando
    print("\n🔍 Verificando respuestas registradas...")
    url = "https://auraia2-production.up.railway.app/webhook"  # URL actualizada del webhook
    data = {"Body": "Presentación", "From": "whatsapp:+5215593372311"}
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("✅ Respuesta registrada y funcionando correctamente.")
        else:
            print(f"❌ Error al verificar respuestas: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al verificar respuestas: {e}")

    # Verificar si el proceso de confirmación funciona correctamente
    print("\n🔍 Verificando confirmaciones...")
    data = {"Body": "sí", "From": "whatsapp:+5215593372311"}  # Enviamos una confirmación
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("✅ Confirmación procesada correctamente.")
        else:
            print(f"❌ Error al verificar confirmación: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al verificar confirmación: {e}")

# Función principal para ejecutar las verificaciones
def ejecutar_verificaciones():
    verificar_variables_entorno()
    verificar_archivos_esenciales()
    verificar_webhook()
    verificar_base_de_datos()
    verificar_ia()  # Nueva verificación para la IA
    verificar_funciones_principales()  # Nueva verificación para las funciones principales del robot

# Ejecución de las verificaciones al correr el script
if __name__ == "__main__":
    ejecutar_verificaciones()
