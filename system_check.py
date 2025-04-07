import os
import requests
import json

def verificar_variables_entorno():
    print("🔍 Verificando variables de entorno...")
    missing_vars = []
    required_vars = ['OPENAI_API_KEY', 'TWILIO_AUTH_TOKEN', 'TWILIO_ACCOUNT_SID', 'TWILIO_PHONE_NUMBER', 'ADMIN_PASSWORD', 'TWILIO_WHATSAPP_NUMBER', 'LOGIN_PASSWORD']

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Falta la(s) siguiente(s) variable(s) de entorno: {', '.join(missing_vars)}")
    else:
        print("✅ Todas las variables de entorno están configuradas correctamente.")

def verificar_archivos_esenciales():
    print("\n🔍 Verificando archivos esenciales...")
    required_files = ['bot_data.json', 'logs_errores.json']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Falta el(los) siguiente(s) archivo(s): {file}")
        else:
            print(f"✅ El archivo {file} está presente.")

def verificar_webhook():
    print("\n🔍 Verificando Webhook...")
    url = "https://auraia2-production.up.railway.app/webhook"
    try:
        response = requests.post(url, data={"Body": "hola", "From": "whatsapp:+5215593372311"})
        if response.status_code == 200:
            print("✅ Webhook conectado correctamente.")
        else:
            print(f"❌ Error al conectar con el webhook: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al conectar con el webhook: {e}")

def verificar_base_de_datos():
    print("\n🔍 Verificando conexión a la base de datos...")
    try:
        with open('bot_data.json', 'r', encoding='utf-8') as f:
            json.load(f)  # Intentamos leer el archivo para ver si es accesible.
        print("✅ La base de datos 'bot_data.json' es accesible.")
    except Exception as e:
        print(f"❌ Error al leer la base de datos: {e}")

if __name__ == "__main__":
    verificar_variables_entorno()
    verificar_archivos_esenciales()
    verificar_webhook()
    verificar_base_de_datos()
