#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Script de prueba para verificar endpoints de base de conocimiento
"""

import requests
import json
import time

# Configuración
BASE_URL = "http://localhost:5000"
NOMBRE_NORA = "aura"

def test_endpoint(method, url, data=None, descripcion=""):
    """Probar un endpoint específico"""
    print(f"\n🔍 {descripcion}")
    print(f"   {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"   ❌ Método {method} no soportado")
            return False
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"   ✅ Respuesta JSON válida")
                if json_data.get('success'):
                    if 'data' in json_data:
                        print(f"   📊 Datos: {len(json_data['data'])} elementos")
                    if 'message' in json_data:
                        print(f"   💬 Mensaje: {json_data['message']}")
                else:
                    print(f"   ⚠️ Success=False: {json_data.get('message', 'Sin mensaje')}")
                return json_data
            except:
                print(f"   ⚠️ Respuesta no JSON: {response.text[:100]}...")
                return False
        else:
            print(f"   ❌ Error HTTP {response.status_code}: {response.text[:100]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ No se pudo conectar al servidor")
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    print("🧪 PRUEBA DE ENDPOINTS DE BASE DE CONOCIMIENTO")
    print("=" * 50)
    
    # 1. Verificar conexión general
    resultado = test_endpoint(
        "GET", 
        f"{BASE_URL}/admin/nora/{NOMBRE_NORA}/test-db",
        descripcion="Verificar conexión a base de datos"
    )
    
    if not resultado:
        print("\n❌ No se pudo conectar al servidor. ¿Está ejecutándose?")
        print("   Ejecuta: python dev_start.py")
        return
    
    # 2. Listar bloques existentes
    bloques = test_endpoint(
        "GET",
        f"{BASE_URL}/admin/nora/{NOMBRE_NORA}/entrenar/bloques",
        descripcion="Listar bloques de conocimiento existentes"
    )
    
    # 3. Si no hay bloques, crear algunos de prueba
    if bloques and bloques.get('success') and len(bloques.get('data', [])) == 0:
        print("\n📝 No hay bloques, creando datos de prueba...")
        test_endpoint(
            "POST",
            f"{BASE_URL}/admin/nora/{NOMBRE_NORA}/test-create",
            descripcion="Crear datos de prueba"
        )
        
        # Volver a listar después de crear
        bloques = test_endpoint(
            "GET",
            f"{BASE_URL}/admin/nora/{NOMBRE_NORA}/entrenar/bloques",
            descripcion="Listar bloques después de crear datos de prueba"
        )
    
    # 4. Probar crear un nuevo bloque
    nuevo_bloque = {
        "contenido": "🧪 Este es un bloque de prueba creado por script",
        "etiquetas": ["test", "script", "prueba"],
        "prioridad": True
    }
    
    test_endpoint(
        "POST",
        f"{BASE_URL}/admin/nora/{NOMBRE_NORA}/entrenar/bloques",
        data=nuevo_bloque,
        descripcion="Crear nuevo bloque de conocimiento"
    )
    
    # 5. Listar de nuevo para verificar
    test_endpoint(
        "GET",
        f"{BASE_URL}/admin/nora/{NOMBRE_NORA}/entrenar/bloques",
        descripcion="Verificar que el nuevo bloque fue creado"
    )
    
    print("\n" + "=" * 50)
    print("✅ PRUEBA COMPLETADA")
    print(f"🌐 Panel de entrenamiento: {BASE_URL}/admin/nora/{NOMBRE_NORA}/entrenar")
    print(f"🧪 Página de prueba: {BASE_URL}/test_conocimiento_simple.html")

if __name__ == "__main__":
    main()
