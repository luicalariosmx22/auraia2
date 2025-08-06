#!/usr/bin/env python3
"""
Intento específico para obtener Page Access Token de Luica Larios
Probando diferentes métodos y endpoints
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env.local')

# Configuración
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
LUICA_LARIOS_PAGE_ID = "1669696123329079"

def metodo_1_accounts_directo():
    """Método 1: Buscar directamente en /me/accounts"""
    print("=" * 60)
    print("🔍 MÉTODO 1: Búsqueda directa en /me/accounts")
    print("=" * 60)
    
    url = f"https://graph.facebook.com/v21.0/me/accounts?fields=id,name,access_token&access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            pages = data.get('data', [])
            print(f"📊 Revisando {len(pages)} páginas...")
            
            for page in pages:
                if page.get('id') == LUICA_LARIOS_PAGE_ID:
                    print(f"🎯 ¡ENCONTRADA! {page.get('name')}")
                    page_token = page.get('access_token')
                    if page_token:
                        print(f"✅ Page Access Token: {page_token[:50]}...")
                        return page_token
                    else:
                        print(f"❌ Sin access_token en la respuesta")
                        return None
            
            print(f"❌ Página {LUICA_LARIOS_PAGE_ID} no encontrada en accounts")
        else:
            print(f"❌ Error: {data}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    return None

def metodo_2_acceso_directo_con_token():
    """Método 2: Intentar acceso directo a la página pidiendo access_token"""
    print("\n" + "=" * 60)
    print("🔍 MÉTODO 2: Acceso directo solicitando access_token")
    print("=" * 60)
    
    url = f"https://graph.facebook.com/v21.0/{LUICA_LARIOS_PAGE_ID}?fields=id,name,access_token&access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print(f"🌐 Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Página encontrada: {data.get('name')}")
            page_token = data.get('access_token')
            if page_token:
                print(f"🎯 ¡Page Access Token obtenido! {page_token[:50]}...")
                return page_token
            else:
                print(f"❌ Campo 'access_token' no disponible")
                print(f"   Campos recibidos: {list(data.keys())}")
        else:
            print(f"❌ Error: {data}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    return None

def metodo_3_generar_page_token():
    """Método 3: Intentar generar Page Access Token usando Graph API"""
    print("\n" + "=" * 60)
    print("🔍 MÉTODO 3: Generar Page Access Token via API")
    print("=" * 60)
    
    # Intentar obtener Page Access Token para una página específica
    url = f"https://graph.facebook.com/v21.0/{LUICA_LARIOS_PAGE_ID}/access_tokens?access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print(f"🌐 Status: {response.status_code}")
        
        if response.status_code == 200:
            tokens = data.get('data', [])
            if tokens:
                print(f"🎯 ¡Tokens encontrados!")
                for i, token_data in enumerate(tokens):
                    print(f"   Token {i+1}: {token_data.get('access_token', 'No disponible')[:50]}...")
                return tokens[0].get('access_token') if tokens else None
            else:
                print(f"❌ Sin tokens en la respuesta")
        else:
            print(f"❌ Error: {data}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    return None

def metodo_4_oauth_page_token():
    """Método 4: Intentar con endpoint específico de OAuth"""
    print("\n" + "=" * 60)
    print("🔍 MÉTODO 4: Endpoint OAuth para Page Token")
    print("=" * 60)
    
    # Algunos endpoints alternativos para Page Access Tokens
    endpoints = [
        f"https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id={os.getenv('META_APP_ID')}&client_secret={os.getenv('META_APP_SECRET')}&fb_exchange_token={META_ACCESS_TOKEN}",
        f"https://graph.facebook.com/v21.0/{LUICA_LARIOS_PAGE_ID}?fields=access_token&access_token={META_ACCESS_TOKEN}"
    ]
    
    for i, url in enumerate(endpoints, 1):
        print(f"\n🔄 Probando endpoint {i}...")
        try:
            response = requests.get(url)
            data = response.json()
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                if 'access_token' in data:
                    token = data.get('access_token')
                    print(f"   ✅ Token obtenido: {token[:50]}...")
                    return token
                else:
                    print(f"   ℹ️ Respuesta: {data}")
            else:
                print(f"   ❌ Error: {data}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    return None

def metodo_5_verificar_permisos_pagina():
    """Método 5: Verificar permisos específicos sobre la página"""
    print("\n" + "=" * 60)
    print("🔍 MÉTODO 5: Verificar permisos sobre la página")
    print("=" * 60)
    
    # Verificar si tenemos algún tipo de permiso sobre la página
    endpoints_permisos = [
        f"https://graph.facebook.com/v21.0/{LUICA_LARIOS_PAGE_ID}/roles?access_token={META_ACCESS_TOKEN}",
        f"https://graph.facebook.com/v21.0/{LUICA_LARIOS_PAGE_ID}/admins?access_token={META_ACCESS_TOKEN}",
        f"https://graph.facebook.com/v21.0/me/permissions?access_token={META_ACCESS_TOKEN}"
    ]
    
    for i, url in enumerate(endpoints_permisos, 1):
        print(f"\n🔄 Verificando endpoint {i}...")
        try:
            response = requests.get(url)
            data = response.json()
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Datos obtenidos: {data}")
            else:
                print(f"   ❌ Error: {data}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

def validar_page_token(page_token):
    """Validar si un Page Access Token funciona"""
    if not page_token:
        return False
    
    print(f"\n" + "=" * 60)
    print(f"🔍 VALIDANDO PAGE ACCESS TOKEN")
    print("=" * 60)
    
    # Probar el token obteniendo información de la página
    url = f"https://graph.facebook.com/v21.0/{LUICA_LARIOS_PAGE_ID}?fields=id,name,category&access_token={page_token}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print(f"🌐 Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Token válido!")
            print(f"   Página: {data.get('name')}")
            print(f"   ID: {data.get('id')}")
            print(f"   Categoría: {data.get('category')}")
            return True
        else:
            print(f"❌ Token inválido: {data}")
            return False
    except Exception as e:
        print(f"❌ Error validando token: {str(e)}")
        return False

def main():
    """Función principal - probar todos los métodos"""
    print("🎯 INTENTO ESPECÍFICO: OBTENER PAGE ACCESS TOKEN DE LUICA LARIOS")
    print("=" * 80)
    print(f"Página objetivo: Luica Larios (ID: {LUICA_LARIOS_PAGE_ID})")
    print("=" * 80)
    
    page_token = None
    
    # Probar método 1
    page_token = metodo_1_accounts_directo()
    if page_token:
        if validar_page_token(page_token):
            print(f"\n🎉 ¡ÉXITO! Page Access Token obtenido con Método 1")
            return page_token
    
    # Probar método 2
    page_token = metodo_2_acceso_directo_con_token()
    if page_token:
        if validar_page_token(page_token):
            print(f"\n🎉 ¡ÉXITO! Page Access Token obtenido con Método 2")
            return page_token
    
    # Probar método 3
    page_token = metodo_3_generar_page_token()
    if page_token:
        if validar_page_token(page_token):
            print(f"\n🎉 ¡ÉXITO! Page Access Token obtenido con Método 3")
            return page_token
    
    # Probar método 4
    page_token = metodo_4_oauth_page_token()
    if page_token:
        if validar_page_token(page_token):
            print(f"\n🎉 ¡ÉXITO! Page Access Token obtenido con Método 4")
            return page_token
    
    # Método 5 - solo verificación
    metodo_5_verificar_permisos_pagina()
    
    print(f"\n" + "=" * 80)
    print(f"❌ RESULTADO: No se pudo obtener Page Access Token")
    print(f"💡 Razón probable: El token actual no tiene permisos administrativos")
    print(f"   sobre la página 'Luica Larios' (ID: {LUICA_LARIOS_PAGE_ID})")
    print(f"🔧 Solución: Generar token desde la cuenta que administra la página")
    print("=" * 80)
    
    return None

if __name__ == "__main__":
    main()
