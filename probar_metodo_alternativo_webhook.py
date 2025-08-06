#!/usr/bin/env python3
"""
Suscripción de webhook usando API de aplicación en lugar de API de página
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env.local')

# Configuración
LUICA_PAGE_TOKEN = "EAAPJAAprGjgBPCW28xufZC72i8ZBx0Uketfrexpch7lNZB9igZCw5f5itJwpAhNIlvHitZAupkTKjkakIrOZB3mn0MzH3WqguwcqlQH53qyZBKSN94BPPVGEBYia8A5Soq9TS3MuQlNqEY5U6YggNJj5hx9ZCTKJotpNFoVdlZCoPrZCyUhMZA3nuGhWVIxkUhfGXBUYpZA6"
LUICA_LARIOS_PAGE_ID = "1669696123329079"
META_APP_ID = os.getenv('META_APP_ID')
META_APP_SECRET = os.getenv('META_APP_SECRET')
WEBHOOK_URL = os.getenv('META_WEBHOOK_URL')
WEBHOOK_VERIFY_TOKEN = os.getenv('META_WEBHOOK_VERIFY_TOKEN')

def obtener_app_access_token():
    """Obtener App Access Token"""
    print("=" * 60)
    print("🔑 OBTENIENDO APP ACCESS TOKEN")
    print("=" * 60)
    
    url = f"https://graph.facebook.com/oauth/access_token?client_id={META_APP_ID}&client_secret={META_APP_SECRET}&grant_type=client_credentials"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            app_token = data.get('access_token')
            print(f"✅ App Access Token obtenido: {app_token[:50]}...")
            return app_token
        else:
            print(f"❌ Error obteniendo App Access Token: {data}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def suscribir_webhook_via_app(app_token):
    """Suscribir webhook usando la API de aplicación"""
    print("\n" + "=" * 60)
    print("📡 SUSCRIBIENDO VIA API DE APLICACIÓN")
    print("=" * 60)
    
    if not app_token:
        print("❌ No hay App Access Token disponible")
        return False
    
    # Datos para la suscripción usando API de aplicación
    webhook_data = {
        'object': 'page',
        'callback_url': WEBHOOK_URL,
        'verify_token': WEBHOOK_VERIFY_TOKEN,
        'fields': 'feed',
        'access_token': app_token
    }
    
    # URL de suscripción a nivel de aplicación
    url = f"https://graph.facebook.com/v21.0/{META_APP_ID}/subscriptions"
    
    try:
        print(f"📡 Enviando suscripción via aplicación...")
        print(f"   URL: {url}")
        print(f"   App ID: {META_APP_ID}")
        print(f"   Webhook URL: {WEBHOOK_URL}")
        print(f"   Objeto: page")
        print(f"   Campo: feed")
        
        response = requests.post(url, data=webhook_data)
        data = response.json()
        
        print(f"\n🌐 Status: {response.status_code}")
        
        if response.status_code == 200:
            success = data.get('success', False)
            if success:
                print(f"🎉 ¡WEBHOOK SUSCRITO A NIVEL DE APLICACIÓN!")
                print(f"   ✅ Aplicación: {META_APP_ID}")
                print(f"   ✅ Objeto: page")
                print(f"   ✅ Campo: feed")
                print(f"   ✅ Webhook URL: {WEBHOOK_URL}")
                return True
            else:
                print(f"❌ Suscripción falló: {data}")
                return False
        else:
            print(f"❌ Error en suscripción:")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {data}")
            return False
            
    except Exception as e:
        print(f"❌ Error suscribiendo webhook: {str(e)}")
        return False

def verificar_suscripciones_app(app_token):
    """Verificar suscripciones a nivel de aplicación"""
    print("\n" + "=" * 60)
    print("🔍 VERIFICANDO SUSCRIPCIONES DE LA APLICACIÓN")
    print("=" * 60)
    
    if not app_token:
        print("❌ No hay App Access Token disponible")
        return
    
    url = f"https://graph.facebook.com/v21.0/{META_APP_ID}/subscriptions?access_token={app_token}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print(f"🌐 Status: {response.status_code}")
        
        if response.status_code == 200:
            subscriptions = data.get('data', [])
            print(f"📊 Suscripciones de aplicación encontradas: {len(subscriptions)}")
            
            if subscriptions:
                for i, sub in enumerate(subscriptions, 1):
                    print(f"   {i}. Objeto: {sub.get('object')}")
                    print(f"      URL: {sub.get('callback_url')}")
                    print(f"      Campos: {sub.get('fields', [])}")
                    print(f"      Estado: {sub.get('active', 'Desconocido')}")
                    
                    # Verificar si es para páginas
                    if sub.get('object') == 'page':
                        print(f"      🎯 Esta suscripción cubrirá las páginas de la app")
            else:
                print(f"   ℹ️ No hay suscripciones de aplicación activas")
        else:
            print(f"❌ Error verificando suscripciones: {data}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def probar_endpoint_alternativo():
    """Probar con endpoint alternativo usando Page Access Token directamente"""
    print("\n" + "=" * 60)
    print("🔄 PROBANDO ENDPOINT ALTERNATIVO")
    print("=" * 60)
    
    # Método alternativo: usar el endpoint de la aplicación pero con Page Token
    webhook_data = {
        'object': 'page',
        'callback_url': WEBHOOK_URL,
        'verify_token': WEBHOOK_VERIFY_TOKEN,
        'fields': 'feed',
        'access_token': LUICA_PAGE_TOKEN
    }
    
    url = f"https://graph.facebook.com/v21.0/{META_APP_ID}/subscriptions"
    
    try:
        print(f"📡 Probando con Page Token en endpoint de aplicación...")
        print(f"   URL: {url}")
        
        response = requests.post(url, data=webhook_data)
        data = response.json()
        
        print(f"\n🌐 Status: {response.status_code}")
        
        if response.status_code == 200:
            success = data.get('success', False)
            if success:
                print(f"🎉 ¡ÉXITO CON MÉTODO ALTERNATIVO!")
                return True
            else:
                print(f"❌ Falló: {data}")
        else:
            print(f"❌ Error: {data}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    return False

def actualizar_base_datos():
    """Actualizar estado en la base de datos"""
    print("\n" + "=" * 60)
    print("💾 ACTUALIZANDO BASE DE DATOS")
    print("=" * 60)
    
    try:
        from supabase.client import create_client, Client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Credenciales de Supabase no encontradas")
            return
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Actualizar estado de la página Luica Larios
        result = supabase.table('facebook_paginas').update({
            'webhook_estado': 'activa'
        }).eq('page_id', LUICA_LARIOS_PAGE_ID).execute()
        
        if result.data:
            print(f"✅ Estado actualizado en base de datos")
            print(f"   Página: Luica Larios")
            print(f"   Estado: activa")
        else:
            print(f"❌ Error actualizando base de datos")
            
    except Exception as e:
        print(f"❌ Error con base de datos: {str(e)}")

def main():
    """Función principal"""
    print("🔄 MÉTODO ALTERNATIVO: SUSCRIPCIÓN VIA API DE APLICACIÓN")
    print("=" * 80)
    
    # 1. Obtener App Access Token
    app_token = obtener_app_access_token()
    
    # 2. Probar suscripción via aplicación
    exito_app = suscribir_webhook_via_app(app_token)
    
    # 3. Verificar suscripciones de aplicación
    verificar_suscripciones_app(app_token)
    
    # 4. Probar método alternativo
    exito_alternativo = probar_endpoint_alternativo()
    
    # 5. Actualizar base de datos si algún método funcionó
    if exito_app or exito_alternativo:
        actualizar_base_datos()
        
        print(f"\n" + "=" * 80)
        print(f"🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!")
        print(f"✅ Webhook configurado para recibir eventos de páginas")
        print(f"✅ Incluye la página Luica Larios")
        print(f"🔔 Eventos se enviarán a: {WEBHOOK_URL}")
        print("=" * 80)
    else:
        print(f"\n" + "=" * 80)
        print(f"❌ TODOS LOS MÉTODOS FALLARON")
        print(f"💡 Posibles causas:")
        print(f"   - Página no completamente administrada por la aplicación")
        print(f"   - Configuración de webhook en Facebook Developer Console")
        print(f"   - Permisos insuficientes a nivel de aplicación")
        print("=" * 80)

if __name__ == "__main__":
    main()
