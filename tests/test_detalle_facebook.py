#!/usr/bin/env python3
"""
🧪 TEST DETALLE: Verificar ruta de detalle específico
"""

import requests
import time

print("🔍 Probando ruta de detalle de página Facebook...")

# URL base
BASE_URL = "http://localhost:5000"

# Ruta específica de detalle
ruta_detalle = "/panel_cliente/aura/redes_sociales/facebook/782681001814242"

url_completa = BASE_URL + ruta_detalle

try:
    print(f"🔍 Probando: {ruta_detalle}")
    
    start_time = time.time()
    response = requests.get(url_completa, timeout=10, allow_redirects=True)
    end_time = time.time()
    
    tiempo_respuesta = round((end_time - start_time) * 1000, 2)
    
    if response.status_code == 200:
        print(f"✅ OK ({response.status_code}) - {tiempo_respuesta}ms")
        print(f"🎯 ¡El detalle de la página funciona correctamente!")
    elif 300 <= response.status_code < 400:
        print(f"🔀 REDIRECT ({response.status_code}) - {tiempo_respuesta}ms")
        print(f"📍 Redirigiendo a: {response.headers.get('Location', 'Unknown')}")
    else:
        print(f"❌ ERROR ({response.status_code}) - {tiempo_respuesta}ms")
        print(f"📝 Respuesta: {response.text[:200]}...")
        
except requests.exceptions.ConnectionError:
    print(f"❌ CONEXIÓN FALLIDA - Servidor no disponible")
except requests.exceptions.Timeout:
    print(f"⏰ TIMEOUT - La página tardó más de 10 segundos")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n🎯 Test de detalle completado!")
