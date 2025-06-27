#!/usr/bin/env python3
"""
🔧 Test Completo para Endpoints de Conocimiento
Ejecutar después de iniciar el servidor para verificar funcionamiento
"""

import requests
import json

def test_endpoints_conocimiento():
    base_url = "http://localhost:5000"
    nombre_nora = "aura"
    
    print("🧪 TESTING ENDPOINTS DE CONOCIMIENTO")
    print("=" * 60)
    
    # Test 1: GET bloques
    print(f"\n1️⃣ GET /panel_cliente/{nombre_nora}/entrenar/bloques")
    print("-" * 40)
    try:
        url = f"{base_url}/panel_cliente/{nombre_nora}/entrenar/bloques"
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Response JSON: {json.dumps(data, indent=2)}")
            except:
                print(f"✅ Response Text: {response.text}")
        else:
            print(f"❌ Error Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor en localhost:5000")
        print("   Asegúrate de que el servidor esté corriendo")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    # Test 2: POST nuevo bloque
    print(f"\n2️⃣ POST /panel_cliente/{nombre_nora}/entrenar/bloques")
    print("-" * 40)
    
    test_data = {
        "contenido": "🧪 Bloque de prueba automático desde script de test",
        "etiquetas": ["test", "automatico", "debug"],
        "prioridad": True
    }
    
    try:
        url = f"{base_url}/panel_cliente/{nombre_nora}/entrenar/bloques"
        print(f"URL: {url}")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=test_data, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Response JSON: {json.dumps(data, indent=2)}")
            except:
                print(f"✅ Response Text: {response.text}")
        else:
            print(f"❌ Error Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN:")
    print("- Si ves 'Connection Error', el servidor no está corriendo")
    print("- Si ves Status 404, los endpoints no están registrados")
    print("- Si ves Status 500, hay un error en el código del servidor")
    print("- Si ves Status 200, ¡todo funciona correctamente! 🎉")
    print("\n🚀 Para iniciar servidor: export $(grep -v '^#' .env.local | xargs) && python dev_start.py")

if __name__ == "__main__":
    test_endpoints_conocimiento()
