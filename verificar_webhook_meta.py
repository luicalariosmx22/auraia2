#!/usr/bin/env python3
"""
Script para verificar el estado del webhook en Meta
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def verificar_webhook_meta():
    """Verificar si el webhook está registrado en Meta"""
    
    access_token = os.getenv('META_ACCESS_TOKEN')
    app_id = os.getenv('META_APP_ID')
    
    if not access_token or not app_id:
        print("❌ Error: META_ACCESS_TOKEN y META_APP_ID deben estar configurados")
        return
    
    print("🔍 Verificando configuración de webhook en Meta...")
    print(f"📱 App ID: {app_id}")
    
    # URL para obtener información de webhooks de la app
    url = f"https://graph.facebook.com/v18.0/{app_id}/subscriptions"
    
    params = {
        'access_token': access_token
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 200:
            print("✅ Respuesta exitosa de Meta API")
            
            if 'data' in data:
                webhooks = data['data']
                if webhooks:
                    print(f"🔗 Webhooks configurados: {len(webhooks)}")
                    for webhook in webhooks:
                        print(f"  📋 Objeto: {webhook.get('object', 'N/A')}")
                        print(f"  🔗 URL callback: {webhook.get('callback_url', 'N/A')}")
                        print(f"  ✅ Activo: {webhook.get('active', 'N/A')}")
                        print(f"  📝 Campos: {webhook.get('fields', 'N/A')}")
                        print("  ---")
                else:
                    print("⚠️ No hay webhooks configurados para esta app")
            else:
                print("❌ No se encontró data en la respuesta")
                print(f"Respuesta: {data}")
        else:
            print(f"❌ Error {response.status_code}: {data}")
            
    except Exception as e:
        print(f"❌ Error al verificar webhook: {str(e)}")
    
    # También verificar variables de entorno relevantes
    print("\n🔧 Variables de entorno configuradas:")
    webhook_url = os.getenv('META_WEBHOOK_URL')
    verify_token = os.getenv('META_WEBHOOK_VERIFY_TOKEN')
    
    print(f"  🔗 META_WEBHOOK_URL: {webhook_url if webhook_url else '❌ No configurada'}")
    print(f"  🔑 META_WEBHOOK_VERIFY_TOKEN: {'✅ Configurada' if verify_token else '❌ No configurada'}")

if __name__ == "__main__":
    verificar_webhook_meta()
