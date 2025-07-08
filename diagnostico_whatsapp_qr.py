#!/usr/bin/env python3
"""
Diagnóstico completo del sistema WhatsApp Web - QR
Verifica todo el flujo desde el backend hasta el frontend
"""

import requests
import json
import time
import sys
from datetime import datetime

def print_header(title):
    """Imprimir header con formato"""
    print(f"\n{'='*50}")
    print(f"🔍 {title}")
    print(f"{'='*50}")

def check_backend_health():
    """Verificar salud del backend"""
    print_header("VERIFICANDO BACKEND RAILWAY")
    
    backend_url = 'https://whatsapp-server-production-8f61.up.railway.app'
    
    try:
        # Health check
        response = requests.get(f'{backend_url}/health', timeout=10)
        print(f"✅ Backend responde: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Backend está funcionando correctamente")
            return True
        else:
            print(f"❌ Backend error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando al backend: {e}")
        return False

def check_backend_endpoints():
    """Verificar endpoints específicos del backend"""
    print_header("VERIFICANDO ENDPOINTS DEL BACKEND")
    
    backend_url = 'https://whatsapp-server-production-8f61.up.railway.app'
    endpoints = [
        '/health',
        '/status',
        '/qr',
        '/init_session',
        '/close_session'
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            if endpoint in ['/init_session', '/close_session']:
                # POST endpoints
                response = requests.post(f'{backend_url}{endpoint}', timeout=10)
            else:
                # GET endpoints
                response = requests.get(f'{backend_url}{endpoint}', timeout=10)
            
            print(f"📡 {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    results[endpoint] = data
                    print(f"   ✅ JSON válido: {json.dumps(data, indent=2)[:100]}...")
                except json.JSONDecodeError:
                    print(f"   ⚠️ Respuesta HTML (no JSON)")
                    results[endpoint] = {'content_type': 'html', 'status': 'ok'}
            else:
                print(f"   ❌ Error: {response.status_code}")
                results[endpoint] = {'error': response.status_code}
                
        except Exception as e:
            print(f"   ❌ Excepción: {e}")
            results[endpoint] = {'error': str(e)}
    
    return results

def test_qr_generation():
    """Probar generación de QR"""
    print_header("PROBANDO GENERACIÓN DE QR")
    
    backend_url = 'https://whatsapp-server-production-8f61.up.railway.app'
    
    try:
        # Paso 1: Inicializar sesión
        print("🚀 Paso 1: Iniciando sesión...")
        init_response = requests.post(f'{backend_url}/init_session', timeout=15)
        print(f"   Status: {init_response.status_code}")
        
        if init_response.status_code == 200:
            print("   ✅ Sesión iniciada")
            
            # Paso 2: Esperar un poco
            print("⏳ Paso 2: Esperando 3 segundos...")
            time.sleep(3)
            
            # Paso 3: Obtener QR
            print("📱 Paso 3: Obteniendo QR...")
            qr_response = requests.get(f'{backend_url}/qr', timeout=10)
            print(f"   Status: {qr_response.status_code}")
            
            if qr_response.status_code == 200:
                try:
                    qr_data = qr_response.json()
                    print(f"   ✅ QR obtenido: {json.dumps(qr_data, indent=2)}")
                    
                    if 'qr_data' in qr_data and qr_data['qr_data']:
                        print(f"   📱 QR Data disponible: {len(qr_data['qr_data'])} caracteres")
                        print(f"   📱 QR Preview: {qr_data['qr_data'][:50]}...")
                        return qr_data['qr_data']
                    else:
                        print("   ⚠️ No hay datos de QR en la respuesta")
                        return None
                        
                except json.JSONDecodeError:
                    print("   ❌ Respuesta QR no es JSON válido")
                    return None
            else:
                print(f"   ❌ Error obteniendo QR: {qr_response.status_code}")
                print(f"   ❌ Respuesta: {qr_response.text}")
                return None
        else:
            print(f"   ❌ Error iniciando sesión: {init_response.status_code}")
            print(f"   ❌ Respuesta: {init_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en test QR: {e}")
        return None

def test_nora_integration():
    """Probar integración con NORA"""
    print_header("PROBANDO INTEGRACIÓN CON NORA")
    
    try:
        # Importar cliente NORA
        sys.path.append('/mnt/c/Users/PC/PYTHON/Auraai2')
        from clientes.aura.utils.whatsapp_websocket_client import WhatsAppWebSocketClient
        
        print("✅ Cliente NORA importado exitosamente")
        
        # Crear cliente
        client = WhatsAppWebSocketClient()
        print("✅ Cliente creado")
        
        # Health check
        health = client.get_health_status()
        if health:
            print(f"✅ Health check: {health}")
        else:
            print("❌ Health check falló")
            
        # Conectar
        if client.connect():
            print("✅ Conectado al backend")
            
            # Iniciar sesión
            if client.init_session():
                print("✅ Sesión iniciada")
                
                # Esperar QR
                print("⏳ Esperando QR...")
                time.sleep(5)
                
                qr = client.get_qr_code()
                if qr:
                    print(f"✅ QR obtenido: {len(qr)} caracteres")
                    print(f"📱 QR Preview: {qr[:50]}...")
                else:
                    print("❌ No se obtuvo QR")
                
                # Desconectar
                client.disconnect()
            else:
                print("❌ Error iniciando sesión")
        else:
            print("❌ Error conectando")
            
    except Exception as e:
        print(f"❌ Error en integración NORA: {e}")
        import traceback
        traceback.print_exc()

def test_frontend_libraries():
    """Verificar bibliotecas del frontend"""
    print_header("VERIFICANDO BIBLIOTECAS FRONTEND")
    
    try:
        # Verificar si QRCode.js está disponible
        qr_js_url = 'https://cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js'
        response = requests.get(qr_js_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ QRCode.js está disponible en CDN")
            print(f"   Tamaño: {len(response.content)} bytes")
        else:
            print(f"❌ Error obteniendo QRCode.js: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error verificando bibliotecas: {e}")

def main():
    """Función principal de diagnóstico"""
    print(f"🔍 DIAGNÓSTICO WHATSAPP WEB QR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar backend
    backend_ok = check_backend_health()
    if not backend_ok:
        print("\n❌ El backend no está funcionando. Saliendo...")
        return
    
    # Verificar endpoints
    endpoints_result = check_backend_endpoints()
    
    # Probar generación de QR
    qr_data = test_qr_generation()
    
    # Probar integración NORA
    test_nora_integration()
    
    # Verificar bibliotecas frontend
    test_frontend_libraries()
    
    # Resumen
    print_header("RESUMEN DEL DIAGNÓSTICO")
    
    if qr_data:
        print("✅ QR generado exitosamente")
        print("💡 El problema puede estar en el frontend o en la integración")
        print("\n🔧 PRÓXIMOS PASOS:")
        print("1. Verificar que el frontend esté cargando QRCode.js")
        print("2. Verificar que el blueprint esté usando el cliente correcto")
        print("3. Verificar que los logs del frontend muestren el QR")
    else:
        print("❌ No se pudo generar QR")
        print("💡 El problema está en el backend o en la comunicación")
        print("\n🔧 PRÓXIMOS PASOS:")
        print("1. Verificar logs del backend Railway")
        print("2. Verificar que Chrome/Selenium esté funcionando en Railway")
        print("3. Considerar usar modo fallback")

if __name__ == "__main__":
    main()
