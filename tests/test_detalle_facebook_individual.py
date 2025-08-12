#!/usr/bin/env python3
"""
🧪 TEST: Ruta de detalle de Facebook
"""

import requests
import time

print("🔍 Probando ruta de detalle de Facebook...")

BASE_URL = "http://localhost:5000"
ruta = "/panel_cliente/aura/redes_sociales/facebook/782681001814242"

try:
    print(f"🔍 Probando: {ruta}")
    
    start_time = time.time()
    response = requests.get(BASE_URL + ruta, timeout=15)
    end_time = time.time()
    
    tiempo_respuesta = round((end_time - start_time) * 1000, 2)
    
    print(f"📊 Status: {response.status_code}")
    print(f"⏱️ Tiempo: {tiempo_respuesta}ms")
    
    if response.status_code == 200:
        print(f"✅ ÉXITO - Página cargada correctamente")
        print(f"📄 Contenido: {len(response.text)} caracteres")
    elif response.status_code == 404:
        print(f"❌ Página no encontrada (404)")
        print(f"📄 Respuesta: {response.text[:300]}...")
    elif response.status_code == 500:
        print(f"❌ ERROR INTERNO (500)")
        print(f"📄 Respuesta: {response.text[:300]}...")
    else:
        print(f"❌ ERROR ({response.status_code})")
        print(f"📄 Respuesta: {response.text[:300]}...")
        
except requests.exceptions.ConnectionError:
    print(f"❌ CONEXIÓN FALLIDA - ¿Servidor activo?")
except requests.exceptions.Timeout:
    print(f"⏰ TIMEOUT - Tardó más de 15 segundos")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n🎯 Test de detalle completado!")
