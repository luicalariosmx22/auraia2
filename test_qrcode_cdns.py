#!/usr/bin/env python3
"""
Test de conectividad a CDNs de QRCode.js
"""

import requests

def test_qrcode_cdns():
    """Test de conectividad a diferentes CDNs de QRCode.js"""
    
    print("📡 TEST CONECTIVIDAD CDNs QRCode.js")
    print("="*40)
    
    cdns = [
        {
            'name': 'CDNJS (original)',
            'url': 'https://cdnjs.cloudflare.com/ajax/libs/qrcode/1.5.3/qrcode.min.js'
        },
        {
            'name': 'jsDelivr',
            'url': 'https://cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js'
        },
        {
            'name': 'unpkg',
            'url': 'https://unpkg.com/qrcode@1.5.3/build/qrcode.min.js'
        },
        {
            'name': 'QR Server API',
            'url': 'https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=test'
        }
    ]
    
    for cdn in cdns:
        print(f"\n🧪 Probando: {cdn['name']}")
        print(f"   URL: {cdn['url']}")
        
        try:
            response = requests.get(cdn['url'], timeout=10)
            print(f"   📊 Status: {response.status_code}")
            print(f"   📏 Tamaño: {len(response.content)} bytes")
            
            if response.status_code == 200:
                if 'qrcode' in cdn['url'].lower() and 'api.qrserver' not in cdn['url']:
                    # Es una biblioteca JS
                    content = response.text
                    if 'QRCode' in content and 'function' in content:
                        print(f"   ✅ Biblioteca JS válida")
                    else:
                        print(f"   ⚠️ Contenido sospechoso")
                else:
                    # Es API de imagen
                    if response.headers.get('content-type', '').startswith('image'):
                        print(f"   ✅ API de imagen funciona")
                    else:
                        print(f"   ⚠️ No es imagen")
                        
            else:
                print(f"   ❌ Error HTTP")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_qrcode_cdns()
