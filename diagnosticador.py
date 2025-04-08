import os
import json
import requests
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()  # Asegúrate de que esto esté al principio del archivo

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

# Función principal para ejecutar las verificaciones
def ejecutar_verificaciones():
    verificar_variables_entorno()
    verificar_archivos_esenciales()
    verificar_webhook()
    verificar_base_de_datos()

# Ejecución de las verificaciones al correr el script
if __name__ == "__main__":
    ejecutar_verificaciones()
