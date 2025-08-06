#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para diagnosticar permisos y acceso a páginas de Facebook
"""

import os
import requests
from dotenv import load_dotenv

def diagnosticar_acceso_facebook():
    """Diagnostica qué acceso tiene el token actual"""
    
    load_dotenv()
    access_token = os.getenv('META_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ No se encontró META_ACCESS_TOKEN")
        return
    
    print("🔍 DIAGNÓSTICO DE ACCESO A FACEBOOK")
    print("=" * 50)
    
    # 1. Información del usuario/app actual
    print("\n1️⃣ Información del token:")
    try:
        response = requests.get(f"https://graph.facebook.com/v19.0/me", params={
            'access_token': access_token,
            'fields': 'id,name,email'
        })
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Usuario ID: {user_data.get('id')}")
            print(f"   👤 Nombre: {user_data.get('name')}")
            print(f"   📧 Email: {user_data.get('email', 'No disponible')}")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Permisos del token
    print("\n2️⃣ Permisos del token:")
    try:
        response = requests.get(f"https://graph.facebook.com/v19.0/me/permissions", params={
            'access_token': access_token
        })
        
        if response.status_code == 200:
            permisos = response.json().get('data', [])
            print(f"   📋 Total permisos: {len(permisos)}")
            
            permisos_concedidos = [p['permission'] for p in permisos if p['status'] == 'granted']
            permisos_denegados = [p['permission'] for p in permisos if p['status'] == 'declined']
            
            print(f"   ✅ Concedidos ({len(permisos_concedidos)}):")
            for permiso in permisos_concedidos:
                print(f"      • {permiso}")
            
            if permisos_denegados:
                print(f"   ❌ Denegados ({len(permisos_denegados)}):")
                for permiso in permisos_denegados:
                    print(f"      • {permiso}")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Intentar diferentes endpoints para páginas
    print("\n3️⃣ Intentando diferentes métodos para obtener páginas:")
    
    # Método 1: me/accounts (páginas que administras)
    print("\n   🔍 Método 1: me/accounts")
    try:
        response = requests.get(f"https://graph.facebook.com/v19.0/me/accounts", params={
            'access_token': access_token,
            'fields': 'id,name,category'
        })
        
        if response.status_code == 200:
            data = response.json()
            paginas = data.get('data', [])
            print(f"      📄 Páginas encontradas: {len(paginas)}")
            for pagina in paginas[:3]:  # Solo mostrar primeras 3
                print(f"         • {pagina.get('name')} (ID: {pagina.get('id')})")
        else:
            print(f"      ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"      ❌ Error: {e}")
    
    # Método 2: Verificar si el token es de app o usuario
    print("\n   🔍 Método 2: Información del token")
    try:
        response = requests.get(f"https://graph.facebook.com/v19.0/debug_token", params={
            'input_token': access_token,
            'access_token': access_token
        })
        
        if response.status_code == 200:
            token_info = response.json().get('data', {})
            print(f"      🔑 Tipo: {token_info.get('type', 'Desconocido')}")
            print(f"      📱 App ID: {token_info.get('app_id', 'Desconocido')}")
            print(f"      👤 User ID: {token_info.get('user_id', 'Desconocido')}")
            print(f"      ⏰ Expira: {token_info.get('expires_at', 'No expira')}")
            
            scopes = token_info.get('scopes', [])
            print(f"      🎯 Scopes: {', '.join(scopes) if scopes else 'Ninguno'}")
        else:
            print(f"      ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"      ❌ Error: {e}")
    
    # 4. Verificar Business Manager
    print("\n4️⃣ Verificando acceso a Business Manager:")
    try:
        response = requests.get(f"https://graph.facebook.com/v19.0/me/businesses", params={
            'access_token': access_token,
            'fields': 'id,name'
        })
        
        if response.status_code == 200:
            businesses = response.json().get('data', [])
            print(f"   🏢 Business Managers: {len(businesses)}")
            for business in businesses:
                print(f"      • {business.get('name')} (ID: {business.get('id')})")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n{'='*50}")
    print("🎯 RECOMENDACIONES:")
    print("1. Si no ves páginas, verifica que estés usando el token correcto")
    print("2. Las páginas deben estar en el mismo Business Manager que las cuentas de ads")
    print("3. El token debe tener permisos 'pages_read_engagement' y 'pages_show_list'")
    print("4. Si las páginas están en otra cuenta, necesitas un token de esa cuenta")

if __name__ == "__main__":
    diagnosticar_acceso_facebook()
