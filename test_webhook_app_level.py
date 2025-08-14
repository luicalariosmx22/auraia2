#!/usr/bin/env python3
"""
Test de registro de webhook a nivel de app con app_secret_proof
"""

from dotenv import load_dotenv
load_dotenv('.env.local')

import requests
import os
import hmac
import hashlib

def test_webhook_app_level():
    """Test directo del registro de webhook a nivel de app"""
    
    app_id = os.getenv('META_APP_ID')
    app_secret = os.getenv('META_APP_SECRET') 
    access_token = os.getenv('META_ACCESS_TOKEN')
    webhook_url = f"{os.getenv('BASE_URL', 'https://app.soynoraai.com')}/meta/webhook"
    verify_token = os.getenv('META_WEBHOOK_VERIFY_TOKEN', 'nora123')

    print('🧪 TEST REGISTRO WEBHOOK NIVEL APP')
    print('=' * 50)
    
    # Verificar variables
    if not all([app_id, app_secret, access_token]):
        print('❌ Variables faltantes')
        print(f'APP_ID: {bool(app_id)}')
        print(f'APP_SECRET: {bool(app_secret)}')
        print(f'ACCESS_TOKEN: {bool(access_token)}')
        return False

    # Calcular app_secret_proof según documentación Meta
    app_secret_proof = hmac.new(
        app_secret.encode('utf-8'),
        access_token.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()

    print(f'📱 App ID: {app_id}')
    print(f'🔗 Webhook URL: {webhook_url}')
    print(f'🔑 App Secret Proof: {app_secret_proof[:20]}...')
    print(f'🎫 Verify Token: {verify_token}')

    # Endpoint oficial Meta
    url = f'https://graph.facebook.com/v18.0/{app_id}/subscriptions'

    data = {
        'object': 'adaccount',
        'callback_url': webhook_url,
        'fields': ['campaign', 'adset', 'ad', 'creative'],
        'verify_token': verify_token,
        'access_token': access_token,
        'appsecret_proof': app_secret_proof
    }

    print(f'\n📡 Enviando POST a: {url}')
    print(f'📋 Campos enviados: {list(data.keys())}')

    try:
        response = requests.post(url, data=data, timeout=15)
        
        print(f'\n📊 Response Status: {response.status_code}')
        print(f'📋 Response Headers: {dict(response.headers)}')
        print(f'📋 Response Body: {response.text}')

        if response.status_code == 200:
            print('\n✅ WEBHOOK REGISTRADO EXITOSAMENTE A NIVEL APP')
            try:
                result = response.json()
                print(f'📋 Resultado: {result}')
            except:
                print('📋 Respuesta sin JSON')
            return True
        else:
            print(f'\n❌ ERROR EN REGISTRO: {response.status_code}')
            try:
                error_data = response.json()
                print(f'📋 Error detalle: {error_data}')
            except:
                print('📋 Error sin JSON detallado')
            return False
            
    except Exception as e:
        print(f'\n❌ ERROR DE CONEXIÓN: {e}')
        return False

if __name__ == "__main__":
    test_webhook_app_level()
