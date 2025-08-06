#!/usr/bin/env python3
"""
Investigación profunda de la página Luica Larios
Verificar por qué no aparece en páginas administradas si es tuya
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env.local')

# Configuración
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
LUICA_LARIOS_PAGE_ID = "1669696123329079"

def verificar_token_actual():
    """Verificar información del token actual"""
    print("=" * 60)
    print("🔍 VERIFICANDO TOKEN ACTUAL")
    print("=" * 60)
    
    url = f"https://graph.facebook.com/v21.0/me?access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            print(f"✅ Token válido para usuario: {data.get('name')} (ID: {data.get('id')})")
            return data.get('id')
        else:
            print(f"❌ Error en token: {data}")
            return None
            
    except Exception as e:
        print(f"❌ Error verificando token: {str(e)}")
        return None

def verificar_permisos_token():
    """Verificar qué permisos tiene el token actual"""
    print("\n" + "=" * 60)
    print("🔐 VERIFICANDO PERMISOS DEL TOKEN")
    print("=" * 60)
    
    url = f"https://graph.facebook.com/v21.0/me/permissions?access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            print("📋 Permisos del token:")
            for permission in data.get('data', []):
                status = permission.get('status')
                permission_name = permission.get('permission')
                icon = "✅" if status == 'granted' else "❌"
                print(f"  {icon} {permission_name}: {status}")
        else:
            print(f"❌ Error obteniendo permisos: {data}")
            
    except Exception as e:
        print(f"❌ Error verificando permisos: {str(e)}")

def buscar_pagina_en_cuentas():
    """Buscar la página Luica Larios en diferentes endpoints"""
    print("\n" + "=" * 60)
    print("🔍 BUSCANDO PÁGINA EN DIFERENTES ENDPOINTS")
    print("=" * 60)
    
    # 1. Buscar en /me/accounts (páginas administradas)
    print("\n🏢 Buscando en /me/accounts...")
    url_accounts = f"https://graph.facebook.com/v21.0/me/accounts?access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url_accounts)
        data = response.json()
        
        if response.status_code == 200:
            pages = data.get('data', [])
            print(f"📊 Total de páginas en /me/accounts: {len(pages)}")
            
            luica_found = False
            for page in pages:
                if page.get('id') == LUICA_LARIOS_PAGE_ID or 'luica' in page.get('name', '').lower():
                    print(f"  ✅ ENCONTRADA: {page.get('name')} (ID: {page.get('id')})")
                    print(f"     - Categoría: {page.get('category')}")
                    print(f"     - Tareas: {page.get('tasks', [])}")
                    luica_found = True
            
            if not luica_found:
                print(f"  ❌ Luica Larios (ID: {LUICA_LARIOS_PAGE_ID}) NO encontrada en /me/accounts")
        else:
            print(f"❌ Error en /me/accounts: {data}")
            
    except Exception as e:
        print(f"❌ Error buscando en accounts: {str(e)}")
    
    # 2. Buscar en /me/pages (incluye páginas con diferentes roles)
    print("\n📄 Buscando en /me/pages...")
    url_pages = f"https://graph.facebook.com/v21.0/me/pages?access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url_pages)
        data = response.json()
        
        if response.status_code == 200:
            pages = data.get('data', [])
            print(f"📊 Total de páginas en /me/pages: {len(pages)}")
            
            luica_found = False
            for page in pages:
                if page.get('id') == LUICA_LARIOS_PAGE_ID or 'luica' in page.get('name', '').lower():
                    print(f"  ✅ ENCONTRADA: {page.get('name')} (ID: {page.get('id')})")
                    luica_found = True
            
            if not luica_found:
                print(f"  ❌ Luica Larios (ID: {LUICA_LARIOS_PAGE_ID}) NO encontrada en /me/pages")
        else:
            print(f"❌ Error en /me/pages: {data}")
            
    except Exception as e:
        print(f"❌ Error buscando en pages: {str(e)}")

def verificar_acceso_directo_detallado():
    """Verificar acceso directo a la página con más detalles"""
    print("\n" + "=" * 60)
    print("🔍 VERIFICACIÓN DETALLADA DE LA PÁGINA")
    print("=" * 60)
    
    # Campos detallados para obtener más información
    campos = "id,name,category,fan_count,access_token,roles,tasks,permissions"
    url = f"https://graph.facebook.com/v21.0/{LUICA_LARIOS_PAGE_ID}?fields={campos}&access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print(f"🌐 Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ ACCESO EXITOSO - Información de la página:")
            print(f"  📝 Nombre: {data.get('name')}")
            print(f"  🆔 ID: {data.get('id')}")
            print(f"  📂 Categoría: {data.get('category')}")
            print(f"  👥 Seguidores: {data.get('fan_count', 'No disponible')}")
            print(f"  🔑 Access Token: {'SÍ' if data.get('access_token') else 'NO'}")
            print(f"  👔 Roles: {data.get('roles', 'No disponible')}")
            print(f"  📋 Tareas: {data.get('tasks', 'No disponible')}")
            print(f"  🔐 Permisos: {data.get('permissions', 'No disponible')}")
        else:
            print(f"❌ ERROR en acceso directo:")
            print(f"   Código: {response.status_code}")
            print(f"   Mensaje: {data.get('error', {}).get('message', 'Sin mensaje')}")
            print(f"   Tipo: {data.get('error', {}).get('type', 'Sin tipo')}")
            
    except Exception as e:
        print(f"❌ Error en verificación detallada: {str(e)}")

def verificar_aplicacion_facebook():
    """Verificar configuración de la aplicación de Facebook"""
    print("\n" + "=" * 60)
    print("📱 VERIFICANDO APLICACIÓN DE FACEBOOK")
    print("=" * 60)
    
    app_id = os.getenv('META_APP_ID')
    url = f"https://graph.facebook.com/v21.0/{app_id}?access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            print("✅ Información de la aplicación:")
            print(f"  📱 Nombre: {data.get('name')}")
            print(f"  🆔 ID: {data.get('id')}")
            print(f"  📂 Categoría: {data.get('category')}")
            print(f"  🌐 Dominio: {data.get('app_domains', [])}")
        else:
            print(f"❌ Error verificando aplicación: {data}")
            
    except Exception as e:
        print(f"❌ Error verificando aplicación: {str(e)}")

def main():
    """Función principal de investigación"""
    print("🔍 INVESTIGACIÓN PROFUNDA: PÁGINA LUICA LARIOS")
    print("=" * 80)
    
    # 1. Verificar token actual
    user_id = verificar_token_actual()
    
    # 2. Verificar permisos
    verificar_permisos_token()
    
    # 3. Buscar página en diferentes endpoints
    buscar_pagina_en_cuentas()
    
    # 4. Verificación detallada de la página
    verificar_acceso_directo_detallado()
    
    # 5. Verificar aplicación
    verificar_aplicacion_facebook()
    
    print("\n" + "=" * 80)
    print("💡 POSIBLES CAUSAS SI LA PÁGINA NO APARECE:")
    print("   1. Token generado desde cuenta diferente a la propietaria")
    print("   2. Página asociada a cuenta personal vs cuenta business")
    print("   3. Permisos insuficientes en la aplicación Facebook")
    print("   4. Configuración de roles en la página")
    print("   5. Token de User Access vs Page Access")
    print("=" * 80)

if __name__ == "__main__":
    main()
