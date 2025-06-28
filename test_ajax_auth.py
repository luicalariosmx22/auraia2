#!/usr/bin/env python3
"""
🧪 Test de autenticación AJAX para endpoints de conocimiento
"""

import requests
import json
import sys
from datetime import datetime

def test_ajax_authentication():
    """Probar que los endpoints AJAX devuelven JSON en lugar de redirects"""
    
    print("🧪 PROBANDO AUTENTICACIÓN AJAX PARA CONOCIMIENTO")
    print("=" * 60)
    
    # URLs a probar
    urls = [
        "http://localhost:5000/panel_cliente/aura/entrenar/bloques",
        "http://127.0.0.1:5000/panel_cliente/aura/entrenar/bloques",
    ]
    
    for url in urls:
        print(f"\n🔗 Probando: {url}")
        print("-" * 40)
        
        try:
            # Hacer request como AJAX sin autenticación
            response = requests.get(url, headers={
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            }, allow_redirects=False)
            
            print(f"📊 Status: {response.status_code}")
            print(f"📊 Headers: {dict(response.headers)}")
            
            # Verificar que ahora devuelve JSON en lugar de redirect
            if response.status_code == 401:
                try:
                    json_data = response.json()
                    print(f"✅ Devuelve JSON de error como esperado:")
                    print(f"   Success: {json_data.get('success')}")
                    print(f"   Message: {json_data.get('message')}")
                    print(f"   Error: {json_data.get('error')}")
                    if 'debug' in json_data:
                        print(f"   Debug: {json_data.get('debug')}")
                except:
                    print(f"❌ Status 401 pero no devuelve JSON válido")
                    print(f"📄 Contenido: {response.text[:200]}...")
            elif response.status_code == 302:
                print(f"❌ Aún devuelve redirect 302")
                print(f"📄 Location: {response.headers.get('Location', 'No location header')}")
            else:
                print(f"⚠️ Status inesperado: {response.status_code}")
                print(f"📄 Contenido: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Error en request: {e}")
    
    print(f"\n🎉 PRUEBA COMPLETADA")
    print("=" * 60)
    print("\n💡 INTERPRETACIÓN:")
    print("   ✅ Si devuelve 401 + JSON = Funciona correctamente")
    print("   ❌ Si devuelve 302 + HTML = Aún hay problema")
    print("   ⚠️ Si devuelve 200 = Endpoint no protegido")

if __name__ == "__main__":
    test_ajax_authentication()
