#!/usr/bin/env python3
"""
Suscribir webhook para Luica Larios usando el endpoint correcto
POST /{PAGE_ID}/subscribed_apps
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

def validar_page_token():
    """Validar el Page Access Token proporcionado"""
    print("=" * 60)
    print("🔍 VALIDANDO PAGE ACCESS TOKEN")
    print("=" * 60)
    
    url = f"https://graph.facebook.com/v21.0/{LUICA_LARIOS_PAGE_ID}?fields=id,name,category,access_token&access_token={LUICA_PAGE_TOKEN}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print(f"🌐 Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Token válido para:")
            print(f"   📝 Nombre: {data.get('name')}")
            print(f"   🆔 ID: {data.get('id')}")
            print(f"   📂 Categoría: {data.get('category')}")
            return True
        else:
            print(f"❌ Token inválido: {data}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def suscribir_aplicacion_a_pagina():
    """Suscribir la aplicación a la página usando /subscribed_apps"""
    print("\n" + "=" * 60)
    print("📡 SUSCRIBIENDO APLICACIÓN A LA PÁGINA")
    print("=" * 60)
    
    # URL correcta: POST /{PAGE_ID}/subscribed_apps
    url = f"https://graph.facebook.com/v21.0/{LUICA_LARIOS_PAGE_ID}/subscribed_apps"
    
    # Datos para la suscripción
    data = {
        'access_token': LUICA_PAGE_TOKEN,
        'subscribed_fields': 'feed'  # Campo que queremos suscribir
    }
    
    try:
        print(f"📡 Enviando suscripción...")
        print(f"   URL: {url}")
        print(f"   Campo suscrito: feed")
        
        response = requests.post(url, data=data)
        result = response.json()
        
        print(f"\n🌐 Status: {response.status_code}")
        
        if response.status_code == 200:
            success = result.get('success', False)
            if success:
                print(f"🎉 ¡APLICACIÓN SUSCRITA EXITOSAMENTE!")
                print(f"   ✅ Página: Luica Larios")
                print(f"   ✅ ID: {LUICA_LARIOS_PAGE_ID}")
                print(f"   ✅ Campo: feed")
                return True
            else:
                print(f"❌ Suscripción falló: {result}")
                return False
        else:
            print(f"❌ Error en suscripción: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def verificar_aplicaciones_suscritas():
    """Verificar qué aplicaciones están suscritas a la página"""
    print("\n" + "=" * 60)
    print("🔍 VERIFICANDO APLICACIONES SUSCRITAS")
    print("=" * 60)
    
    url = f"https://graph.facebook.com/v21.0/{LUICA_LARIOS_PAGE_ID}/subscribed_apps?access_token={LUICA_PAGE_TOKEN}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print(f"🌐 Status: {response.status_code}")
        
        if response.status_code == 200:
            apps = data.get('data', [])
            print(f"📊 Aplicaciones suscritas: {len(apps)}")
            
            if apps:
                for i, app in enumerate(apps, 1):
                    app_name = app.get('name', 'Sin nombre')
                    app_id = app.get('id')
                    print(f"   {i}. {app_name} (ID: {app_id})")
                    
                    # Verificar si es nuestra aplicación
                    our_app_id = os.getenv('META_APP_ID')
                    if app_id == our_app_id:
                        print(f"      🎯 ¡Esta es nuestra aplicación!")
            else:
                print(f"   ℹ️ No hay aplicaciones suscritas")
        else:
            print(f"❌ Error: {data}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def verificar_webhook_configurado():
    """Verificar si el webhook está configurado correctamente en la aplicación"""
    print("\n" + "=" * 60)
    print("🔍 VERIFICANDO CONFIGURACIÓN DEL WEBHOOK")
    print("=" * 60)
    
    app_id = os.getenv('META_APP_ID')
    app_token = os.getenv('META_ACCESS_TOKEN')  # App Access Token
    
    url = f"https://graph.facebook.com/v21.0/{app_id}/subscriptions?access_token={app_token}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print(f"🌐 Status: {response.status_code}")
        
        if response.status_code == 200:
            subscriptions = data.get('data', [])
            print(f"📊 Suscripciones de webhook: {len(subscriptions)}")
            
            for sub in subscriptions:
                obj_type = sub.get('object')
                callback_url = sub.get('callback_url')
                fields = sub.get('fields', [])
                active = sub.get('active', False)
                
                print(f"   📡 Objeto: {obj_type}")
                print(f"      URL: {callback_url}")
                print(f"      Campos: {', '.join(fields)}")
                print(f"      Activo: {'✅' if active else '❌'}")
                print()
        else:
            print(f"❌ Error: {data}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def actualizar_base_datos():
    """Actualizar el estado en la base de datos"""
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
    print("🎯 SUSCRIPCIÓN CORRECTA: LUICA LARIOS /subscribed_apps")
    print("=" * 80)
    
    # 1. Validar Page Access Token
    if not validar_page_token():
        print("\n❌ Page Access Token inválido. Abortando.")
        return
    
    # 2. Verificar aplicaciones suscritas actuales
    verificar_aplicaciones_suscritas()
    
    # 3. Suscribir aplicación a la página
    exito = suscribir_aplicacion_a_pagina()
    
    # 4. Verificar suscripción después del intento
    verificar_aplicaciones_suscritas()
    
    # 5. Verificar configuración del webhook en la aplicación
    verificar_webhook_configurado()
    
    # 6. Actualizar base de datos si fue exitoso
    if exito:
        actualizar_base_datos()
        
        print(f"\n" + "=" * 80)
        print(f"🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!")
        print(f"✅ Aplicación suscrita a página Luica Larios")
        print(f"✅ Base de datos actualizada")
        print(f"🔔 La página ahora enviará notificaciones de 'feed' a: {WEBHOOK_URL}")
        print("=" * 80)
    else:
        print(f"\n" + "=" * 80)
        print(f"❌ PROCESO FALLÓ")
        print(f"💡 Revisar errores anteriores para diagnosticar el problema")
        print("=" * 80)

if __name__ == "__main__":
    main()
