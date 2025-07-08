#!/usr/bin/env python3
"""
Verificar si el blueprint de WhatsApp Web está funcionando
"""

import requests
import time

def test_nora_whatsapp():
    """Probar el endpoint de WhatsApp Web en NORA"""
    
    print("🔍 VERIFICANDO BLUEPRINT WHATSAPP WEB EN NORA")
    print("="*50)
    
    base_url = "http://localhost:5000"
    
    # 1. Verificar que NORA esté corriendo
    print("\n1️⃣ VERIFICANDO NORA")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ NORA está corriendo")
        else:
            print(f"❌ NORA responde con {response.status_code}")
            return
    except Exception as e:
        print(f"❌ NORA no responde: {e}")
        return
    
    # 2. Verificar el panel de WhatsApp Web
    print("\n2️⃣ VERIFICANDO PANEL WHATSAPP WEB")
    whatsapp_url = f"{base_url}/panel_cliente/aura/whatsapp"
    
    try:
        response = requests.get(whatsapp_url, timeout=10)
        print(f"📡 Respuesta: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Panel WhatsApp Web carga correctamente")
            
            # Verificar que el contenido sea el correcto
            content = response.text
            if "WhatsApp Web" in content:
                print("✅ Contenido del panel correcto")
            else:
                print("❌ Contenido del panel incorrecto")
                print("📋 Contenido recibido (primeros 200 chars):")
                print(content[:200] + "...")
        elif response.status_code == 404:
            print("❌ Blueprint no registrado - Error 404")
        else:
            print(f"❌ Error en panel: {response.status_code}")
            print(f"📋 Respuesta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error accediendo al panel: {e}")
    
    # 3. Verificar endpoints específicos
    print("\n3️⃣ VERIFICANDO ENDPOINTS ESPECÍFICOS")
    endpoints = [
        "/panel_cliente/aura/whatsapp/status",
        "/panel_cliente/aura/whatsapp/connect",
        "/panel_cliente/aura/whatsapp/qr",
        "/panel_cliente/aura/whatsapp/get_qr_auto"
    ]
    
    for endpoint in endpoints:
        try:
            if "connect" in endpoint or "get_qr_auto" in endpoint:
                # POST endpoints
                response = requests.post(f"{base_url}{endpoint}", timeout=5)
            else:
                # GET endpoints
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                
            print(f"📡 {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ JSON: {str(data)[:100]}...")
                except:
                    print(f"   ⚠️ Respuesta no JSON: {response.text[:50]}...")
            elif response.status_code == 404:
                print("   ❌ Endpoint no encontrado")
            else:
                print(f"   ⚠️ Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # 4. Verificar bibliotecas frontend
    print("\n4️⃣ VERIFICANDO BIBLIOTECAS FRONTEND")
    try:
        response = requests.get("https://cdnjs.cloudflare.com/ajax/libs/qrcode/1.5.3/qrcode.min.js", timeout=10)
        if response.status_code == 200:
            print("✅ QRCode.js disponible")
        else:
            print("❌ QRCode.js no disponible")
    except Exception as e:
        print(f"❌ Error verificando QRCode.js: {e}")

def main():
    print("🧪 TEST NORA WHATSAPP WEB")
    print(f"📅 {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    test_nora_whatsapp()
    
    print("\n" + "="*60)
    print("📋 INSTRUCCIONES:")
    print("1. Si el panel carga pero no hay QR:")
    print("   - Hacer clic en 'Flujo Automático'")
    print("   - Abrir DevTools (F12) y ver la consola")
    print("   - Verificar errores de JavaScript")
    print()
    print("2. Si el panel no carga (404):")
    print("   - Reiniciar NORA")
    print("   - Verificar que el blueprint esté registrado")
    print()
    print("3. Para probar QR manualmente:")
    print("   - Ir a: http://localhost:5000/panel_cliente/aura/whatsapp")
    print("   - Hacer clic en 'Flujo Automático'")
    print("   - Esperar 3-5 segundos")

if __name__ == "__main__":
    main()
