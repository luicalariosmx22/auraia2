#!/usr/bin/env python3
"""
Script para probar específicamente el acceso a audiencias personalizadas de Meta
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_custom_audiences():
    """Probar acceso a audiencias personalizadas"""
    
    print("🧪 PRUEBA ESPECÍFICA DE AUDIENCIAS PERSONALIZADAS")
    print("=" * 60)
    
    access_token = os.getenv('META_ACCESS_TOKEN')
    if not access_token:
        print("❌ No se encontró META_ACCESS_TOKEN")
        return
    
    # Cuentas de prueba (usando la que sabemos que existe)
    cuentas_prueba = ["26907830"]  # De los logs anteriores
    
    for cuenta_id in cuentas_prueba:
        print(f"\n🔍 Probando audiencias personalizadas para cuenta: {cuenta_id}")
        
        # Test 1: Acceso básico a customaudiences
        print("\n1️⃣ Test básico de customaudiences:")
        try:
            url = f"https://graph.facebook.com/v19.0/act_{cuenta_id}/customaudiences"
            params = {
                'access_token': access_token,
                'fields': 'id,name',
                'limit': 10
            }
            
            response = requests.get(url, params=params, timeout=30)
            print(f"📡 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                audiencias = data.get('data', [])
                print(f"✅ Éxito: {len(audiencias)} audiencias personalizadas encontradas")
                for aud in audiencias[:3]:  # Mostrar solo las primeras 3
                    print(f"   - ID: {aud.get('id')} | Nombre: {aud.get('name')}")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"💥 Excepción: {e}")
        
        # Test 2: Con más campos
        print("\n2️⃣ Test con campos extendidos:")
        try:
            url = f"https://graph.facebook.com/v19.0/act_{cuenta_id}/customaudiences"
            params = {
                'access_token': access_token,
                'fields': 'id,name,description,approximate_count,time_created,time_updated',
                'limit': 5
            }
            
            response = requests.get(url, params=params, timeout=30)
            print(f"📡 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                audiencias = data.get('data', [])
                print(f"✅ Éxito con campos extendidos: {len(audiencias)} audiencias")
                for aud in audiencias[:2]:
                    print(f"   - {aud.get('name')} | Tamaño: {aud.get('approximate_count')} | Creada: {aud.get('time_created')}")
            else:
                print(f"❌ Error con campos extendidos: {response.text}")
                
        except Exception as e:
            print(f"💥 Excepción con campos extendidos: {e}")
        
        # Test 3: Saved audiences corregido
        print("\n3️⃣ Test de saved audiences (corregido):")
        try:
            url = f"https://graph.facebook.com/v19.0/act_{cuenta_id}/saved_audiences"
            params = {
                'access_token': access_token,
                'fields': 'id,name,description,time_created',  # Sin approximate_count
                'limit': 5
            }
            
            response = requests.get(url, params=params, timeout=30)
            print(f"📡 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                audiencias = data.get('data', [])
                print(f"✅ Éxito saved audiences: {len(audiencias)} audiencias guardadas")
                for aud in audiencias[:2]:
                    print(f"   - {aud.get('name')} | Creada: {aud.get('time_created')}")
            else:
                print(f"❌ Error saved audiences: {response.text}")
                
        except Exception as e:
            print(f"💥 Excepción saved audiences: {e}")

if __name__ == "__main__":
    test_custom_audiences()
