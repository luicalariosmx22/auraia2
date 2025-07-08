#!/usr/bin/env python3
"""
Diagnóstico simple para WhatsApp Web QR
"""

import os
import sys
import json
import requests
import time
from datetime import datetime

def main():
    print("🩺 DIAGNÓSTICO WHATSAPP WEB QR")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    backend_url = 'https://whatsapp-server-production-8f61.up.railway.app'
    
    print(f"\n1. Probando backend: {backend_url}")
    try:
        response = requests.get(f'{backend_url}/health', timeout=10)
        print(f"   ✅ Health: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    print("\n2. Probando endpoint QR...")
    try:
        response = requests.get(f'{backend_url}/qr', timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                qr_data = data.get('qr_data')
                if qr_data:
                    print(f"   ✅ QR disponible: {qr_data[:50]}...")
                else:
                    print("   ❌ No hay QR en respuesta")
                    print(f"   Respuesta: {data}")
            except json.JSONDecodeError:
                print(f"   ❌ Respuesta no es JSON: {response.text[:200]}...")
        else:
            print(f"   ❌ Error: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n3. Probando iniciar sesión...")
    try:
        response = requests.post(f'{backend_url}/init_session', timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Sesión iniciada")
            
            # Esperar y reintentar QR
            print("\n4. Esperando QR después de iniciar sesión...")
            time.sleep(3)
            
            response = requests.get(f'{backend_url}/qr', timeout=10)
            print(f"   Status QR: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    qr_data = data.get('qr_data')
                    if qr_data:
                        print(f"   ✅ QR obtenido: {qr_data[:50]}...")
                    else:
                        print("   ❌ Aún no hay QR")
                        print(f"   Respuesta: {data}")
                except json.JSONDecodeError:
                    print(f"   ❌ Respuesta no es JSON: {response.text[:200]}...")
            else:
                print(f"   ❌ Error obteniendo QR: {response.text[:200]}...")
        else:
            print(f"   ❌ Error iniciando sesión: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n5. Probando cliente WebSocket...")
    try:
        sys.path.append('/mnt/c/Users/PC/PYTHON/Auraai2')
        from clientes.aura.utils.whatsapp_websocket_client import WhatsAppWebSocketClient
        
        client = WhatsAppWebSocketClient()
        print("   ✅ Cliente creado")
        
        if client.connect():
            print("   ✅ Conexión HTTP exitosa")
            
            qr_data = client.get_qr_code()
            if qr_data:
                print(f"   ✅ QR desde cliente: {qr_data[:50]}...")
            else:
                print("   ❌ No hay QR desde cliente")
                
                # Intentar iniciar sesión
                if client.init_session():
                    print("   ✅ Sesión iniciada desde cliente")
                    time.sleep(3)
                    qr_data = client.get_qr_code()
                    if qr_data:
                        print(f"   ✅ QR obtenido después de iniciar: {qr_data[:50]}...")
                    else:
                        print("   ❌ Aún no hay QR desde cliente")
                else:
                    print("   ❌ No se pudo iniciar sesión desde cliente")
        else:
            print("   ❌ No se pudo conectar desde cliente")
            
    except Exception as e:
        print(f"   ❌ Error con cliente: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
