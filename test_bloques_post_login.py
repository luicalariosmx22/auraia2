#!/usr/bin/env python3
"""
Script para probar el endpoint de bloques de conocimiento después del login
"""

import requests
import json

def test_bloques_post_login():
    base_url = "http://localhost:5000"
    
    print("🔄 Iniciando test de bloques post-login...")
    
    # Crear una sesión para mantener cookies
    session = requests.Session()
    
    # Paso 1: Hacer login
    print("🔐 Haciendo login...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    login_response = session.post(f"{base_url}/login/simple", data=login_data)
    print(f"Login response status: {login_response.status_code}")
    
    if login_response.status_code != 302:  # Debería redirigir
        print("❌ Error en login")
        print(f"Response: {login_response.text[:500]}")
        return
    
    print("✅ Login exitoso")
    
    # Paso 2: Verificar que podemos acceder al panel de entrenamiento
    print("🔄 Verificando acceso al panel de entrenamiento...")
    panel_response = session.get(f"{base_url}/panel_cliente/aura/entrenar")
    print(f"Panel response status: {panel_response.status_code}")
    
    if panel_response.status_code != 200:
        print("❌ No se puede acceder al panel de entrenamiento")
        print(f"Response: {panel_response.text[:500]}")
        return
    
    print("✅ Acceso al panel exitoso")
    
    # Paso 3: Probar el endpoint de bloques
    print("🔄 Probando endpoint de bloques...")
    bloques_response = session.get(f"{base_url}/panel_cliente/aura/entrenar/bloques")
    print(f"Bloques response status: {bloques_response.status_code}")
    print(f"Bloques response headers: {dict(bloques_response.headers)}")
    
    if bloques_response.status_code == 200:
        try:
            bloques_data = bloques_response.json()
            print("✅ Endpoint de bloques funcionando")
            print(f"📊 Respuesta: {json.dumps(bloques_data, indent=2)}")
        except json.JSONDecodeError as e:
            print("❌ Error al decodificar JSON de bloques")
            print(f"Response text: {bloques_response.text[:500]}")
    else:
        print("❌ Error en endpoint de bloques")
        print(f"Response: {bloques_response.text[:500]}")
    
    # Paso 4: Probar otros endpoints para comparar
    print("🔄 Probando endpoint de instrucciones para comparar...")
    instrucciones_response = session.get(f"{base_url}/panel_cliente/aura/entrenar")
    print(f"Instrucciones response status: {instrucciones_response.status_code}")
    
    # Paso 5: Verificar cookies de sesión
    print("🍪 Cookies de sesión:")
    for cookie in session.cookies:
        print(f"  {cookie.name}: {cookie.value}")

if __name__ == "__main__":
    test_bloques_post_login()
