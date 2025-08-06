#!/usr/bin/env python3
"""
Script para verificar el estado del webhook en Meta
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv('.env.local', override=True)  # Forzar recarga

def verificar_webhook_meta():
    """Verificar si el webhook está registrado en Meta"""
    
    access_token = os.getenv('META_ACCESS_TOKEN')
    app_id = os.getenv('META_APP_ID')
    app_secret = os.getenv('META_APP_SECRET')  # Esta es para Facebook API
    webhook_secret = os.getenv('META_WEBHOOK_SECRET')  # Esta es para webhook verification
    
    if not access_token or not app_id:
        print("❌ Error: META_ACCESS_TOKEN y META_APP_ID deben estar configurados")
        return
    
    print("🔍 Verificando configuración de webhook en Meta...")
    print(f"📱 App ID: {app_id}")
    print(f"🔑 Facebook App Secret: {'✅ Configurado' if app_secret else '❌ No configurado'}")
    print(f"🔐 Webhook Secret: {'✅ Configurado' if webhook_secret else '❌ No configurado'}")
    
    # Generar App Access Token
    app_access_token = f"{app_id}|{app_secret}"
    
    # URL para obtener información de webhooks de la app
    url = f"https://graph.facebook.com/v21.0/{app_id}/subscriptions"
    
    params = {
        'access_token': app_access_token
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
    webhook_secret = os.getenv('META_WEBHOOK_SECRET')
    
    print(f"  🔗 META_WEBHOOK_URL: {webhook_url if webhook_url else '❌ No configurada'}")
    print(f"  🔑 META_WEBHOOK_VERIFY_TOKEN: {'✅ Configurada' if verify_token else '❌ No configurada'}")
    print(f"  🔐 META_WEBHOOK_SECRET: {'✅ Configurada' if webhook_secret else '❌ No configurada'}")
    
    # Verificar algunas páginas suscritas
    verificar_paginas_suscritas()

def verificar_paginas_suscritas():
    """Verificar algunas páginas que tienen webhooks suscritos"""
    print("\n📄 Verificando páginas con webhooks suscritos...")
    
    access_token = os.getenv('META_ACCESS_TOKEN')
    app_id = os.getenv('META_APP_ID')
    
    # Obtener algunas páginas para verificar
    url_accounts = f"https://graph.facebook.com/v21.0/me/accounts?access_token={access_token}"
    
    try:
        response = requests.get(url_accounts)
        data = response.json()
        
        if response.status_code == 200:
            pages = data.get('data', [])[:5]  # Solo verificar las primeras 5
            print(f"🔍 Verificando {len(pages)} páginas de muestra...")
            
            for page in pages:
                page_id = page.get('id')
                page_name = page.get('name')
                page_token = page.get('access_token')
                
                print(f"\n📄 {page_name} (ID: {page_id})")
                
                # Verificar aplicaciones suscritas
                url_subscribed = f"https://graph.facebook.com/v21.0/{page_id}/subscribed_apps?access_token={page_token}"
                
                try:
                    sub_response = requests.get(url_subscribed)
                    sub_data = sub_response.json()
                    
                    if sub_response.status_code == 200:
                        apps = sub_data.get('data', [])
                        app_encontrada = False
                        
                        for app in apps:
                            if app.get('id') == app_id:
                                print(f"   ✅ Webhook activo")
                                app_encontrada = True
                                break
                        
                        if not app_encontrada:
                            print(f"   ❌ Sin webhook")
                    else:
                        print(f"   ⚠️ Error verificando: {sub_data}")
                        
                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")
        else:
            print(f"❌ Error obteniendo páginas: {data}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    verificar_webhook_meta()
