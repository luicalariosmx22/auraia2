#!/usr/bin/env python3
"""
🔍 Test completo del sistema de login implementado
"""

import requests
import time

def test_login_system():
    print("🔍 TESTING SISTEMA DE LOGIN COMPLETO")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Verificar que el servidor está corriendo
    print("\n1. 🖥️ Verificando servidor...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 302]:
            print("   ✅ Servidor está corriendo")
        else:
            print("   ❌ Servidor tiene problemas")
            return False
    except Exception as e:
        print(f"   ❌ Servidor no responde: {e}")
        print("   💡 Ejecuta: python run.py")
        return False
    
    # Test 2: Verificar redirect principal
    print("\n2. 🔄 Verificando redirect principal (/ -> /login/simple)...")
    try:
        response = requests.get(f"{base_url}/", allow_redirects=False, timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"   Redirect to: {location}")
            if '/login/simple' in location:
                print("   ✅ Redirect principal funciona")
            else:
                print("   ⚠️ Redirect incorrecto")
        else:
            print("   ⚠️ No hay redirect")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Verificar página de login simple
    print("\n3. 🔑 Verificando página de login simple...")
    try:
        response = requests.get(f"{base_url}/login/simple", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            if "Login Simple" in response.text and "admin@test.com" in response.text:
                print("   ✅ Página de login simple funciona")
            else:
                print("   ⚠️ Página no tiene el contenido esperado")
        else:
            print("   ❌ Página de login no carga")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Verificar endpoints protegidos (sin autenticación)
    print("\n4. 🔒 Verificando endpoints protegidos...")
    endpoints_protegidos = [
        "/panel_cliente/aura/entrenar",
        "/panel_cliente/aura/entrenar/bloques"
    ]
    
    for endpoint in endpoints_protegidos:
        try:
            response = requests.get(f"{base_url}{endpoint}", allow_redirects=False, timeout=5)
            print(f"   {endpoint}: Status {response.status_code}")
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                if '/login/simple' in location:
                    print("     ✅ Requiere autenticación correctamente")
                else:
                    print(f"     ⚠️ Redirect incorrecto: {location}")
            else:
                print("     ❌ No requiere autenticación")
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    # Test 5: Verificar endpoints temporales (sin autenticación)
    print("\n5. 🧪 Verificando endpoints temporales...")
    endpoints_temporales = [
        "/test/bloques/aura",
        "/dev/entrenar/aura"
    ]
    
    for endpoint in endpoints_temporales:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"   {endpoint}: Status {response.status_code}")
            if response.status_code == 200:
                print("     ✅ Funciona sin autenticación")
            else:
                print("     ❌ No funciona")
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    # Test 6: Estado de sesión
    print("\n6. 📊 Verificando estado de sesión...")
    try:
        response = requests.get(f"{base_url}/login/status", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Logged in: {data.get('logged_in', False)}")
            print("   ✅ Endpoint de estado funciona")
        else:
            print("   ❌ Endpoint de estado no funciona")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 URLS IMPORTANTES:")
    print(f"   🔑 Login: {base_url}/login/simple")
    print(f"   🏠 Inicio: {base_url}/")
    print(f"   🧪 Test bloques: {base_url}/test/bloques/aura")
    print(f"   🔧 Desarrollo: {base_url}/dev/entrenar/aura")
    print(f"   📊 Estado sesión: {base_url}/login/status")
    
    print("\n👥 USUARIOS DE PRUEBA:")
    print("   🔧 Admin: admin@test.com / 123456")
    print("   👤 Cliente: cliente@test.com / 123456")
    print("   🤖 Cliente Aura: aura@test.com / 123456")
    
    print(f"\n🎉 Sistema de login implementado!")
    print("   1. Ve a http://localhost:5000/login/simple")
    print("   2. Usa aura@test.com / 123456")
    print("   3. Te redirigirá a /panel_cliente/aura/entrenar")
    print("   4. Ahí podrás ver los 3 bloques existentes")

if __name__ == "__main__":
    test_login_system()
