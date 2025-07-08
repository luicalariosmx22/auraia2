#!/usr/bin/env python3
"""
Test rápido del QR corregido
"""

import requests
import json

def test_qr_quick():
    """Test rápido del QR"""
    print("🧪 TEST RÁPIDO DEL QR CORREGIDO")
    print("=" * 50)
    
    try:
        print("📡 Solicitando QR...")
        response = requests.get("http://localhost:5000/panel_cliente/aura/whatsapp/qr", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            qr_data = data.get('qr_data', '')
            
            print(f"✅ Status: {response.status_code}")
            print(f"📱 Success: {data.get('success', False)}")
            print(f"💬 Message: {data.get('message', 'N/A')}")
            print(f"🖼️ Is Real: {data.get('is_real', False)}")
            print(f"📏 QR Length: {len(qr_data)}")
            print(f"🔍 QR Type: {'PNG Image' if qr_data.startswith('data:image/png;base64,') else 'Text' if qr_data.startswith('1@') else 'Unknown'}")
            
            if qr_data.startswith('data:image/png;base64,'):
                print("🎉 ¡QR ES IMAGEN PNG REAL DEL BACKEND!")
                return True
            elif qr_data.startswith('1@'):
                print("📱 QR es texto de WhatsApp Web")
                return True
            else:
                print("❓ QR en formato desconocido")
                return False
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"❌ Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_qr_quick()
    print(f"\n🏁 RESULTADO: {'✅ QR VÁLIDO' if success else '❌ QR INVÁLIDO'}")
