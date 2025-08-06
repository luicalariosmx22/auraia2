#!/usr/bin/env python3
"""
Prueba simplificada para acceder a la página Luica Larios
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env.local')

# Configuración
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
LUICA_LARIOS_PAGE_ID = "1669696123329079"

def listar_todas_las_paginas():
    """Listar todas las páginas administradas con nombres"""
    print("=" * 60)
    print("📋 LISTANDO TODAS LAS PÁGINAS ADMINISTRADAS")
    print("=" * 60)
    
    url = f"https://graph.facebook.com/v21.0/me/accounts?access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            pages = data.get('data', [])
            print(f"📊 Total de páginas: {len(pages)}")
            print("\n🏢 Páginas encontradas:")
            
            for i, page in enumerate(pages, 1):
                name = page.get('name', 'Sin nombre')
                page_id = page.get('id')
                category = page.get('category', 'Sin categoría')
                
                # Marcar si contiene "luica" o "larios"
                is_luica = any(term in name.lower() for term in ['luica', 'larios'])
                marker = "⭐ POSIBLE MATCH: " if is_luica else "   "
                
                print(f"{marker}{i:2d}. {name} (ID: {page_id})")
                print(f"       Categoría: {category}")
                
                if page_id == LUICA_LARIOS_PAGE_ID:
                    print(f"       🎯 ¡ESTA ES LUICA LARIOS!")
                print()
        else:
            print(f"❌ Error: {data}")
            
    except Exception as e:
        print(f"❌ Error listando páginas: {str(e)}")

def acceso_simple_luica():
    """Acceso simple a la página Luica Larios"""
    print("=" * 60)
    print("🔍 ACCESO SIMPLE A LUICA LARIOS")
    print("=" * 60)
    
    # Solo campos básicos que sabemos que funcionan
    campos = "id,name,category,fan_count"
    url = f"https://graph.facebook.com/v21.0/{LUICA_LARIOS_PAGE_ID}?fields={campos}&access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print(f"🌐 Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ ACCESO EXITOSO:")
            print(f"  📝 Nombre: {data.get('name')}")
            print(f"  🆔 ID: {data.get('id')}")
            print(f"  📂 Categoría: {data.get('category')}")
            print(f"  👥 Seguidores: {data.get('fan_count', 'No disponible')}")
        else:
            print(f"❌ ERROR:")
            print(f"   Código: {response.status_code}")
            print(f"   Mensaje: {data}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def intentar_obtener_page_access_token():
    """Intentar obtener Page Access Token directamente"""
    print("\n" + "=" * 60)
    print("🔑 INTENTANDO OBTENER PAGE ACCESS TOKEN")
    print("=" * 60)
    
    # Primero verificar si la página está en accounts con access_token
    url = f"https://graph.facebook.com/v21.0/me/accounts?fields=id,name,access_token&access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            pages = data.get('data', [])
            
            for page in pages:
                if page.get('id') == LUICA_LARIOS_PAGE_ID:
                    print(f"🎯 ¡PÁGINA ENCONTRADA EN ACCOUNTS!")
                    print(f"   Nombre: {page.get('name')}")
                    print(f"   ID: {page.get('id')}")
                    print(f"   Page Access Token: {'SÍ' if page.get('access_token') else 'NO'}")
                    return page.get('access_token')
            
            print("❌ Página no encontrada en /me/accounts")
        else:
            print(f"❌ Error obteniendo accounts: {data}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    return None

def buscar_por_nombre():
    """Buscar páginas que contengan 'luica' o 'larios' en el nombre"""
    print("\n" + "=" * 60)
    print("🔍 BUSCANDO POR NOMBRE (LUICA/LARIOS)")
    print("=" * 60)
    
    url = f"https://graph.facebook.com/v21.0/me/accounts?access_token={META_ACCESS_TOKEN}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            pages = data.get('data', [])
            matches = []
            
            for page in pages:
                name = page.get('name', '').lower()
                if 'luica' in name or 'larios' in name:
                    matches.append(page)
            
            if matches:
                print(f"🎯 Encontradas {len(matches)} páginas con 'luica' o 'larios':")
                for page in matches:
                    print(f"  📝 {page.get('name')} (ID: {page.get('id')})")
            else:
                print("❌ No se encontraron páginas con 'luica' o 'larios' en el nombre")
        else:
            print(f"❌ Error: {data}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Función principal"""
    print("🔍 INVESTIGACIÓN SIMPLIFICADA: LUICA LARIOS")
    print("=" * 80)
    
    # 1. Listar todas las páginas
    listar_todas_las_paginas()
    
    # 2. Buscar por nombre
    buscar_por_nombre()
    
    # 3. Acceso simple a la página
    acceso_simple_luica()
    
    # 4. Intentar obtener Page Access Token
    page_token = intentar_obtener_page_access_token()
    
    if page_token:
        print(f"\n✅ Page Access Token obtenido: {page_token[:50]}...")
    else:
        print(f"\n❌ No se pudo obtener Page Access Token")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
