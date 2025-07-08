#!/usr/bin/env python3
"""
Diagnóstico específico del endpoint QR
Verifica qué está devolviendo el endpoint /qr
"""

import requests
import json

def test_qr_endpoint():
    """Test del endpoint QR específico"""
    print("🔍 DIAGNÓSTICO ENDPOINT QR")
    print("="*40)
    
    base_url = "http://localhost:5000"
    endpoints = [
        f"{base_url}/panel_cliente/aura/whatsapp/qr",
        f"{base_url}/panel_cliente/aura/whatsapp/get_qr_auto",
        f"{base_url}/panel_cliente/aura/whatsapp/status",
    ]
    
    for endpoint in endpoints:
        print(f"\n🧪 Probando: {endpoint}")
        try:
            if "get_qr_auto" in endpoint:
                # POST request
                response = requests.post(endpoint, 
                                       headers={'Content-Type': 'application/json'},
                                       timeout=10)
            else:
                # GET request
                response = requests.get(endpoint, timeout=10)
            
            print(f"📊 Status: {response.status_code}")
            print(f"🔗 Headers: {dict(response.headers)}")
            
            try:
                data = response.json()
                print(f"📄 JSON Response:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Analizar respuesta específicamente para QR
                if 'qr_data' in data:
                    qr_data = data['qr_data']
                    if qr_data:
                        print(f"✅ QR encontrado (longitud: {len(qr_data)} chars)")
                        if qr_data.startswith('data:image/'):
                            print(f"📱 QR tipo: Imagen base64")
                        else:
                            print(f"📱 QR tipo: Texto")
                            print(f"📱 Inicio QR: {qr_data[:50]}...")
                    else:
                        print(f"⚠️ QR_data está vacío")
                
            except json.JSONDecodeError:
                print(f"📄 Text Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_backend_direct():
    """Test directo del backend Railway"""
    print(f"\n🚀 PROBANDO BACKEND RAILWAY DIRECTO")
    print("="*40)
    
    backend_url = "https://whatsapp-server-production-7e82.up.railway.app"
    
    try:
        response = requests.get(f"{backend_url}/health", timeout=10)
        print(f"📊 Health status: {response.status_code}")
        print(f"📄 Content: {response.text[:200]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_qr_endpoint()
    test_backend_direct()
