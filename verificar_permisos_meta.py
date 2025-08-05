#!/usr/bin/env python3
"""
Script para verificar permisos del token de Meta y probar acceso a audiencias
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

def verificar_token_permisos():
    """Verifica los permisos del token actual"""
    try:
        import requests
        
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            print("❌ No se encontró META_ACCESS_TOKEN")
            return False
            
        print(f"✅ Token encontrado: {access_token[:20]}...")
        
        # Verificar permisos del token
        url = "https://graph.facebook.com/v19.0/me/permissions"
        params = {'access_token': access_token}
        
        response = requests.get(url, params=params, timeout=10)
        print(f"📡 Status verificación permisos: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            permisos = data.get('data', [])
            print(f"🔐 Permisos encontrados: {len(permisos)}")
            
            permisos_importantes = [
                'ads_read', 'ads_management', 'business_management',
                'pages_read_engagement', 'pages_manage_ads'
            ]
            
            permisos_activos = []
            for permiso in permisos:
                nombre = permiso.get('permission', '')
                estado = permiso.get('status', '')
                print(f"   - {nombre}: {estado}")
                
                if estado == 'granted' and nombre in permisos_importantes:
                    permisos_activos.append(nombre)
            
            print(f"\n✅ Permisos importantes activos: {permisos_activos}")
            
            # Verificar si tiene permisos para audiencias
            if 'ads_read' in permisos_activos or 'ads_management' in permisos_activos:
                print("✅ Token tiene permisos para leer datos de anuncios")
            else:
                print("❌ Token NO tiene permisos para leer datos de anuncios")
                
            return True
        else:
            print(f"❌ Error verificando permisos: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Error verificando permisos: {e}")
        return False

def probar_acceso_cuenta_simple(cuenta_id):
    """Prueba acceso básico a una cuenta publicitaria"""
    try:
        import requests
        
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            return False
            
        # Limpiar el prefijo 'act_' si existe
        if cuenta_id.startswith('act_'):
            cuenta_id = cuenta_id[4:]
            
        # Probar acceso básico a la cuenta
        url = f"https://graph.facebook.com/v19.0/act_{cuenta_id}"
        params = {
            'access_token': access_token,
            'fields': 'id,name,account_status,business'
        }
        
        print(f"\n🔍 Probando acceso básico a cuenta: {cuenta_id}")
        response = requests.get(url, params=params, timeout=10)
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Acceso exitoso a cuenta:")
            print(f"   - ID: {data.get('id')}")
            print(f"   - Nombre: {data.get('name', 'N/A')}")
            print(f"   - Estado: {data.get('account_status', 'N/A')}")
            return True
        else:
            print(f"❌ Error accediendo a cuenta: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Error probando acceso a cuenta: {e}")
        return False

def probar_endpoints_alternativos(cuenta_id):
    """Prueba endpoints alternativos que podrían funcionar"""
    try:
        import requests
        
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            return False
            
        # Limpiar el prefijo 'act_' si existe
        if cuenta_id.startswith('act_'):
            cuenta_id = cuenta_id[4:]
        
        # Lista de endpoints alternativos para probar
        endpoints_alternativos = [
            {
                'name': 'Saved Audiences',
                'url': f"https://graph.facebook.com/v19.0/act_{cuenta_id}/saved_audiences",
                'fields': 'id,name,description,approximate_count'
            },
            {
                'name': 'Targeting Search',
                'url': f"https://graph.facebook.com/v19.0/act_{cuenta_id}/targetingsearch",
                'fields': 'type,name,path'
            },
            {
                'name': 'Ads (para ver si hay datos)',
                'url': f"https://graph.facebook.com/v19.0/act_{cuenta_id}/ads",
                'fields': 'id,name,status'
            }
        ]
        
        for endpoint in endpoints_alternativos:
            print(f"\n🔍 Probando {endpoint['name']}:")
            
            params = {
                'access_token': access_token,
                'fields': endpoint['fields'],
                'limit': 5
            }
            
            response = requests.get(endpoint['url'], params=params, timeout=10)
            print(f"📡 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('data', [])
                print(f"✅ {endpoint['name']}: {len(items)} elementos encontrados")
                
                for item in items[:3]:  # Mostrar solo los primeros 3
                    print(f"   - {item.get('id')}: {item.get('name', 'Sin nombre')}")
            else:
                print(f"❌ Error en {endpoint['name']}: {response.text[:200]}")
                
    except Exception as e:
        print(f"💥 Error probando endpoints alternativos: {e}")

def verificar_version_api():
    """Verifica si la versión de la API es correcta"""
    try:
        import requests
        
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            return False
        
        # Probar diferentes versiones de la API
        versiones = ['v19.0', 'v18.0', 'v17.0']
        
        for version in versiones:
            print(f"\n🔍 Probando API versión {version}:")
            
            url = f"https://graph.facebook.com/{version}/me"
            params = {'access_token': access_token}
            
            response = requests.get(url, params=params, timeout=5)
            print(f"📡 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Versión {version} funciona - Usuario: {data.get('name', 'N/A')}")
            else:
                print(f"❌ Versión {version} falla: {response.text[:100]}")
                
    except Exception as e:
        print(f"💥 Error verificando versiones API: {e}")

if __name__ == "__main__":
    print("🔐 VERIFICACIÓN DE PERMISOS Y ACCESO META ADS")
    print("=" * 60)
    
    # 1. Verificar permisos del token
    print("\n1. Verificando permisos del token...")
    verificar_token_permisos()
    
    # 2. Verificar versiones de API
    print("\n2. Verificando versiones de API...")
    verificar_version_api()
    
    # 3. Probar acceso a una cuenta específica
    print("\n3. Probando acceso a cuenta específica...")
    cuenta_test = "26907830"  # Primera cuenta que falló
    if probar_acceso_cuenta_simple(cuenta_test):
        print("\n4. Probando endpoints alternativos...")
        probar_endpoints_alternativos(cuenta_test)
    
    print("\n" + "=" * 60)
    print("🔍 DIAGNÓSTICO:")
    print("- Si el token no tiene permisos 'ads_read' o 'ads_management', necesitas regenerarlo")
    print("- Si no puedes acceder a la cuenta, revisa si el token fue creado con los permisos correctos")
    print("- Las audiencias personalizadas requieren permisos especiales de Business Manager")
    print("- Considera usar 'saved_audiences' en lugar de 'customaudiences' si no tienes permisos")
