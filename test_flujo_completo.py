#!/usr/bin/env python3
"""
Test del flujo completo como lo hace el frontend
"""

import requests
import time
import json

def test_frontend_flow():
    """Simular el flujo completo del frontend"""
    print("🧪 SIMULANDO FLUJO FRONTEND COMPLETO")
    print("="*50)
    
    base_url = "http://localhost:5000"
    
    # Paso 1: Conectar
    print("\n🔌 Paso 1: Conectar al backend...")
    try:
        response = requests.post(
            f"{base_url}/panel_cliente/aura/whatsapp/connect",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        print(f"📊 Connect Status: {response.status_code}")
        data = response.json()
        print(f"📄 Connect Response: {json.dumps(data, indent=2)}")
        
        if not data.get('success'):
            print("❌ Error conectando, abortando")
            return
            
    except Exception as e:
        print(f"❌ Error en connect: {e}")
        return
    
    # Paso 2: Iniciar sesión (get_qr_auto)
    print("\n🚀 Paso 2: Iniciar sesión y obtener QR...")
    try:
        response = requests.post(
            f"{base_url}/panel_cliente/aura/whatsapp/get_qr_auto",
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        print(f"📊 Get QR Status: {response.status_code}")
        data = response.json()
        print(f"📄 Get QR Response: {json.dumps(data, indent=2)}")
        
        if data.get('has_qr') and data.get('qr_data'):
            qr_data = data['qr_data']
            print(f"✅ QR encontrado! (longitud: {len(qr_data)} chars)")
            if qr_data.startswith('data:image/'):
                print("📱 Tipo: Imagen base64")
            else:
                print("📱 Tipo: Texto")
                print(f"📱 Inicio: {qr_data[:50]}...")
        else:
            print("⚠️ No hay QR aún, esperando...")
            
    except Exception as e:
        print(f"❌ Error en get_qr_auto: {e}")
        return
    
    # Paso 3: Reintentar obtener QR cada pocos segundos
    for i in range(5):
        print(f"\n🔄 Paso 3.{i+1}: Reintentando obtener QR (intento {i+1}/5)...")
        time.sleep(3)
        
        try:
            response = requests.get(
                f"{base_url}/panel_cliente/aura/whatsapp/qr",
                timeout=10
            )
            print(f"📊 QR Status: {response.status_code}")
            data = response.json()
            
            if data.get('success') and data.get('qr_data'):
                qr_data = data['qr_data']
                print(f"✅ QR encontrado en intento {i+1}! (longitud: {len(qr_data)} chars)")
                if qr_data.startswith('data:image/'):
                    print("📱 Tipo: Imagen base64")
                else:
                    print("📱 Tipo: Texto")
                    print(f"📱 Inicio: {qr_data[:50]}...")
                break
            else:
                print(f"⚠️ Intento {i+1}: {data.get('message', 'Sin QR')}")
                
        except Exception as e:
            print(f"❌ Error en intento {i+1}: {e}")
    
    # Paso 4: Verificar estado final
    print(f"\n📊 Paso 4: Estado final...")
    try:
        response = requests.get(
            f"{base_url}/panel_cliente/aura/whatsapp/status",
            timeout=10
        )
        data = response.json()
        print(f"📄 Estado final: {json.dumps(data, indent=2)}")
        
    except Exception as e:
        print(f"❌ Error en status: {e}")

if __name__ == "__main__":
    test_frontend_flow()
