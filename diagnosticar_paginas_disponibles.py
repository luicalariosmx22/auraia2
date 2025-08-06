#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para diagnosticar qué páginas están disponibles con el token actual
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def obtener_access_token():
    """Obtiene el access token desde variables de entorno"""
    return os.getenv('META_ACCESS_TOKEN')

def verificar_permisos_token():
    """Verifica qué permisos tiene el token actual"""
    access_token = obtener_access_token()
    if not access_token:
        print("❌ No se encontró META_ACCESS_TOKEN")
        return
    
    print("🔍 VERIFICANDO PERMISOS DEL TOKEN")
    print("=" * 50)
    
    try:
        url = "https://graph.facebook.com/v19.0/me/permissions"
        params = {'access_token': access_token}
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            permisos = data.get('data', [])
            
            print(f"✅ Token válido - {len(permisos)} permisos encontrados:")
            print()
            
            permisos_concedidos = []
            permisos_denegados = []
            
            for permiso in permisos:
                nombre = permiso.get('permission', 'desconocido')
                estado = permiso.get('status', 'desconocido')
                
                if estado == 'granted':
                    permisos_concedidos.append(nombre)
                    print(f"  ✅ {nombre}")
                else:
                    permisos_denegados.append(nombre)
                    print(f"  ❌ {nombre} ({estado})")
            
            print(f"\n📊 RESUMEN:")
            print(f"  ✅ Concedidos: {len(permisos_concedidos)}")
            print(f"  ❌ Denegados: {len(permisos_denegados)}")
            
            # Verificar permisos críticos para páginas
            permisos_necesarios = ['pages_manage_metadata', 'pages_messaging', 'pages_read_engagement']
            
            print(f"\n🎯 PERMISOS NECESARIOS PARA PÁGINAS:")
            for permiso in permisos_necesarios:
                if permiso in permisos_concedidos:
                    print(f"  ✅ {permiso}")
                else:
                    print(f"  ❌ {permiso} - FALTA")
            
        else:
            print(f"❌ Error verificando permisos: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def listar_paginas_disponibles():
    """Lista las páginas disponibles con el token actual"""
    access_token = obtener_access_token()
    if not access_token:
        print("❌ No se encontró META_ACCESS_TOKEN")
        return
    
    print("\n🏢 PÁGINAS DISPONIBLES CON EL TOKEN ACTUAL")
    print("=" * 60)
    
    try:
        url = "https://graph.facebook.com/v19.0/me/accounts"
        params = {
            'access_token': access_token,
            'fields': 'id,name,access_token,category,about,followers_count'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            pages = data.get('data', [])
            
            if pages:
                print(f"✅ {len(pages)} páginas disponibles:")
                print()
                
                for i, page in enumerate(pages, 1):
                    page_id = page.get('id', 'N/A')
                    name = page.get('name', 'Sin nombre')
                    category = page.get('category', 'Sin categoría')
                    followers = page.get('followers_count', 0)
                    has_token = '✅' if page.get('access_token') else '❌'
                    
                    print(f"{i:2d}. {name}")
                    print(f"     📋 ID: {page_id}")
                    print(f"     📂 Categoría: {category}")
                    print(f"     👥 Seguidores: {followers:,}")
                    print(f"     🎟️ Page Token: {has_token}")
                    print()
            else:
                print("❌ No se encontraron páginas disponibles")
                print("💡 Esto significa que el token NO tiene acceso a ninguna página")
                
        else:
            print(f"❌ Error obteniendo páginas: {response.status_code}")
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'message': response.text}
            print(f"   Detalles: {error_data}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def verificar_pagina_especifica(page_id):
    """Verifica si tenemos acceso a una página específica"""
    access_token = obtener_access_token()
    if not access_token:
        return False
    
    try:
        url = f"https://graph.facebook.com/v19.0/{page_id}"
        params = {
            'access_token': access_token,
            'fields': 'id,name,category'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Acceso a página {page_id}: {data.get('name', 'Sin nombre')}")
            return True
        else:
            print(f"❌ Sin acceso a página {page_id}: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando página {page_id}: {e}")
        return False

def probar_paginas_muestra():
    """Prueba acceso a algunas páginas de muestra de nuestra base de datos"""
    print("\n🧪 PROBANDO ACCESO A PÁGINAS DE MUESTRA")
    print("=" * 50)
    
    # Páginas de muestra que sabemos que están en la base de datos
    paginas_muestra = [
        ("721485141037304", "Desiertontos"),
        ("701218573066130", "Vetenvan"),
        ("708497639015320", "Adora Tulum"),
        ("332165499972137", "ChekoMgoficial"),
        ("494300117096126", "Yusef Escultor de Siluetas HMO")
    ]
    
    accesibles = 0
    total = len(paginas_muestra)
    
    for page_id, nombre in paginas_muestra:
        print(f"\n🔍 Probando: {nombre} ({page_id})")
        if verificar_pagina_especifica(page_id):
            accesibles += 1
    
    print(f"\n📊 RESULTADO:")
    print(f"  ✅ Páginas accesibles: {accesibles}/{total}")
    print(f"  ❌ Páginas sin acceso: {total - accesibles}/{total}")
    
    if accesibles == 0:
        print(f"\n⚠️ PROBLEMA IDENTIFICADO:")
        print(f"  El token actual NO tiene acceso a NINGUNA página")
        print(f"  Necesitas generar un nuevo token con los permisos correctos")

def main():
    """Función principal"""
    print("🚀 DIAGNÓSTICO DE PÁGINAS DE FACEBOOK")
    print("=" * 60)
    
    # Verificar permisos del token
    verificar_permisos_token()
    
    # Listar páginas disponibles
    listar_paginas_disponibles()
    
    # Probar páginas específicas
    probar_paginas_muestra()
    
    print("\n" + "=" * 60)
    print("🏁 DIAGNÓSTICO COMPLETADO")

if __name__ == "__main__":
    main()
