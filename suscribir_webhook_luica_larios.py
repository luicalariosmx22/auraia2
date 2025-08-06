#!/usr/bin/env python3
"""
Suscribir webhook específicamente para la página Luica Larios
Usando el Page Access Token obtenido
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env.local')

# Configuración
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
LUICA_LARIOS_PAGE_ID = "1669696123329079"
WEBHOOK_URL = os.getenv('META_WEBHOOK_URL')

def obtener_page_access_token_luica():
    """Obtener el Page Access Token de Luica Larios"""
    print("=" * 60)
    print("🔑 OBTENIENDO PAGE ACCESS TOKEN DE LUICA LARIOS")
    print("=" * 60)
    
    url = f"https://graph.facebook.com/v21.0/{LUICA_LARIOS_PAGE_ID}?fields=id,name,access_token&access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            page_token = data.get('access_token')
            page_name = data.get('name')
            print(f"✅ Page Access Token obtenido para: {page_name}")
            print(f"   Token: {page_token[:50]}...")
            return page_token
        else:
            print(f"❌ Error obteniendo token: {data}")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def suscribir_webhook_luica_larios(page_token):
    """Suscribir webhook para la página Luica Larios"""
    print("\n" + "=" * 60)
    print("📡 SUSCRIBIENDO WEBHOOK PARA LUICA LARIOS")
    print("=" * 60)
    
    if not page_token:
        print("❌ No hay Page Access Token disponible")
        return False
    
    # Datos para la suscripción
    webhook_data = {
        'object': 'page',
        'callback_url': WEBHOOK_URL,
        'fields': 'feed',  # Campo simplificado
        'verify_token': os.getenv('META_WEBHOOK_VERIFY_TOKEN'),
        'access_token': page_token
    }
    
    url = f"https://graph.facebook.com/v21.0/{LUICA_LARIOS_PAGE_ID}/subscriptions"
    
    try:
        print(f"📡 Enviando suscripción...")
        print(f"   URL: {url}")
        print(f"   Webhook URL: {WEBHOOK_URL}")
        print(f"   Campo: feed")
        
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
            print(f"❌ Error en suscripción: {data}")
            return False
            
    except Exception as e:
        print(f"❌ Error suscribiendo webhook: {str(e)}")
        return False

def verificar_suscripcion_existente(page_token):
    """Verificar si ya existe una suscripción"""
    print("\n" + "=" * 60)
    print("🔍 VERIFICANDO SUSCRIPCIONES EXISTENTES")
    print("=" * 60)
    
    if not page_token:
        print("❌ No hay Page Access Token disponible")
        return
    
    url = f"https://graph.facebook.com/v21.0/{LUICA_LARIOS_PAGE_ID}/subscriptions?access_token={page_token}"
    
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
            else:
                print(f"   ℹ️ No hay suscripciones activas")
        else:
            print(f"❌ Error verificando suscripciones: {data}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def actualizar_base_datos():
    """Actualizar el estado en la base de datos"""
    print("\n" + "=" * 60)
    print("💾 ACTUALIZANDO BASE DE DATOS")
    print("=" * 60)
    
    # Importar Supabase
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
    print("🎯 SUSCRIPCIÓN ESPECÍFICA: WEBHOOK LUICA LARIOS")
    print("=" * 80)
    
    # 1. Obtener Page Access Token
    page_token = obtener_page_access_token_luica()
    
    if not page_token:
        print("\n❌ No se pudo obtener Page Access Token. Abortando.")
        return
    
    # 2. Verificar suscripciones existentes
    verificar_suscripcion_existente(page_token)
    
    # 3. Suscribir webhook
    exito = suscribir_webhook_luica_larios(page_token)
    
    # 4. Actualizar base de datos si fue exitoso
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
