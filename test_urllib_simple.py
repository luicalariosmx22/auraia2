#!/usr/bin/env python3
"""
Script simple para probar el endpoint de bloques directamente
"""

import urllib.request
import urllib.parse
import http.cookiejar
import json

def test_con_urllib():
    """Test usando urllib para evitar problemas con requests"""
    
    print("🔄 Testando con urllib...")
    
    # Crear un cookie jar para mantener sesión
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    urllib.request.install_opener(opener)
    
    base_url = "http://localhost:5000"
    
    try:
        # Step 1: Obtener formulario de login
        print("📋 Step 1: Obteniendo formulario de login...")
        login_page = urllib.request.urlopen(f"{base_url}/login/simple")
        print(f"Login page status: {login_page.getcode()}")
        
        # Step 2: Hacer login
        print("🔐 Step 2: Haciendo login...")
        login_data = urllib.parse.urlencode({
            'email': 'admin@test.com',
            'password': '123456'
        }).encode()
        
        login_req = urllib.request.Request(
            f"{base_url}/login/simple/auth",
            data=login_data,
            method='POST'
        )
        
        try:
            login_response = urllib.request.urlopen(login_req)
            print(f"Login status: {login_response.getcode()}")
        except urllib.error.HTTPError as e:
            if e.code == 302:
                print("✅ Login exitoso (redirect)")
            else:
                print(f"❌ Error en login: {e.code}")
                return
        
        # Step 3: Probar endpoint de bloques
        print("📦 Step 3: Probando endpoint de bloques...")
        try:
            bloques_response = urllib.request.urlopen(f"{base_url}/panel_cliente/aura/entrenar/bloques")
            data = bloques_response.read().decode()
            
            print(f"Bloques status: {bloques_response.getcode()}")
            print(f"Content-Type: {bloques_response.getheader('Content-Type')}")
            
            if 'application/json' in bloques_response.getheader('Content-Type', ''):
                bloques_data = json.loads(data)
                print(f"✅ JSON válido")
                print(f"Success: {bloques_data.get('success')}")
                print(f"Bloques: {len(bloques_data.get('data', []))}")
            else:
                print(f"❌ No es JSON: {data[:200]}")
                
        except urllib.error.HTTPError as e:
            if e.code == 302:
                print("❌ Redirigido en bloques - problema de sesión")
                print(f"Location: {e.headers.get('Location', 'N/A')}")
            else:
                print(f"❌ Error en bloques: {e.code}")
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_con_urllib()
