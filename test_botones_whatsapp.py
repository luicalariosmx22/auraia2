#!/usr/bin/env python3
"""
Test de funcionalidad de botones WhatsApp Web
"""

import requests
import json
import time

def test_botones_whatsapp():
    """Test de todos los botones del panel WhatsApp"""
    
    print("🔘 TEST FUNCIONALIDAD BOTONES WHATSAPP WEB")
    print("="*50)
    
    base_url = "http://localhost:5000"
    whatsapp_base = f"{base_url}/panel_cliente/aura/whatsapp"
    
    # Lista de endpoints a probar
    endpoints = [
        {
            'name': 'Estado',
            'url': f"{whatsapp_base}/status",
            'method': 'GET',
            'expected': 'success'
        },
        {
            'name': 'Conectar',
            'url': f"{whatsapp_base}/connect",
            'method': 'POST',
            'expected': 'success'
        },
        {
            'name': 'Iniciar Sesión (QR Automático)',
            'url': f"{whatsapp_base}/get_qr_auto",
            'method': 'POST',
            'expected': 'success',
            'check_qr': True
        },
        {
            'name': 'Obtener QR',
            'url': f"{whatsapp_base}/qr",
            'method': 'GET',
            'expected': 'qr_data',
            'check_qr': True
        },
        {
            'name': 'Verificar Estado',
            'url': f"{whatsapp_base}/check_status",
            'method': 'POST',
            'expected': 'success'
        }
    ]
    
    resultados = []
    
    for endpoint in endpoints:
        print(f"\n🧪 Probando: {endpoint['name']}")
        print(f"   URL: {endpoint['url']}")
        print(f"   Método: {endpoint['method']}")
        
        try:
            if endpoint['method'] == 'POST':
                response = requests.post(
                    endpoint['url'],
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
            else:
                response = requests.get(endpoint['url'], timeout=10)
            
            print(f"   📊 Status: {response.status_code}")
            
            try:
                data = response.json()
                print(f"   📄 Response: {json.dumps(data, indent=2)[:200]}...")
                
                # Verificar resultado esperado
                success = False
                qr_found = False
                
                if endpoint['expected'] == 'success':
                    success = data.get('success', False)
                elif endpoint['expected'] == 'qr_data':
                    success = data.get('success', False) or data.get('qr_data') is not None
                    qr_found = data.get('qr_data') is not None
                
                # Verificar QR si es necesario
                if endpoint.get('check_qr', False):
                    if data.get('qr_data'):
                        qr_data = data['qr_data']
                        print(f"   📱 QR encontrado: {len(qr_data)} chars")
                        if qr_data.startswith('data:image/'):
                            print(f"   📱 Tipo: Imagen base64")
                        else:
                            print(f"   📱 Tipo: Texto")
                        qr_found = True
                    else:
                        print(f"   ⚠️ No hay QR en respuesta")
                
                resultado = "✅" if success else "❌"
                print(f"   {resultado} Resultado: {'OK' if success else 'ERROR'}")
                
                resultados.append({
                    'name': endpoint['name'],
                    'success': success,
                    'qr_found': qr_found,
                    'status_code': response.status_code
                })
                
            except json.JSONDecodeError:
                print(f"   📄 Text Response: {response.text[:200]}")
                resultados.append({
                    'name': endpoint['name'],
                    'success': False,
                    'qr_found': False,
                    'status_code': response.status_code
                })
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            resultados.append({
                'name': endpoint['name'],
                'success': False,
                'qr_found': False,
                'error': str(e)
            })
            
        time.sleep(1)  # Pequeña pausa entre requests
    
    # Resumen final
    print(f"\n📋 RESUMEN DE PRUEBAS")
    print("="*30)
    
    total = len(resultados)
    exitosos = sum(1 for r in resultados if r['success'])
    con_qr = sum(1 for r in resultados if r.get('qr_found', False))
    
    for resultado in resultados:
        status = "✅" if resultado['success'] else "❌"
        qr_status = "📱" if resultado.get('qr_found', False) else "   "
        print(f"{status} {qr_status} {resultado['name']}")
    
    print(f"\n📊 Estadísticas:")
    print(f"   Total: {total}")
    print(f"   Exitosos: {exitosos}/{total}")
    print(f"   Con QR: {con_qr}")
    
    if exitosos == total:
        print(f"\n🎉 ¡TODOS LOS BOTONES FUNCIONAN!")
    elif exitosos > total // 2:
        print(f"\n✅ La mayoría de botones funcionan")
    else:
        print(f"\n⚠️ Varios botones tienen problemas")
    
    if con_qr > 0:
        print(f"📱 ¡QR está funcionando! ({con_qr} endpoints devuelven QR)")
    else:
        print(f"❌ No se encontró QR en ningún endpoint")

if __name__ == "__main__":
    test_botones_whatsapp()
