#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TEST AGREGAR BLOQUE - Prueba de funcionalidad de agregado de conocimiento
Verifica que el formulario del panel funcione correctamente
"""

import requests
import json
from datetime import datetime
import uuid

# Configuración
BASE_URL = "http://localhost:5000"
NOMBRE_NORA = "aura"  # Cambiar por el nombre de tu asistente

def test_agregar_bloque():
    """Prueba la funcionalidad de agregar bloque"""
    print("🧪 INICIANDO PRUEBA - Agregar Bloque de Conocimiento")
    print("=" * 60)
    
    # URL del endpoint
    url = f"{BASE_URL}/panel_cliente/{NOMBRE_NORA}/entrenar/bloques"
    print(f"📡 URL: {url}")
    
    # Datos de prueba
    test_data = {
        "contenido": "Esta es una prueba de agregado de conocimiento desde la interfaz web. Incluye información importante para el asistente.",
        "etiquetas": ["prueba", "test", "conocimiento", "interfaz"],
        "prioridad": True
    }
    
    print("📝 Datos de prueba:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    print()
    
    # Headers para simular petición AJAX
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        print("🚀 Enviando petición POST...")
        response = requests.post(url, json=test_data, headers=headers)
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📡 Headers: {dict(response.headers)}")
        
        # Imprimir respuesta
        if response.headers.get('content-type', '').startswith('application/json'):
            resultado = response.json()
            print("📦 Respuesta JSON:")
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
            
            if resultado.get('success'):
                print("✅ ÉXITO: Bloque agregado correctamente")
                if 'data' in resultado:
                    print(f"🆔 ID del nuevo bloque: {resultado['data'][0].get('id', 'N/A')}")
            else:
                print(f"❌ ERROR: {resultado.get('message', 'Error desconocido')}")
        else:
            print("📄 Respuesta texto:")
            print(response.text[:500])
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se pudo conectar al servidor")
        print("💡 Asegúrate de que el servidor esté ejecutándose en http://localhost:5000")
        
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")
        
    print("\n" + "=" * 60)
    print("🧪 PRUEBA COMPLETADA")

def test_obtener_bloques():
    """Prueba obtener bloques para verificar que el nuevo se agregó"""
    print("\n🔍 VERIFICANDO - Obtener Bloques")
    print("-" * 40)
    
    url = f"{BASE_URL}/panel_cliente/{NOMBRE_NORA}/entrenar/bloques"
    headers = {
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            resultado = response.json()
            
            if resultado.get('success') and 'data' in resultado:
                bloques = resultado['data']
                print(f"📊 Total de bloques: {len(bloques)}")
                
                # Buscar bloques de prueba
                bloques_prueba = [b for b in bloques if 'prueba' in b.get('contenido', '').lower()]
                if bloques_prueba:
                    print(f"🧪 Bloques de prueba encontrados: {len(bloques_prueba)}")
                    for bloque in bloques_prueba[-3:]:  # Mostrar últimos 3
                        print(f"  - ID: {bloque.get('id', 'N/A')[:8]}...")
                        print(f"    Contenido: {bloque.get('contenido', '')[:50]}...")
                        print(f"    Etiquetas: {bloque.get('etiquetas', [])}")
                        print(f"    Prioridad: {bloque.get('prioridad', False)}")
                        print()
                else:
                    print("⚠️ No se encontraron bloques de prueba")
            else:
                print(f"❌ Error obteniendo bloques: {resultado.get('message', 'Error desconocido')}")
        else:
            print("❌ Respuesta no es JSON")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_agregar_bloque()
    test_obtener_bloques()
