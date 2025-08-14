#!/usr/bin/env python3
"""
Diagnóstico de Meta API para entender el error 500
"""
import os
import requests
from dotenv import load_dotenv

def diagnosticar_meta_api():
    """Diagnostica el estado de Meta API y suscripciones"""
    load_dotenv()
    
    app_id = os.getenv('META_APP_ID')
    app_secret = os.getenv('META_APP_SECRET')
    access_token = os.getenv('META_ACCESS_TOKEN')
    webhook_url = os.getenv('META_WEBHOOK_URL')
    
    print('🔍 DIAGNÓSTICO META API')
    print('=' * 50)
    print(f'App ID: {app_id}')
    print(f'Webhook URL: {webhook_url}')
    print()
    
    # 1. Verificar suscripciones existentes
    print('1. 📋 Verificando suscripciones actuales...')
    app_access_token = f'{app_id}|{app_secret}'
    url = f'https://graph.facebook.com/v18.0/{app_id}/subscriptions'
    params = {'access_token': app_access_token}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            subs = data.get('data', [])
            print(f'   Suscripciones existentes: {len(subs)}')
            
            if subs:
                for sub in subs:
                    obj = sub.get('object', 'unknown')
                    callback_url = sub.get('callback_url', 'N/A')
                    activa = sub.get('active', False)
                    estado = '✅ Activa' if activa else '❌ Inactiva'
                    fields = sub.get('fields', [])
                    print(f'   • {obj}: {estado}')
                    print(f'     URL: {callback_url}')
                    print(f'     Fields: {", ".join(fields)}')
            else:
                print('   ℹ️  No hay suscripciones configuradas')
        else:
            print(f'   ❌ Error: {response.text}')
    except Exception as e:
        print(f'   ❌ Error: {e}')
    
    # 2. Verificar permisos del token
    print('\n2. 🔑 Verificando permisos del access token...')
    url = 'https://graph.facebook.com/debug_token'
    params = {
        'input_token': access_token,
        'access_token': app_access_token
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            print(f'   Token válido: {data.get("is_valid")}')
            print(f'   App ID: {data.get("app_id")}')
            print(f'   User ID: {data.get("user_id")}')
            print(f'   Tipo: {data.get("type")}')
            
            scopes = data.get('scopes', [])
            print(f'   Scopes ({len(scopes)} permisos):')
            
            # Mostrar scopes relevantes para webhooks
            scopes_importantes = ['pages_read_engagement', 'pages_show_list', 'manage_pages', 'ads_read', 'ads_management']
            for scope in scopes:
                if scope in scopes_importantes:
                    print(f'     ✅ {scope}')
                elif len([s for s in scopes_importantes if s in scopes]) < 5:
                    # Si no tiene muchos importantes, mostrar algunos más
                    print(f'     • {scope}')
        else:
            print(f'   ❌ Error: {response.text}')
    except Exception as e:
        print(f'   ❌ Error: {e}')
    
    # 3. Test del webhook URL
    print('\n3. 🌐 Verificando accesibilidad del webhook URL...')
    try:
        # Test GET al webhook (debería responder con 405 Method Not Allowed o similar)
        response = requests.get(webhook_url, timeout=10)
        print(f'   Status: {response.status_code}')
        print(f'   Respuesta: {response.text[:200]}...' if len(response.text) > 200 else f'   Respuesta: {response.text}')
        
        if response.status_code in [200, 405, 404]:
            print('   ✅ URL es accesible desde internet')
        else:
            print('   ⚠️  URL puede no ser accesible')
    except Exception as e:
        print(f'   ❌ Error: {e}')
    
    # 4. Verificar información de la app
    print('\n4. 📱 Verificando información de la app...')
    url = f'https://graph.facebook.com/v18.0/{app_id}'
    params = {'access_token': app_access_token}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'   Nombre: {data.get("name", "N/A")}')
            print(f'   Categoría: {data.get("category", "N/A")}')
            print(f'   ID: {data.get("id", "N/A")}')
        else:
            print(f'   ❌ Error: {response.text}')
    except Exception as e:
        print(f'   ❌ Error: {e}')
    
    print('\n' + '=' * 50)
    print('🎯 RECOMENDACIONES:')
    print('1. Si no hay suscripciones, el error 500 puede ser normal la primera vez')
    print('2. Verificar que el webhook URL sea accesible públicamente')
    print('3. Comprobar que la app tenga los permisos necesarios')
    print('4. Intentar crear la suscripción paso a paso')

if __name__ == "__main__":
    diagnosticar_meta_api()
