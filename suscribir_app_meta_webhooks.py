"""
Script para suscribir la app de Nora a webhooks de Meta Ads
Basado en la documentación oficial de Meta Business API

Proceso:
1. Suscribir la APP a recibir webhooks de adaccounts
2. Suscribir cada cuenta publicitaria a la app
"""

import os
import requests
import json
from dotenv import load_dotenv
from clientes.aura.utils.supabase_client import supabase

load_dotenv()

def obtener_credenciales():
    """Obtiene las credenciales necesarias desde variables de entorno"""
    credenciales = {
        'app_id': os.getenv('META_APP_ID'),
        'app_secret': os.getenv('META_APP_SECRET'),
        'access_token': os.getenv('META_ACCESS_TOKEN'),
        'webhook_url': os.getenv('META_WEBHOOK_URL', 'https://app.soynoraai.com/meta/webhook'),
        'verify_token': os.getenv('META_WEBHOOK_VERIFY_TOKEN', 'nora123')
    }
    
    print("🔍 Verificando credenciales...")
    for key, value in credenciales.items():
        if value:
            if 'token' in key or 'secret' in key:
                print(f"✅ {key}: {value[:10]}...")
            else:
                print(f"✅ {key}: {value}")
        else:
            print(f"❌ {key}: NO CONFIGURADO")
    
    return credenciales

