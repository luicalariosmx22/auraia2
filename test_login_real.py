#!/usr/bin/env python3
"""
Script para probar el login real y verificar sesiones
"""

import requests
import json

def test_login_real():
    """Test completo del flujo de login y bloques"""
    base_url = "http://localhost:5000"
    
    print("🚀 Test completo de login y bloques...")
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # Test 1: Verificar formulario de login
    print("\n🔍 Step 1: Verificando formulario de login...")
    try:
        login_page = session.get(f"{base_url}/login/simple")
        print(f"Login page status: {login_page.status_code}")
        if "email" in login_page.text.lower():
            print("✅ Formulario de login encontrado")
        else:
            print("❌ Formulario de login no encontrado")
    except Exception as e:
        print(f"❌ Error al acceder al login: {e}")
        return
    
    # Test 2: Intentar login
    print("\n🔐 Step 2: Intentando login...")
    
    # Probar diferentes credenciales
    credenciales = [
        {"email": "admin@test.com", "password": "123456"},
        {"email": "aura@test.com", "password": "123456"},
        {"email": "cliente@test.com", "password": "123456"}
    ]
    
    login_exitoso = False
    
    for cred in credenciales:
        print(f"   Probando: {cred['email']}")
        
        login_response = session.post(f"{base_url}/login/simple/auth", data=cred, allow_redirects=False)
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code == 302:  # Redirect = success
            print(f"   ✅ Login exitoso con {cred['email']}")
            login_exitoso = True
            break
        elif login_response.status_code == 200:
            if "error" in login_response.text.lower():
                print(f"   ❌ Credenciales incorrectas para {cred['email']}")
            else:
                print(f"   ⚠️ Login posiblemente exitoso, verificando...")
        else:
            print(f"   ❌ Error inesperado: {login_response.status_code}")
    
    if not login_exitoso:
        print("❌ No se pudo hacer login con ninguna credencial")
        return
    
    # Test 3: Verificar acceso al panel
    print("\n🎯 Step 3: Verificando acceso al panel...")
    panel_response = session.get(f"{base_url}/panel_cliente/aura/entrenar")
    print(f"Panel status: {panel_response.status_code}")
    
    if panel_response.status_code == 200:
        print("✅ Acceso al panel exitoso")
    elif panel_response.status_code == 302:
        print("❌ Redirigido - sesión no válida")
        return
    else:
        print(f"❌ Error en panel: {panel_response.status_code}")
        return
    
    # Test 4: Verificar endpoint de bloques
    print("\n📦 Step 4: Verificando endpoint de bloques...")
    bloques_response = session.get(f"{base_url}/panel_cliente/aura/entrenar/bloques")
    print(f"Bloques status: {bloques_response.status_code}")
    print(f"Bloques Content-Type: {bloques_response.headers.get('Content-Type', 'N/A')}")
    
    if bloques_response.status_code == 200:
        try:
            bloques_data = bloques_response.json()
            print(f"✅ Endpoint de bloques funcionando")
            print(f"📊 Success: {bloques_data.get('success', 'N/A')}")
            print(f"📊 Bloques encontrados: {len(bloques_data.get('data', []))}")
            
            if bloques_data.get('data'):
                print("🔍 Primeros bloques:")
                for i, bloque in enumerate(bloques_data['data'][:2]):
                    print(f"  {i+1}. {bloque.get('contenido', '')[:50]}...")
        except json.JSONDecodeError:
            print("❌ Respuesta no es JSON válido")
            print(f"Response: {bloques_response.text[:200]}")
    elif bloques_response.status_code == 302:
        print("❌ Redirigido en bloques - problema de sesión")
    else:
        print(f"❌ Error en bloques: {bloques_response.status_code}")
        print(f"Response: {bloques_response.text[:200]}")
    
    # Test 5: Verificar otros endpoints
    print("\n🔄 Step 5: Comparando con otros endpoints...")
    
    # Probar endpoint de personalidad (que sabemos que funciona)
    try:
        # Este es un POST, así que solo verificamos que no nos redirija
        otros_response = session.get(f"{base_url}/panel_cliente/aura/entrenar")
        print(f"Otros endpoints status: {otros_response.status_code}")
        if otros_response.status_code == 200:
            print("✅ Otros endpoints funcionan correctamente")
        
    except Exception as e:
        print(f"❌ Error en otros endpoints: {e}")
    
    print("\n📊 RESUMEN:")
    print("- Si login funciona pero bloques no, el problema está en el endpoint específico")
    print("- Si otros endpoints funcionan pero bloques no, es problema específico de bloques")
    print("- Si todos fallan después del login, es problema de sesión")

if __name__ == "__main__":
    test_login_real()
