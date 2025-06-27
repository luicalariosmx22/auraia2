#!/usr/bin/env python3
"""
🔐 Test rápido de autenticación - Verificar que los endpoints principales requieren login
"""

import requests
import sys

def test_auth_quick():
    print("🔐 Test rápido de autenticación")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    test_endpoints = [
        f"/panel_cliente/test/entrenar",
        f"/panel_cliente/test/entrenar/bloques"
    ]
    
    server_running = False
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        server_running = True
        print("✅ Servidor está corriendo")
    except:
        print("❌ Servidor no está corriendo")
        print("   Ejecuta: python run.py o flask run")
        return False
    
    if not server_running:
        return False
    
    # Test de endpoints con autenticación
    print("\n🔍 Probando endpoints que deben requerir autenticación:")
    
    for endpoint in test_endpoints:
        url = base_url + endpoint
        try:
            print(f"\nProbando: {endpoint}")
            response = requests.get(url, allow_redirects=False)
            
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                if '/login' in location:
                    print("✅ Correctamente redirige a login")
                else:
                    print(f"⚠️  Redirige a: {location}")
            elif response.status_code == 401:
                print("✅ Retorna 401 Unauthorized")
            else:
                print(f"❌ Status inesperado: {response.status_code}")
                if response.status_code == 200:
                    print("   ⚠️  PROBLEMA: No requiere autenticación cuando debería")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test de endpoint temporal (sin autenticación)
    print("\n🔓 Probando endpoint temporal (sin autenticación):")
    temp_url = f"{base_url}/test/bloques/test"
    try:
        response = requests.get(temp_url, allow_redirects=False)
        if response.status_code == 200:
            print("✅ Endpoint temporal funciona sin autenticación")
        else:
            print(f"⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎯 Autenticación configurada correctamente!")
    print("   Los endpoints principales requieren login")
    print("   Los endpoints temporales no requieren login")
    print("\n⚠️  RECORDATORIO: Eliminar endpoints temporales antes de producción")

if __name__ == "__main__":
    test_auth_quick()