def suscribir_app_a_webhooks(credenciales):
    """
    Paso 1: Suscribir la aplicación a webhooks de adaccounts
    
    POST /{app-id}/subscriptions
    """
    print("\n🎯 PASO 1: Suscribiendo APP a webhooks de adaccounts")
    print("=" * 60)
    
    app_id = credenciales['app_id']
    app_secret = credenciales['app_secret']
    webhook_url = credenciales['webhook_url']
    verify_token = credenciales['verify_token']
    
    if not all([app_id, app_secret]):
        print("❌ ERROR: META_APP_ID y META_APP_SECRET son requeridos")
        return False
    
    # Crear App Access Token: {app-id}|{app-secret}
    app_access_token = f"{app_id}|{app_secret}"
    
    url = f"https://graph.facebook.com/v18.0/{app_id}/subscriptions"
    
    data = {
        'object': 'adaccount',
        'callback_url': webhook_url,
        'fields': ['campaign', 'adset', 'ad', 'creative'],
        'verify_token': verify_token,
        'access_token': app_access_token
    }
    
    print(f"📍 URL: {url}")
    print(f"📍 Webhook URL: {webhook_url}")
    print(f"📍 Object: adaccount")
    print(f"📍 Fields: {data['fields']}")
    print(f"📍 Verify Token: {verify_token}")
    
    try:
        response = requests.post(url, data=data, timeout=15)
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📋 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ APP suscrita exitosamente a webhooks de adaccounts!")
            return True
        else:
            print("❌ Error suscribiendo la app")
            try:
                error_data = response.json()
                if 'error' in error_data:
                    print(f"❌ Error details: {error_data['error']}")
            except:
                pass
            return False
            
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def verificar_suscripcion_app(credenciales):
    """Verifica qué objetos están suscritos a la app"""
    print("\n🔍 Verificando suscripciones de la app...")
    
    app_id = credenciales['app_id']
    app_secret = credenciales['app_secret']
    
    app_access_token = f"{app_id}|{app_secret}"
    
    url = f"https://graph.facebook.com/v18.0/{app_id}/subscriptions"
    params = {'access_token': app_access_token}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            suscripciones = data.get('data', [])
            
            print(f"📋 Suscripciones activas: {len(suscripciones)}")
            
            for sus in suscripciones:
                objeto = sus.get('object')
                callback_url = sus.get('callback_url')
                fields = sus.get('fields', [])
                active = sus.get('active', False)
                
                estado = "✅ Activa" if active else "❌ Inactiva"
                print(f"• {objeto}: {callback_url} - {estado}")
                print(f"  Fields: {', '.join(fields)}")
            
            # Verificar si adaccount está suscrito
            adaccount_suscrito = any(s.get('object') == 'adaccount' for s in suscripciones)
            return adaccount_suscrito
        else:
            print(f"❌ Error verificando suscripciones: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def obtener_cuentas_publicitarias():
    """Obtiene cuentas publicitarias desde Supabase"""
    print("\n📊 Obteniendo cuentas publicitarias desde BD...")
    
    try:
        response = supabase.table('meta_ads_cuentas') \
            .select('id_cuenta_publicitaria, nombre_cliente, estado_actual') \
            .eq('estado_actual', 'ACTIVE') \
            .execute()
        
        cuentas = response.data or []
        print(f"✅ Encontradas {len(cuentas)} cuentas activas")
        
        for cuenta in cuentas:
            print(f"• {cuenta['nombre_cliente']}: {cuenta['id_cuenta_publicitaria']}")
        
        return cuentas
        
    except Exception as e:
        print(f"❌ Error obteniendo cuentas: {e}")
        return []

def suscribir_cuenta_a_app(id_cuenta, access_token, app_id):
    """
    Paso 2: Suscribir una cuenta publicitaria específica a la app
    
    POST /act_{AD_ACCOUNT_ID}/subscribed_apps?app_id={APP_ID}
    """
    print(f"\n🎯 Suscribiendo cuenta {id_cuenta} a la app...")
    
    url = f"https://graph.facebook.com/v18.0/act_{id_cuenta}/subscribed_apps"
    
    data = {
        'access_token': access_token,
        'app_id': app_id
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📋 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') == 'true':
                print(f"✅ Cuenta {id_cuenta} suscrita exitosamente!")
                return True
            else:
                print(f"❌ Respuesta inesperada: {result}")
                return False
        else:
            print(f"❌ Error suscribiendo cuenta {id_cuenta}")
            try:
                error_data = response.json()
                if 'error' in error_data:
                    print(f"❌ Error details: {error_data['error']}")
            except:
                pass
            return False
            
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def verificar_suscripcion_cuenta(id_cuenta, access_token):
    """Verifica qué apps están suscritas a una cuenta"""
    print(f"\n🔍 Verificando apps suscritas a cuenta {id_cuenta}...")
    
    url = f"https://graph.facebook.com/v18.0/act_{id_cuenta}/subscribed_apps"
    params = {'access_token': access_token}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            apps = data.get('data', [])
            
            print(f"📋 Apps suscritas: {len(apps)}")
            for app in apps:
                print(f"• {app.get('name', 'Sin nombre')}: {app.get('id')}")
            
            return apps
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def main():
    """Función principal del script"""
    print("🚀 SCRIPT PARA SUSCRIBIR APP DE NORA A META WEBHOOKS")
    print("=" * 60)
    
    # Obtener credenciales
    credenciales = obtener_credenciales()
    
    if not all([credenciales['app_id'], credenciales['app_secret'], credenciales['access_token']]):
        print("❌ ERROR: Faltan credenciales necesarias")
        return
    
    # Paso 1: Suscribir app a webhooks
    print("\n" + "=" * 60)
    if suscribir_app_a_webhooks(credenciales):
        print("✅ Paso 1 completado: App suscrita a webhooks")
    else:
        print("❌ Paso 1 falló: No se pudo suscribir la app")
        return
    
    # Verificar suscripción de la app
    print("\n" + "=" * 60)
    if verificar_suscripcion_app(credenciales):
        print("✅ Verificación: App correctamente suscrita a adaccounts")
    else:
        print("⚠️ Verificación: App no está suscrita a adaccounts")
    
    # Paso 2: Suscribir cuentas publicitarias a la app
    print("\n" + "=" * 60)
    print("🎯 PASO 2: Suscribiendo cuentas publicitarias a la app")
    
    cuentas = obtener_cuentas_publicitarias()
    
    if not cuentas:
        print("⚠️ No se encontraron cuentas publicitarias")
        return
    
    exitosas = 0
    fallidas = 0
    
    for cuenta in cuentas:
        id_cuenta = cuenta['id_cuenta_publicitaria']
        nombre = cuenta['nombre_cliente']
        
        print(f"\n--- Procesando: {nombre} ({id_cuenta}) ---")
        
        if suscribir_cuenta_a_app(id_cuenta, credenciales['access_token'], credenciales['app_id']):
            exitosas += 1
            
            # Actualizar BD
            try:
                supabase.table('meta_ads_cuentas') \
                    .update({'webhook_registrado': True}) \
                    .eq('id_cuenta_publicitaria', id_cuenta) \
                    .execute()
                print(f"✅ BD actualizada para {nombre}")
            except Exception as e:
                print(f"⚠️ Error actualizando BD: {e}")
        else:
            fallidas += 1
        
        # Verificar suscripción
        apps_suscritas = verificar_suscripcion_cuenta(id_cuenta, credenciales['access_token'])
        app_encontrada = any(app.get('id') == credenciales['app_id'] for app in apps_suscritas)
        
        if app_encontrada:
            print(f"✅ Verificado: App {credenciales['app_id']} está suscrita a {nombre}")
        else:
            print(f"❌ Verificado: App {credenciales['app_id']} NO está suscrita a {nombre}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    print(f"✅ Cuentas suscritas exitosamente: {exitosas}")
    print(f"❌ Cuentas con errores: {fallidas}")
    print(f"📋 Total procesadas: {len(cuentas)}")
    
    if exitosas > 0:
        print("\n🎉 ¡Proceso completado! Las cuentas están suscritas a webhooks.")
        print("📍 Webhook URL configurada:", credenciales['webhook_url'])
        print("📍 Ahora deberías recibir eventos de Meta Ads en tiempo real.")
    else:
        print("\n⚠️ No se pudo suscribir ninguna cuenta. Revisa los errores anteriores.")

if __name__ == "__main__":
    main()
