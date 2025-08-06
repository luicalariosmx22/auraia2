#!/usr/bin/env python3
"""
Probar suscripción de webhook con el Page Access Token específico de Luica Larios
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env.local')

# Configuración
LUICA_PAGE_TOKEN = "EAAPJAAprGjgBPCW28xufZC72i8ZBx0Uketfrexpch7lNZB9igZCw5f5itJwpAhNIlvHitZAupkTKjkakIrOZB3mn0MzH3WqguwcqlQH53qyZBKSN94BPPVGEBYia8A5Soq9TS3MuQlNqEY5U6YggNJj5hx9ZCTKJotpNFoVdlZCoPrZCyUhMZA3nuGhWVIxkUhfGXBUYpZA6"
LUICA_LARIOS_PAGE_ID = "1669696123329079"
WEBHOOK_URL = os.getenv('META_WEBHOOK_URL')
WEBHOOK_VERIFY_TOKEN = os.getenv('META_WEBHOOK_VERIFY_TOKEN')

def validar_page_token():
    """Validar el Page Access Token proporcionado"""
    print("=" * 60)
    print("🔍 VALIDANDO PAGE ACCESS TOKEN PROPORCIONADO")
    print("=" * 60)
    
    # Probar acceso a la página con el token
    url = f"https://graph.facebook.com/v21.0/me?access_token={LUICA_PAGE_TOKEN}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print(f"🌐 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Token válido!")
            print(f"   ID: {data.get('id')}")
            print(f"   Nombre: {data.get('name')}")
            print(f"   Categoría: {data.get('category', 'No disponible')}")
            
            # Verificar que es el token correcto
            if data.get('id') == LUICA_LARIOS_PAGE_ID:
                print(f"🎯 ¡CONFIRMADO! Es el token de la página Luica Larios")
                return True
            else:
                print(f"❓ ADVERTENCIA: ID diferente al esperado")
                print(f"   Esperado: {LUICA_LARIOS_PAGE_ID}")
                print(f"   Recibido: {data.get('id')}")
                return True  # Aún puede funcionar
        else:
            print(f"❌ Token inválido: {data}")
            return False
            
    except Exception as e:
        print(f"❌ Error validando token: {str(e)}")
        return False

def verificar_permisos_webhook():
    """Verificar qué permisos tiene este token"""
    print("\n" + "=" * 60)
    print("🔐 VERIFICANDO PERMISOS DEL TOKEN")
    print("=" * 60)
    
    # Verificar permisos del token
    url = f"https://graph.facebook.com/v21.0/debug_token?input_token={LUICA_PAGE_TOKEN}&access_token={LUICA_PAGE_TOKEN}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            token_info = data.get('data', {})
            print("📋 Información del token:")
            print(f"   App ID: {token_info.get('app_id')}")
            print(f"   Tipo: {token_info.get('type')}")
            print(f"   Válido: {token_info.get('is_valid')}")
            print(f"   Scopes: {', '.join(token_info.get('scopes', []))}")
            
            # Verificar si tiene permisos para webhooks
            scopes = token_info.get('scopes', [])
            webhook_scopes = ['pages_messaging', 'pages_manage_metadata', 'pages_show_list']
            
            print(f"\n🔍 Permisos para webhooks:")
            for scope in webhook_scopes:
                tiene = scope in scopes
                icon = "✅" if tiene else "❌"
                print(f"   {icon} {scope}")
                
        else:
            print(f"❌ Error verificando permisos: {data}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def suscribir_webhook_con_token():
    """Suscribir webhook usando el Page Access Token específico"""
    print("\n" + "=" * 60)
    print("📡 SUSCRIBIENDO WEBHOOK CON PAGE ACCESS TOKEN")
    print("=" * 60)
    
    # Datos para la suscripción
    webhook_data = {
        'object': 'page',
        'callback_url': WEBHOOK_URL,
        'fields': 'feed',
        'verify_token': WEBHOOK_VERIFY_TOKEN,
        'access_token': LUICA_PAGE_TOKEN
    }
    
    url = f"https://graph.facebook.com/v21.0/{LUICA_LARIOS_PAGE_ID}/subscriptions"
    
    try:
        print(f"📡 Enviando suscripción...")
        print(f"   URL: {url}")
        print(f"   Página ID: {LUICA_LARIOS_PAGE_ID}")
        print(f"   Webhook URL: {WEBHOOK_URL}")
        print(f"   Campo: feed")
        print(f"   Verify Token: {WEBHOOK_VERIFY_TOKEN}")
        
        response = requests.post(url, data=webhook_data)
        data = response.json()
        
        print(f"\n🌐 Status: {response.status_code}")
        
        if response.status_code == 200:
            success = data.get('success', False)
            if success:
                print(f"🎉 ¡WEBHOOK SUSCRITO EXITOSAMENTE!")
                print(f"   ✅ Página: Luica Larios")
                print(f"   ✅ ID: {LUICA_LARIOS_PAGE_ID}")
                print(f"   ✅ Webhook URL: {WEBHOOK_URL}")
                print(f"   ✅ Campo: feed")
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

def verificar_suscripciones():
    """Verificar suscripciones activas después de la suscripción"""
    print("\n" + "=" * 60)
    print("🔍 VERIFICANDO SUSCRIPCIONES ACTIVAS")
    print("=" * 60)
    
    url = f"https://graph.facebook.com/v21.0/{LUICA_LARIOS_PAGE_ID}/subscriptions?access_token={LUICA_PAGE_TOKEN}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print(f"🌐 Status: {response.status_code}")
        
        if response.status_code == 200:
            subscriptions = data.get('data', [])
            print(f"📊 Suscripciones encontradas: {len(subscriptions)}")
            
            if subscriptions:
                for i, sub in enumerate(subscriptions, 1):
                    print(f"   {i}. Objeto: {sub.get('object')}")
                    print(f"      URL: {sub.get('callback_url')}")
                    print(f"      Campos: {sub.get('fields', [])}")
                    print(f"      Estado: {sub.get('active', 'Desconocido')}")
            else:
                print(f"   ℹ️ No hay suscripciones activas")
        else:
            print(f"❌ Error verificando suscripciones: {data}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

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
            'webhook_estado': 'activa',
            'page_access_token': LUICA_PAGE_TOKEN[:50] + '...'  # Guardar solo parte del token
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
    print("🎯 PRUEBA CON PAGE ACCESS TOKEN ESPECÍFICO DE LUICA LARIOS")
    print("=" * 80)
    print(f"Token: {LUICA_PAGE_TOKEN[:50]}...")
    print("=" * 80)
    
    # 1. Validar el token
    if not validar_page_token():
        print("\n❌ Token inválido. Abortando.")
        return
    
    # 2. Verificar permisos
    verificar_permisos_webhook()
    
    # 3. Intentar suscribir webhook
    exito = suscribir_webhook_con_token()
    
    # 4. Verificar suscripciones
    verificar_suscripciones()
    
    # 5. Actualizar base de datos si fue exitoso
    if exito:
        actualizar_base_datos()
        
        print(f"\n" + "=" * 80)
        print(f"🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!")
        print(f"✅ Webhook suscrito para Luica Larios")
        print(f"✅ Base de datos actualizada")
        print(f"🔔 La página ahora enviará notificaciones a: {WEBHOOK_URL}")
        print("=" * 80)
    else:
        print(f"\n" + "=" * 80)
        print(f"❌ PROCESO FALLÓ")
        print(f"💡 Revisar errores anteriores para diagnosticar el problema")
        print("=" * 80)

if __name__ == "__main__":
    main()
