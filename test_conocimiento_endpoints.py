#!/usr/bin/env python3
# Script para probar los endpoints de conocimiento

import requests
import json

# URL base (cambia esto según tu configuración)
BASE_URL = "http://localhost:5000"
NOMBRE_NORA = "aura"  # Cambia esto por el nombre de tu Nora

def test_get_conocimiento():
    """Prueba el endpoint GET para obtener bloques de conocimiento"""
    url = f"{BASE_URL}/panel_cliente/{NOMBRE_NORA}/entrenamiento/bloques"
    print(f"🔍 Probando GET: {url}")
    
    try:
        response = requests.get(url)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Respuesta JSON: {json.dumps(data, indent=2)}")
            except:
                print(f"⚠️ Respuesta no es JSON: {response.text[:200]}...")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_post_conocimiento():
    """Prueba el endpoint POST para agregar un bloque de conocimiento"""
    url = f"{BASE_URL}/panel_cliente/{NOMBRE_NORA}/entrenamiento/bloques"
    print(f"🔍 Probando POST: {url}")
    
    data = {
        "contenido": "Este es un bloque de prueba creado desde el script de testing.",
        "etiquetas": ["test", "script", "prueba"],
        "prioridad": True
    }
    
    try:
        response = requests.post(
            url, 
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ Respuesta JSON: {json.dumps(result, indent=2)}")
            except:
                print(f"⚠️ Respuesta no es JSON: {response.text[:200]}...")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    print("🧪 Iniciando pruebas de endpoints de conocimiento...")
    print("=" * 60)
    
    test_get_conocimiento()
    print("\n" + "=" * 60)
    
    test_post_conocimiento()
    print("\n" + "=" * 60)
    
    print("🏁 Pruebas completadas.")
