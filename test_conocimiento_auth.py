#!/usr/bin/env python3
"""
🧪 TEST DE AUTENTICACIÓN PARA CONOCIMIENTO
==========================================
Script para probar la autenticación AJAX para los endpoints de conocimiento.
"""

import requests
import json
from urllib.parse import urljoin

# Configuración
BASE_URL = "http://localhost:5000"
HEADERS = {
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/json'
}

def test_conocimiento_sin_auth():
    """Probar endpoints sin autenticación - deben devolver 401"""
    print("🧪 PROBANDO ENDPOINTS SIN AUTENTICACIÓN")
    print("=" * 60)
    
    endpoints = [
        "/panel_cliente/aura/entrenar/bloques",
        "/admin/nora/aura/entrenar/bloques"
    ]
    
    session = requests.Session()
    
    for endpoint in endpoints:
        url = urljoin(BASE_URL, endpoint)
        print(f"\n🔗 Probando: {url}")
        print("-" * 40)
        
        try:
            response = session.get(url, headers=HEADERS)
            print(f"📊 Status: {response.status_code}")
            print(f"📊 Headers: {dict(response.headers)}")
            
            if response.status_code == 401:
                try:
                    data = response.json()
                    print("✅ Devuelve JSON de error como esperado:")
                    print(f"   Success: {data.get('success')}")
                    print(f"   Message: {data.get('message')}")
                    print(f"   Error: {data.get('error')}")
                    if 'debug' in data:
                        print(f"   Debug: {data.get('debug')}")
                except json.JSONDecodeError:
                    print("❌ No es JSON válido")
                    print(f"📄 Contenido: {response.text[:200]}...")
            elif response.status_code == 302:
                print("❌ Aún devuelve redirect - problema no solucionado")
            else:
                print(f"⚠️ Status inesperado: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_conocimiento_con_auth_falsa():
    """Probar POST con datos falsos para verificar validación"""
    print("\n\n🧪 PROBANDO POST SIN AUTENTICACIÓN")
    print("=" * 60)
    
    url = urljoin(BASE_URL, "/panel_cliente/aura/entrenar/bloques")
    
    data = {
        "contenido": "Test de contenido",
        "etiquetas": ["test"],
        "prioridad": False
    }
    
    session = requests.Session()
    
    try:
        response = session.post(url, headers=HEADERS, json=data)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 401:
            try:
                result = response.json()
                print("✅ POST también protegido correctamente:")
                print(f"   Success: {result.get('success')}")
                print(f"   Message: {result.get('message')}")
                print(f"   Error: {result.get('error')}")
            except json.JSONDecodeError:
                print("❌ No es JSON válido")
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 TEST DE AUTENTICACIÓN AJAX PARA CONOCIMIENTO")
    print("=" * 80)
    print("Este script verifica que los endpoints AJAX devuelvan JSON 401")
    print("en lugar de redirects 302 cuando no hay autenticación.")
    print()
    
    test_conocimiento_sin_auth()
    test_conocimiento_con_auth_falsa()
    
    print("\n\n🎉 PRUEBA COMPLETADA")
    print("=" * 80)
    print("\n💡 INTERPRETACIÓN:")
    print("   ✅ Si devuelve 401 + JSON = Funciona correctamente")
    print("   ❌ Si devuelve 302 + HTML = Aún hay problema")
    print("   ⚠️ Si devuelve 200 = Endpoint no protegido")
    print("\n📋 PRÓXIMOS PASOS:")
    print("   1. Asegúrate de que el servidor esté ejecutándose")
    print("   2. Abre el navegador en http://localhost:5000")
    print("   3. Inicia sesión en el sistema")
    print("   4. Ve a Panel Cliente > Entrenar Nora")
    print("   5. Verifica que el conocimiento se cargue correctamente")
