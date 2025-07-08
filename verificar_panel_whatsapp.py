#!/usr/bin/env python3
"""
Verificación completa del panel WhatsApp Web
"""

import requests
import json
from datetime import datetime

def main():
    print("🔍 VERIFICACIÓN COMPLETA PANEL WHATSAPP WEB")
    print("="*50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    base_url = "http://localhost:5000"
    whatsapp_url = f"{base_url}/panel_cliente/aura/whatsapp/"
    
    # 1. Verificar NORA base
    print("1️⃣ VERIFICANDO NORA BASE")
    try:
        response = requests.get(base_url, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ NORA responde correctamente")
        else:
            print(f"   ❌ NORA error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error conectando a NORA: {e}")
        return
    
    # 2. Verificar panel WhatsApp
    print("\n2️⃣ VERIFICANDO PANEL WHATSAPP")
    try:
        response = requests.get(whatsapp_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Verificar contenido del panel
            if "WhatsApp" in content:
                print("   ✅ Panel contiene contenido WhatsApp")
            else:
                print("   ❌ Panel NO contiene contenido WhatsApp")
                
            if "QR" in content or "qr" in content:
                print("   ✅ Panel menciona QR")
            else:
                print("   ❌ Panel NO menciona QR")
                
            if "Flujo Automático" in content:
                print("   ✅ Panel tiene botón Flujo Automático")
            else:
                print("   ❌ Panel NO tiene botón Flujo Automático")
                
            if "qrcode" in content:
                print("   ✅ Panel incluye biblioteca QRCode.js")
            else:
                print("   ❌ Panel NO incluye biblioteca QRCode.js")
                
        elif response.status_code == 404:
            print("   ❌ Panel WhatsApp NO ENCONTRADO (404)")
            print("   💡 El blueprint no se registró correctamente")
        else:
            print(f"   ❌ Panel WhatsApp error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error accediendo al panel: {e}")
    
    # 3. Verificar endpoints específicos
    print("\n3️⃣ VERIFICANDO ENDPOINTS WHATSAPP")
    endpoints = [
        "/panel_cliente/aura/whatsapp/connect",
        "/panel_cliente/aura/whatsapp/status", 
        "/panel_cliente/aura/whatsapp/get_qr_auto"
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 405:  # Method not allowed = endpoint existe
                print(f"   ✅ {endpoint} - Disponible (405)")
            elif response.status_code == 200:
                print(f"   ✅ {endpoint} - Disponible (200)")
            elif response.status_code == 404:
                print(f"   ❌ {endpoint} - NO ENCONTRADO (404)")
            else:
                print(f"   ⚠️ {endpoint} - Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} - Error: {e}")
    
    # 4. Verificar backend Railway
    print("\n4️⃣ VERIFICANDO BACKEND RAILWAY")
    railway_url = "https://whatsapp-server-production-8f61.up.railway.app"
    try:
        response = requests.get(f"{railway_url}/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ Backend Railway funcionando")
        else:
            print(f"   ❌ Backend Railway error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Backend Railway no accesible: {e}")
    
    print("\n" + "="*50)
    print("📋 RESUMEN:")
    print("Si el panel WhatsApp responde (200), accede a:")
    print(f"🔗 {whatsapp_url}")
    print("Y haz clic en 'Flujo Automático' para obtener QR")
    print()
    print("Si hay errores 404, el blueprint no se registró.")
    print("Verifica los logs de NORA para más detalles.")

if __name__ == "__main__":
    main()
