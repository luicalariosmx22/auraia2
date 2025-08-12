#!/usr/bin/env python3
"""
Script para verificar que se leen correctamente las variables de entorno
"""
import os
from dotenv import load_dotenv

# Recargar variables de entorno
load_dotenv('.env.local', override=True)

print("🔍 Verificando variables de entorno Meta:")
print(f"META_APP_ID: {os.getenv('META_APP_ID')}")

app_secret = os.getenv('META_APP_SECRET')
webhook_secret = os.getenv('META_WEBHOOK_SECRET')

print(f"META_APP_SECRET: {app_secret[:20] + '...' if app_secret else 'No configurada'} (Facebook API)")
print(f"META_WEBHOOK_SECRET: {webhook_secret if webhook_secret else 'No configurada'} (Webhook)")
print(f"META_WEBHOOK_VERIFY_TOKEN: {os.getenv('META_WEBHOOK_VERIFY_TOKEN')}")
print(f"META_WEBHOOK_URL: {os.getenv('META_WEBHOOK_URL')}")

# Ahora verificar si el App Secret funciona
print("\n🔍 Probando App Access Token:")
app_id = os.getenv('META_APP_ID')
app_secret = os.getenv('META_APP_SECRET')

if app_id and app_secret:
    app_access_token = f"{app_id}|{app_secret}"
    print(f"App Access Token: {app_access_token[:30]}...")
    
    # Probar con una llamada simple a la API
    import requests
    
    url = f"https://graph.facebook.com/v21.0/{app_id}"
    params = {'access_token': app_access_token}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 200:
            print("✅ App Access Token funciona correctamente")
            print(f"App Name: {data.get('name', 'N/A')}")
        else:
            print(f"❌ Error con App Access Token: {data}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
else:
    print("❌ Faltan variables para generar App Access Token")
