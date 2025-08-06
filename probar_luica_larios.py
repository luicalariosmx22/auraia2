#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para probar suscripción de webhook en una página específica que marca error
Página de prueba: Luica Larios (ID: 1669696123329079)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
from datetime import datetime
from dotenv import load_dotenv
from clientes.aura.utils.supabase_client import supabase

# Cargar variables de entorno
load_dotenv()

def obtener_access_token():
    """Obtiene el access token desde variables de entorno"""
    return os.getenv('META_ACCESS_TOKEN')

def obtener_webhook_url():
    """Obtiene la URL del webhook desde variables de entorno"""
    return os.getenv('META_WEBHOOK_URL')

def obtener_verify_token():
    """Obtiene el verify token desde variables de entorno"""
    return os.getenv('META_WEBHOOK_VERIFY_TOKEN')

def verificar_acceso_directo_pagina(page_id, access_token):
    """
    Verifica si tenemos acceso directo a la página usando el User Access Token
    """
    print(f"🔍 Verificando acceso directo a página {page_id}...")
    
    try:
        # Intentar acceder directamente a la información de la página
        url = f"https://graph.facebook.com/v19.0/{page_id}"
        params = {
            'access_token': access_token,
            'fields': 'id,name,category,about,followers_count'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        print(f"📊 Respuesta HTTP: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ACCESO DIRECTO EXITOSO:")
            print(f"   📋 Nombre: {data.get('name', 'N/A')}")
            print(f"   📂 Categoría: {data.get('category', 'N/A')}")
            print(f"   👥 Seguidores: {data.get('followers_count', 'N/A')}")
            return True, data
        else:
            try:
                error_data = response.json()
                print(f"❌ ACCESO DIRECTO FALLIDO:")
                print(f"   🔴 Error: {error_data}")
                return False, error_data
            except:
                print(f"❌ ACCESO DIRECTO FALLIDO:")
                print(f"   🔴 Error: {response.text}")
                return False, {'error': response.text}
                
    except Exception as e:
        print(f"❌ Error en verificación directa: {e}")
        return False, {'error': str(e)}

def obtener_page_access_token(page_id, user_access_token):
    """
    Intenta obtener el Page Access Token para la página
    """
    print(f"🎟️ Buscando Page Access Token para página {page_id}...")
    
    try:
        url = f"https://graph.facebook.com/v19.0/me/accounts"
        params = {
            'access_token': user_access_token,
            'fields': 'id,name,access_token,category'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            pages = data.get('data', [])
            
            print(f"📋 Páginas disponibles con el token: {len(pages)}")
            
            # Buscar la página específica
            for page in pages:
                if page.get('id') == page_id:
                    print(f"✅ ¡PÁGINA ENCONTRADA!")
                    print(f"   📋 Nombre: {page.get('name', 'N/A')}")
                    print(f"   📂 Categoría: {page.get('category', 'N/A')}")
                    return page.get('access_token')
            
            print(f"❌ Página {page_id} NO está en la lista de páginas disponibles")
            print(f"💡 Páginas disponibles:")
            for i, page in enumerate(pages[:5], 1):  # Mostrar solo las primeras 5
                print(f"   {i}. {page.get('name', 'Sin nombre')} (ID: {page.get('id')})")
            if len(pages) > 5:
                print(f"   ... y {len(pages) - 5} más")
            
            return None
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'message': response.text}
            print(f"❌ Error obteniendo lista de páginas: {response.status_code}")
            print(f"   🔴 Detalles: {error_data}")
            return None
            
    except Exception as e:
        print(f"❌ Error obteniendo Page Access Token: {e}")
        return None

def intentar_suscripcion_webhook(page_id, user_access_token, webhook_url, verify_token):
    """
    Intenta suscribir webhook para la página específica
    """
    print(f"📡 Intentando suscribir webhook para página {page_id}...")
    
    # Primero intentar obtener Page Access Token
    page_access_token = obtener_page_access_token(page_id, user_access_token)
    
    if not page_access_token:
        print(f"❌ No se pudo obtener Page Access Token - no es posible suscribir webhook")
        return False
    
    print(f"✅ Page Access Token obtenido exitosamente")
    
    try:
        # Intentar suscribir webhook
        url = f"https://graph.facebook.com/v19.0/{page_id}/subscribed_apps"
        
        data = {
            'access_token': page_access_token,
            'subscribed_fields': 'feed'
        }
        
        response = requests.post(url, data=data, timeout=30)
        
        print(f"📊 Respuesta de suscripción: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success', False):
                print(f"✅ ¡WEBHOOK SUSCRITO EXITOSAMENTE!")
                return True
            else:
                print(f"⚠️ Respuesta inesperada: {result}")
                return False
        else:
            try:
                error_data = response.json()
                print(f"❌ ERROR EN SUSCRIPCIÓN:")
                print(f"   🔴 Error: {error_data}")
                return False
            except:
                print(f"❌ ERROR EN SUSCRIPCIÓN:")
                print(f"   🔴 Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error en suscripción: {e}")
        return False

def main():
    """Función principal para probar Luica Larios"""
    print("🧪 PRUEBA ESPECÍFICA: LUICA LARIOS")
    print("=" * 50)
    
    # Información de la página que vamos a probar
    page_id = "1669696123329079"
    page_name = "Luica Larios"
    
    print(f"🎯 Página objetivo: {page_name}")
    print(f"📋 Page ID: {page_id}")
    print(f"🔴 Estado esperado: ERROR (según análisis previo)")
    
    # Verificar tokens y configuración
    access_token = obtener_access_token()
    if not access_token:
        print("❌ Access token no configurado")
        return
    
    webhook_url = obtener_webhook_url()
    verify_token = obtener_verify_token()
    
    print(f"✅ Access token configurado")
    print(f"✅ Webhook URL: {webhook_url}")
    print(f"✅ Verify token configurado")
    
    print(f"\n" + "=" * 50)
    print(f"🔍 PASO 1: VERIFICACIÓN DE ACCESO DIRECTO")
    print(f"=" * 50)
    
    # Verificar acceso directo a la página
    acceso_directo, info_directa = verificar_acceso_directo_pagina(page_id, access_token)
    
    print(f"\n" + "=" * 50)
    print(f"🎟️ PASO 2: BÚSQUEDA DE PAGE ACCESS TOKEN")
    print(f"=" * 50)
    
    # Intentar obtener Page Access Token
    page_token = obtener_page_access_token(page_id, access_token)
    
    print(f"\n" + "=" * 50)
    print(f"📡 PASO 3: INTENTO DE SUSCRIPCIÓN DE WEBHOOK")
    print(f"=" * 50)
    
    # Intentar suscribir webhook
    if page_token:
        webhook_exitoso = intentar_suscripcion_webhook(page_id, access_token, webhook_url, verify_token)
    else:
        print(f"⏭️ Saltando suscripción - no hay Page Access Token disponible")
        webhook_exitoso = False
    
    print(f"\n" + "=" * 50)
    print(f"📊 RESUMEN DE LA PRUEBA")
    print(f"=" * 50)
    print(f"🎯 Página: {page_name} ({page_id})")
    print(f"🔍 Acceso directo: {'✅ SÍ' if acceso_directo else '❌ NO'}")
    print(f"🎟️ Page Access Token: {'✅ SÍ' if page_token else '❌ NO'}")
    print(f"📡 Webhook suscrito: {'✅ SÍ' if webhook_exitoso else '❌ NO'}")
    
    print(f"\n💡 CONCLUSIÓN:")
    if not acceso_directo:
        print(f"🔴 El User Access Token NO tiene acceso a esta página")
        print(f"🔧 Solución: Necesitas un token con acceso a esta página específica")
    elif not page_token:
        print(f"🔴 La página no está disponible en las cuentas administradas")
        print(f"🔧 Solución: Verificar permisos de administración de la página")
    elif not webhook_exitoso:
        print(f"🔴 Error en la suscripción del webhook")
        print(f"🔧 Solución: Revisar permisos de webhook de la página")
    else:
        print(f"✅ ¡Todo funcionó correctamente!")

if __name__ == "__main__":
    main()
