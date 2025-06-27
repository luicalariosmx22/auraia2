#!/usr/bin/env python3
"""
Script para hacer login automático y probar bloques
"""

import requests
import json
import time

def test_flujo_completo():
    """Test del flujo completo con debug"""
    base_url = "http://localhost:5000"
    
    print("🚀 INICIANDO TEST COMPLETO CON DEBUG\n")
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # Step 1: Test de bloques directo (sin auth)
    print("📦 Step 1: Test directo de bloques (sin auth)...")
    try:
        direct_response = session.get(f"{base_url}/debug/bloques/aura")
        if direct_response.status_code == 200:
            data = direct_response.json()
            print(f"✅ Bloques en BD: {data.get('count', 0)}")
            if data.get('count', 0) > 0:
                print("✅ Los bloques SÍ existen en la base de datos")
            else:
                print("❌ NO hay bloques en la base de datos")
        else:
            print(f"❌ Error en test directo: {direct_response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Step 2: Login
    print("\n🔐 Step 2: Haciendo login...")
    login_data = {
        'email': 'admin@test.com',
        'password': '123456'
    }
    
    login_response = session.post(f"{base_url}/login/simple/auth", data=login_data, allow_redirects=False)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code == 302:
        print("✅ Login exitoso (redirect)")
    else:
        print("❌ Login falló")
        return
    
    # Step 3: Verificar sesión
    print("\n👤 Step 3: Verificando estado de sesión...")
    try:
        session_response = session.get(f"{base_url}/debug/session")
        if session_response.status_code == 200:
            session_data = session_response.json()
            print(f"📧 Email: {session_data.get('email', 'NO')}")
            print(f"🎯 Nombre Nora: {session_data.get('nombre_nora', 'NO')}")
            print(f"👤 User data: {bool(session_data.get('user'))}")
            print(f"🔑 Is Admin: {session_data.get('is_admin', 'NO')}")
            
            if session_data.get('email') and session_data.get('nombre_nora'):
                print("✅ Sesión tiene los datos necesarios")
            else:
                print("❌ Sesión incompleta")
        else:
            print(f"❌ Error verificando sesión: {session_response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Step 4: Test endpoint de bloques con auth
    print("\n📦 Step 4: Test endpoint de bloques CON auth...")
    try:
        bloques_response = session.get(f"{base_url}/panel_cliente/aura/entrenar/bloques")
        print(f"Bloques status: {bloques_response.status_code}")
        print(f"Content-Type: {bloques_response.headers.get('Content-Type', 'N/A')}")
        
        if bloques_response.status_code == 200:
            try:
                bloques_data = bloques_response.json()
                print(f"✅ Endpoint con auth funcionó")
                print(f"📊 Success: {bloques_data.get('success')}")
                print(f"📊 Bloques: {len(bloques_data.get('data', []))}")
            except:
                print("❌ Respuesta no es JSON")
                print(f"Response: {bloques_response.text[:200]}")
        elif bloques_response.status_code == 302:
            print("❌ Redirigido - problema de sesión")
            print(f"Location: {bloques_response.headers.get('Location', 'N/A')}")
        else:
            print(f"❌ Error: {bloques_response.status_code}")
            print(f"Response: {bloques_response.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Step 5: Test acceso al panel general
    print("\n🎯 Step 5: Test acceso al panel general...")
    try:
        panel_response = session.get(f"{base_url}/panel_cliente/aura/entrenar")
        print(f"Panel status: {panel_response.status_code}")
        
        if panel_response.status_code == 200:
            print("✅ Panel general accesible")
        elif panel_response.status_code == 302:
            print("❌ Panel también redirige")
        else:
            print(f"❌ Error en panel: {panel_response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50)
    print("📋 RESUMEN DIAGNÓSTICO:")
    print("1. Si bloques directo funciona pero con auth no → problema de sesión")
    print("2. Si sesión se ve bien pero auth falla → problema en decorador")  
    print("3. Si panel general funciona pero bloques no → problema específico del endpoint")
    print("="*50)

if __name__ == "__main__":
    test_flujo_completo()
