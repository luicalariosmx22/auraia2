#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para webhooks de Facebook Pages
Prueba suscripción básica con un solo campo
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def probar_webhook_una_pagina():
    """Prueba suscripción de webhook en una página específica"""
    
    user_token = os.getenv('META_ACCESS_TOKEN')
    if not user_token:
        print("❌ No se encontró META_ACCESS_TOKEN")
        return
    
    print("🧪 PRUEBA DE WEBHOOK EN UNA PÁGINA")
    print("=" * 40)
    
    try:
        # 1. Obtener lista de páginas
        print("1️⃣ Obteniendo páginas...")
        url = f"https://graph.facebook.com/v19.0/me/accounts"
        params = {
            'access_token': user_token,
            'fields': 'id,name,access_token,tasks'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Error obteniendo páginas: {response.status_code}")
            print(response.text)
            return
        
        pages = response.json().get('data', [])
        if not pages:
            print("❌ No se encontraron páginas")
            return
        
        # Tomar la primera página
        page = pages[0]
        page_id = page.get('id')
        page_name = page.get('name')
        page_token = page.get('access_token')
        
        print(f"✅ Página seleccionada: {page_name}")
        print(f"   ID: {page_id}")
        print(f"   Tareas: {page.get('tasks', [])}")
        
        if not page_token:
            print("❌ No se pudo obtener Page Access Token")
            return
        
        # 2. Verificar suscripciones actuales
        print(f"\n2️⃣ Verificando suscripciones actuales...")
        check_url = f"https://graph.facebook.com/v19.0/{page_id}/subscribed_apps"
        check_params = {'access_token': page_token}
        
        check_response = requests.get(check_url, params=check_params, timeout=10)
        
        if check_response.status_code == 200:
            subs_data = check_response.json()
            apps = subs_data.get('data', [])
            
            print(f"   Apps suscritas: {len(apps)}")
            for app in apps:
                print(f"   - App ID: {app.get('id')}")
                print(f"     Campos: {app.get('subscribed_fields', [])}")
        else:
            print(f"⚠️ Error verificando suscripciones: {check_response.status_code}")
            print(f"   {check_response.text}")
        
        # 3. Intentar suscripción básica con solo 'feed'
        print(f"\n3️⃣ Intentando suscripción básica (solo 'feed')...")
        webhook_url = f"https://graph.facebook.com/v19.0/{page_id}/subscribed_apps"
        webhook_data = {
            'access_token': page_token,
            'subscribed_fields': 'feed'  # Solo el campo más básico
        }
        
        webhook_response = requests.post(webhook_url, data=webhook_data, timeout=10)
        
        print(f"   Status: {webhook_response.status_code}")
        
        if webhook_response.status_code == 200:
            result = webhook_response.json()
            print(f"   ✅ Suscripción exitosa: {result}")
            
            # Verificar de nuevo
            print(f"\n4️⃣ Verificando suscripción después del POST...")
            check_response2 = requests.get(check_url, params=check_params, timeout=10)
            if check_response2.status_code == 200:
                subs_data2 = check_response2.json()
                apps2 = subs_data2.get('data', [])
                print(f"   Apps suscritas ahora: {len(apps2)}")
                for app in apps2:
                    print(f"   - App ID: {app.get('id')}")
                    print(f"     Campos: {app.get('subscribed_fields', [])}")
            
        else:
            print(f"   ❌ Error en suscripción: {webhook_response.text}")
            
            # Si falla con 'feed', probar sin campos (aunque debería fallar)
            print(f"\n🧪 Probando sin campos (debería fallar)...")
            webhook_data_empty = {
                'access_token': page_token
                # Sin subscribed_fields
            }
            
            webhook_response2 = requests.post(webhook_url, data=webhook_data_empty, timeout=10)
            print(f"   Status sin campos: {webhook_response2.status_code}")
            print(f"   Respuesta: {webhook_response2.text}")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def mostrar_permisos_necesarios():
    """Muestra los permisos que se necesitan para diferentes campos"""
    print("\n📋 CAMPOS Y PERMISOS NECESARIOS:")
    print("=" * 35)
    
    campos_permisos = {
        'feed': 'pages_manage_metadata',
        'mention': 'pages_manage_metadata', 
        'messages': 'pages_messaging',
        'messaging_postbacks': 'pages_messaging',
        'messaging_optins': 'pages_messaging',
        'message_reads': 'pages_messaging',
        'messaging_referrals': 'pages_messaging',
        'videos': 'pages_manage_metadata',
        'website': 'pages_manage_metadata'
    }
    
    for campo, permiso in campos_permisos.items():
        print(f"   {campo:<20} → {permiso}")
    
    print(f"\n💡 ESTRATEGIA:")
    print(f"   1. Primero probar con 'feed' (requiere pages_manage_metadata)")
    print(f"   2. Si falla, el User Token necesita más permisos")
    print(f"   3. Una vez que funcione 'feed', agregar más campos")

if __name__ == "__main__":
    mostrar_permisos_necesarios()
    probar_webhook_una_pagina()
