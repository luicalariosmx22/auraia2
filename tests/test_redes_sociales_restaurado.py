#!/usr/bin/env python3
"""
🧪 TEST: Verificar que el módulo de redes sociales funciona como antes
"""

import requests
import time

print("🔄 Verificando que redes sociales funciona como antes de las modificaciones...")

# URL base
BASE_URL = "http://localhost:5000"

# Rutas básicas a probar
rutas_basicas = [
    "/panel_cliente/aura/redes_sociales/",
    "/panel_cliente/aura/redes_sociales/facebook",
]

print(f"📊 Probando {len(rutas_basicas)} rutas básicas...")

for ruta in rutas_basicas:
    url_completa = BASE_URL + ruta
    try:
        print(f"🔍 Probando: {ruta}")
        
        start_time = time.time()
        response = requests.get(url_completa, timeout=10, allow_redirects=True)
        end_time = time.time()
        
        tiempo_respuesta = round((end_time - start_time) * 1000, 2)
        
        if response.status_code == 200:
            print(f"✅ OK ({response.status_code}) - {tiempo_respuesta}ms")
        elif 300 <= response.status_code < 400:
            print(f"🔀 REDIRECT ({response.status_code}) - {tiempo_respuesta}ms → {response.headers.get('Location', 'Unknown')}")
        else:
            print(f"❌ ERROR ({response.status_code}) - {tiempo_respuesta}ms")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONEXIÓN FALLIDA - Esperando a que el servidor termine de cargar...")
        break
    except requests.exceptions.Timeout:
        print(f"⏰ TIMEOUT - La ruta tardó más de 10 segundos")
    except Exception as e:
        print(f"❌ ERROR: {e}")

print("\n🎯 Verificación básica completada!")
