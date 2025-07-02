#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para el endpoint de actualización de últimos 7 días de Google Ads
"""

import requests
import json
from datetime import datetime

# URL del endpoint
url = "http://localhost:5000/api/google-ads/actualizar-ultimos-7-dias"

# Datos de la petición
data = {
    "incluir_mcc": False,
    "incluir_anuncios": True
}

print("=" * 80)
print("🧪 PRUEBA DE ENDPOINT: ACTUALIZAR ÚLTIMOS 7 DÍAS")
print("=" * 80)
print(f"📤 Enviando petición a {url}...")
print(f"   con datos: {json.dumps(data, indent=2)}")

try:
    # Realizar la petición
    response = requests.post(url, json=data)
    
    # Verificar respuesta
    print(f"📥 Respuesta recibida (código {response.status_code})")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Petición exitosa!")
        print("\n📊 RESULTADO:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Error en la petición: {response.status_code}")
        try:
            error = response.json()
            print(json.dumps(error, indent=2, ensure_ascii=False))
        except:
            print(response.text)
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("=" * 80)
