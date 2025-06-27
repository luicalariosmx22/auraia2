#!/usr/bin/env python3
"""
🔧 Test con Sesión para Bloques de Conocimiento
Este script simula una sesión autenticada para probar los endpoints
"""

import requests
import json

def test_with_session():
    """Test con sesión persistente"""
    print("🔐 TESTING CON SESIÓN AUTENTICADA")
    print("=" * 50)
    
    # Crear sesión persistente
    session = requests.Session()
    base_url = "http://localhost:5000"
    nombre_nora = "aura"
    
    # 1. Intentar acceder a la página principal
    print("\n1️⃣ Accediendo a página de entrenamiento...")
    try:
        url_main = f"{base_url}/panel_cliente/{nombre_nora}/entrenar"
        response = session.get(url_main)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print(f"   ↳ Redirect a: {response.headers.get('Location', 'N/A')}")
            print("   ⚠️ Requiere autenticación")
        elif response.status_code == 200:
            print("   ✅ Página accesible")
        else:
            print(f"   ❌ Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Test directo del endpoint de bloques (puede funcionar sin sesión)
    print("\n2️⃣ Test directo endpoint bloques...")
    try:
        url_bloques = f"{base_url}/panel_cliente/{nombre_nora}/entrenar/bloques"
        response = session.get(url_bloques)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Bloques encontrados: {len(data.get('data', []))}")
            if data.get('data'):
                print(f"   📋 Primer bloque: {data['data'][0]['contenido'][:50]}...")
        else:
            print(f"   ❌ Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Test POST (agregar bloque)
    print("\n3️⃣ Test POST (agregar bloque)...")
    test_data = {
        "contenido": "🧪 Test con sesión desde Python",
        "etiquetas": ["test", "sesion", "python"],
        "prioridad": False
    }
    
    try:
        url_post = f"{base_url}/panel_cliente/{nombre_nora}/entrenar/bloques"
        headers = {"Content-Type": "application/json"}
        response = session.post(url_post, json=test_data, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Bloque creado exitosamente")
            print(f"   📋 Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   ❌ Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def check_javascript_console():
    """Verificar si hay errores en JavaScript"""
    print("\n🔍 VERIFICACIÓN DE JAVASCRIPT")
    print("=" * 50)
    print("Para depurar el frontend:")
    print("1. Abre Chrome DevTools (F12)")
    print("2. Ve a la pestaña 'Console'")
    print("3. Navega a: http://localhost:5000/panel_cliente/aura/entrenar")
    print("4. Ve a la sección 'Base de Conocimiento'")
    print("5. Busca errores en la consola como:")
    print("   - 'CORS error'")
    print("   - '401 Unauthorized'")
    print("   - '404 Not Found'")
    print("   - 'Fetch error'")
    print("")
    print("🔧 Si ves errores 401/403 → Problema de autenticación")
    print("🔧 Si ves errores 404 → Problema de rutas")
    print("🔧 Si ves errores CORS → Problema de headers")

def main():
    print("🚀 DIAGNÓSTICO COMPLETO - SESIÓN Y ENDPOINTS")
    print("=" * 60)
    
    test_with_session()
    check_javascript_console()
    
    print("\n📊 CONCLUSIONES:")
    print("- Si los endpoints funcionan por curl/Python pero no en el browser:")
    print("  → Problema de autenticación/sesión en el frontend")
    print("- Si ves errores en la consola de JavaScript:")
    print("  → Problema específico del frontend")
    print("- La base de datos SÍ tiene bloques de conocimiento")

if __name__ == "__main__":
    main()
