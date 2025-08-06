#!/usr/bin/env python3
"""
Script mejorado para verificar y corregir la configuración del webhook de Meta
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def obtener_app_access_token():
    """Obtener App Access Token usando OAuth"""
    app_id = os.getenv('META_APP_ID')
    app_secret = os.getenv('META_APP_SECRET')
    
    if not app_id or not app_secret:
        return None, None
    
    print("🔑 Obteniendo App Access Token...")
    
    # Método 1: Formato tradicional {app_id}|{app_secret}
    traditional_token = f"{app_id}|{app_secret}"
    print(f"   Método 1: {app_id}|{app_secret[:10]}...")
    
    # Método 2: OAuth endpoint
    oauth_url = "https://graph.facebook.com/oauth/access_token"
    oauth_params = {
        'client_id': app_id,
        'client_secret': app_secret,
        'grant_type': 'client_credentials'
    }
    
    try:
        response = requests.get(oauth_url, params=oauth_params)
        
        if response.status_code == 200:
            oauth_data = response.json()
            oauth_token = oauth_data.get('access_token')
            print(f"   Método 2: OAuth token obtenido: {oauth_token[:30]}...")
            return oauth_token, traditional_token
        else:
            print(f"   Método 2: Error OAuth: {response.json()}")
            return traditional_token, traditional_token
            
    except Exception as e:
        print(f"   Método 2: Error: {str(e)}")
        return traditional_token, traditional_token

def verificar_token_funciona(token, nombre_metodo):
    """Verificar si un token funciona para acceder a /subscriptions"""
    app_id = os.getenv('META_APP_ID')
    
    url = f"https://graph.facebook.com/v21.0/{app_id}/subscriptions"
    params = {'access_token': token}
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {nombre_metodo}: Token funciona correctamente")
            return True, data
        else:
            error_data = response.json()
            print(f"❌ {nombre_metodo}: Error {response.status_code}")
            print(f"   Error: {error_data.get('error', {}).get('message', 'Sin mensaje')}")
            return False, error_data
            
    except Exception as e:
        print(f"❌ {nombre_metodo}: Excepción: {str(e)}")
        return False, None

def mostrar_configuracion_webhook(webhook_data):
    """Mostrar la configuración actual de webhooks"""
    print("\n📋 CONFIGURACIÓN ACTUAL DE WEBHOOKS:")
    print("=" * 50)
    
    if 'data' in webhook_data:
        webhooks = webhook_data['data']
        if webhooks:
            print(f"🔗 Webhooks configurados: {len(webhooks)}")
            for i, webhook in enumerate(webhooks, 1):
                print(f"\n{i}. Webhook:")
                print(f"   📋 Objeto: {webhook.get('object', 'N/A')}")
                print(f"   🔗 URL callback: {webhook.get('callback_url', 'N/A')}")
                print(f"   ✅ Activo: {webhook.get('active', 'N/A')}")
                print(f"   📝 Campos: {', '.join(webhook.get('fields', []))}")
        else:
            print("⚠️ No hay webhooks configurados para esta aplicación")
    else:
        print("❌ No se encontró data en la respuesta")

def verificar_app_info(token):
    """Verificar información de la aplicación"""
    app_id = os.getenv('META_APP_ID')
    
    print(f"\n📱 INFORMACIÓN DE LA APLICACIÓN:")
    print("=" * 40)
    
    url = f"https://graph.facebook.com/v21.0/{app_id}"
    params = {
        'access_token': token,
        'fields': 'id,name,category,app_domains'
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            app_data = response.json()
            print(f"✅ Nombre: {app_data.get('name', 'N/A')}")
            print(f"📱 ID: {app_data.get('id', 'N/A')}")
            print(f"📂 Categoría: {app_data.get('category', 'N/A')}")
            print(f"🌐 Dominios: {', '.join(app_data.get('app_domains', []))}")
        else:
            error_data = response.json()
            print(f"❌ Error obteniendo info de app: {error_data}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Función principal"""
    print("🔧 DIAGNÓSTICO Y CORRECCIÓN DE WEBHOOK META")
    print("=" * 60)
    
    app_id = os.getenv('META_APP_ID')
    app_secret = os.getenv('META_APP_SECRET')
    
    if not app_id or not app_secret:
        print("❌ Error: META_APP_ID y META_APP_SECRET deben estar configurados")
        return
    
    print(f"📱 App ID: {app_id}")
    print(f"🔑 App Secret: {app_secret[:10]}...{app_secret[-10:] if len(app_secret) > 20 else app_secret}")
    
    # 1. Obtener tokens
    oauth_token, traditional_token = obtener_app_access_token()
    
    # 2. Probar ambos métodos
    print(f"\n🧪 PROBANDO MÉTODOS DE AUTENTICACIÓN:")
    print("=" * 45)
    
    # Probar OAuth token
    oauth_works, oauth_data = verificar_token_funciona(oauth_token, "OAuth Token")
    
    # Probar traditional token
    traditional_works, traditional_data = verificar_token_funciona(traditional_token, "Traditional Token")
    
    # 3. Usar el token que funcione
    working_token = None
    working_data = None
    
    if oauth_works:
        working_token = oauth_token
        working_data = oauth_data
        print(f"\n🎯 Usando OAuth Token para verificaciones")
    elif traditional_works:
        working_token = traditional_token
        working_data = traditional_data
        print(f"\n🎯 Usando Traditional Token para verificaciones")
    else:
        print(f"\n❌ Ningún método de token funciona")
        return
    
    # 4. Mostrar configuración de webhooks
    if working_data:
        mostrar_configuracion_webhook(working_data)
    
    # 5. Verificar información de la aplicación
    verificar_app_info(working_token)
    
    # 6. Verificar variables de entorno
    print(f"\n🔧 VARIABLES DE ENTORNO:")
    print("=" * 30)
    webhook_url = os.getenv('META_WEBHOOK_URL')
    verify_token = os.getenv('META_WEBHOOK_VERIFY_TOKEN')
    
    print(f"🔗 META_WEBHOOK_URL: {webhook_url if webhook_url else '❌ No configurada'}")
    print(f"🔑 META_WEBHOOK_VERIFY_TOKEN: {'✅ Configurada' if verify_token else '❌ No configurada'}")
    
    print(f"\n✅ DIAGNÓSTICO COMPLETADO")
    print("=" * 30)
    
    if working_token:
        print(f"🎉 Sistema de webhooks operacional")
        print(f"🔑 Token válido encontrado")
    else:
        print(f"⚠️ Problemas de autenticación detectados")

if __name__ == "__main__":
    main()
