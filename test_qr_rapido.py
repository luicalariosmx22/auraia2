#!/usr/bin/env python3
"""
Prueba rápida: Verificar que el QR se muestra correctamente
"""

import requests
import json
import sys
import os

def test_qr_display():
    """Probar que el QR se obtiene correctamente"""
    print("🔍 PRUEBA RÁPIDA: Verificando QR")
    
    # Verificar backend
    backend_url = 'https://whatsapp-server-production-8f61.up.railway.app'
    
    try:
        # Paso 1: Iniciar sesión
        print("🚀 Iniciando sesión...")
        init_response = requests.post(f'{backend_url}/init_session', timeout=15)
        
        if init_response.status_code == 200:
            print("✅ Sesión iniciada")
            
            # Paso 2: Obtener QR
            print("📱 Obteniendo QR...")
            qr_response = requests.get(f'{backend_url}/qr', timeout=10)
            
            if qr_response.status_code == 200:
                qr_data = qr_response.json()
                
                print(f"✅ QR obtenido: {json.dumps(qr_data, indent=2)}")
                
                if 'qr_data' in qr_data and qr_data['qr_data']:
                    qr_content = qr_data['qr_data']
                    print(f"📱 QR Data: {len(qr_content)} caracteres")
                    
                    if qr_content.startswith('data:image/'):
                        print("✅ QR es una imagen base64 - Se mostrará directamente")
                        print(f"📷 Formato: {qr_content.split(',')[0]}")
                        return True
                    else:
                        print("✅ QR es texto - Se usará QRCode.js")
                        print(f"📝 Contenido: {qr_content[:50]}...")
                        return True
                else:
                    print("❌ No hay datos de QR")
                    return False
            else:
                print(f"❌ Error obteniendo QR: {qr_response.status_code}")
                return False
        else:
            print(f"❌ Error iniciando sesión: {init_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_qrcode_js():
    """Verificar que QRCode.js está disponible"""
    print("\n🔍 VERIFICANDO QRCODE.JS")
    
    try:
        # Probar el nuevo CDN
        response = requests.get('https://cdnjs.cloudflare.com/ajax/libs/qrcode/1.5.3/qrcode.min.js', timeout=10)
        if response.status_code == 200:
            print("✅ QRCode.js está disponible en CDNJS")
            print(f"   Tamaño: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 PRUEBA RÁPIDA DE QR WHATSAPP WEB")
    print("=" * 40)
    
    # Test 1: Verificar QR
    qr_ok = test_qr_display()
    
    # Test 2: Verificar QRCode.js
    qrcode_ok = test_qrcode_js()
    
    # Resumen
    print("\n" + "=" * 40)
    print("📋 RESUMEN:")
    
    if qr_ok and qrcode_ok:
        print("✅ Todo funcionando correctamente")
        print("💡 El QR debería mostrarse en el frontend")
        print("\n🚀 PRÓXIMOS PASOS:")
        print("1. Abrir el panel de WhatsApp Web en NORA")
        print("2. Hacer clic en 'Flujo Automático' o 'Iniciar Sesión'")
        print("3. El QR debería aparecer automáticamente")
    elif qr_ok:
        print("⚠️ QR funciona pero hay problemas con QRCode.js")
        print("💡 El QR se mostrará como imagen (fallback)")
    elif qrcode_ok:
        print("⚠️ QRCode.js funciona pero hay problemas con el QR")
        print("💡 Revisar backend de Railway")
    else:
        print("❌ Problemas con QR y QRCode.js")
        print("💡 Revisar configuración completa")

if __name__ == "__main__":
    main()
