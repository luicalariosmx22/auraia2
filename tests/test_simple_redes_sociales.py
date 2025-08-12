#!/usr/bin/env python3
"""
🧪 TEST SIMPLE: Verificar rutas básicas de redes sociales
"""

import requests
import time

print("🌐 Probando rutas básicas de redes sociales...")

# URL base
BASE_URL = "http://localhost:5000"

# Rutas básicas a probar
rutas_basicas = [
    "/panel_cliente/aura/redes_sociales/",
    "/panel_cliente/aura/redes_sociales/facebook",
]

for ruta in rutas_basicas:
    url_completa = BASE_URL + ruta
    try:
        print(f"🔍 Probando: {ruta}")
        
        start_time = time.time()
        response = requests.get(url_completa, timeout=5, allow_redirects=True)
        end_time = time.time()
        
        tiempo_respuesta = round((end_time - start_time) * 1000, 2)
        
        if response.status_code == 200:
            print(f"✅ OK ({response.status_code}) - {tiempo_respuesta}ms")
        elif 300 <= response.status_code < 400:
            print(f"🔀 REDIRECT ({response.status_code}) - {tiempo_respuesta}ms")
        else:
            print(f"❌ ERROR ({response.status_code}) - {tiempo_respuesta}ms")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONEXIÓN FALLIDA - Servidor no disponible")
        break
    except requests.exceptions.Timeout:
        print(f"⏰ TIMEOUT")
    except Exception as e:
        print(f"❌ ERROR: {e}")

print("\n🎯 Test básico completado!")
