#!/usr/bin/env python3
"""
Test rápido del panel WhatsApp Web
"""

import requests
import time

def test_quick():
    """Test rápido del panel"""
    
    print("🔍 TEST RÁPIDO WHATSAPP WEB")
    print("="*40)
    
    base_url = "http://localhost:5000"
    whatsapp_url = f"{base_url}/panel_cliente/aura/whatsapp"
    
    # Esperar hasta que NORA responda
    print("⏳ Esperando que NORA esté listo...")
    
    for i in range(12):  # 60 segundos máximo
        try:
            response = requests.get(base_url, timeout=2)
            if response.status_code == 200:
                print("✅ NORA está listo")
                break
        except:
            pass
        
        print(f"   Intento {i+1}/12...")
        time.sleep(5)
    else:
        print("❌ NORA no responde después de 60 segundos")
        return
    
    # Probar panel WhatsApp
    print("\n📱 Probando panel WhatsApp Web...")
    try:
        response = requests.get(whatsapp_url, timeout=10)
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Panel WhatsApp Web carga correctamente")
            
            content = response.text
            if "WhatsApp Web" in content and "Flujo Automático" in content:
                print("✅ Contenido del panel correcto")
                print("\n🎉 ¡TODO FUNCIONANDO!")
                print(f"🌐 Accede a: {whatsapp_url}")
                print("💡 Haz clic en 'Flujo Automático' para ver el QR")
            else:
                print("⚠️ Contenido del panel incompleto")
                print("📋 Fragmento:", content[:200] + "...")
        elif response.status_code == 404:
            print("❌ Blueprint no registrado (404)")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error probando panel: {e}")

if __name__ == "__main__":
    test_quick()
