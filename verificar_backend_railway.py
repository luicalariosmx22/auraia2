#!/usr/bin/env python3
"""
Verificar endpoints disponibles en el backend de Railway
"""

import requests
import json
from datetime import datetime

def check_backend_endpoints():
    """Verificar todos los endpoints del backend"""
    print("🔍 VERIFICANDO ENDPOINTS DEL BACKEND RAILWAY")
    print("=" * 50)
    
    backend_url = 'https://whatsapp-server-production-8f61.up.railway.app'
    
    # Endpoints a probar
    endpoints = [
        ('GET', '/'),
        ('GET', '/health'),
        ('GET', '/status'),
        ('GET', '/qr'),
        ('POST', '/init_session'),
        ('POST', '/start_session'),
        ('POST', '/get_qr'),
        ('POST', '/close_session'),
        ('POST', '/disconnect'),
        ('POST', '/check_status'),
        ('GET', '/api/status'),
        ('GET', '/api/qr'),
        ('POST', '/api/start'),
        ('POST', '/api/stop'),
    ]
    
    available_endpoints = []
    
    for method, endpoint in endpoints:
        try:
            print(f"📡 Probando {method} {endpoint}...")
            
            if method == 'GET':
                response = requests.get(f'{backend_url}{endpoint}', timeout=10)
            else:
                response = requests.post(f'{backend_url}{endpoint}', timeout=10)
            
            status = response.status_code
            
            if status == 200:
                print(f"   ✅ {status}: Disponible")
                available_endpoints.append((method, endpoint, status))
                
                # Mostrar respuesta si es JSON
                try:
                    data = response.json()
                    print(f"   📄 JSON: {json.dumps(data, indent=2)[:150]}...")
                except:
                    print(f"   📄 Respuesta: {response.text[:100]}...")
                    
            elif status == 404:
                print(f"   ❌ {status}: No encontrado")
            elif status == 405:
                print(f"   ⚠️ {status}: Método no permitido")
            else:
                print(f"   ⚠️ {status}: {response.text[:50]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("📋 ENDPOINTS DISPONIBLES:")
    for method, endpoint, status in available_endpoints:
        print(f"   ✅ {method} {endpoint} ({status})")
    
    return available_endpoints

def test_websocket_connection():
    """Probar conexión WebSocket"""
    print("\n🔌 PROBANDO CONEXIÓN WEBSOCKET")
    print("=" * 50)
    
    try:
        import socketio
        
        backend_url = 'https://whatsapp-server-production-8f61.up.railway.app'
        
        # Crear cliente Socket.IO
        sio = socketio.Client(logger=False, engineio_logger=False)
        
        @sio.event
        def connect():
            print("✅ WebSocket conectado")
        
        @sio.event
        def disconnect():
            print("🔌 WebSocket desconectado")
        
        @sio.event
        def qr_code(data):
            print(f"📱 QR recibido: {data}")
        
        # Conectar
        print(f"🔗 Conectando a {backend_url}...")
        sio.connect(backend_url, wait_timeout=10)
        
        # Probar emitir get_qr
        print("📱 Solicitando QR...")
        sio.emit('get_qr', {'timestamp': datetime.now().isoformat()})
        
        # Esperar respuesta
        sio.sleep(5)
        
        # Desconectar
        sio.disconnect()
        
    except Exception as e:
        print(f"❌ Error WebSocket: {e}")

def main():
    """Función principal"""
    print(f"🔍 VERIFICACIÓN DE BACKEND RAILWAY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar endpoints
    available_endpoints = check_backend_endpoints()
    
    # Verificar WebSocket
    test_websocket_connection()
    
    print("\n" + "=" * 50)
    print("🎯 CONCLUSIONES:")
    
    if available_endpoints:
        print("✅ Backend está funcionando")
        print("💡 Endpoints disponibles encontrados")
        
        # Buscar endpoint para iniciar sesión
        start_endpoints = [ep for ep in available_endpoints if any(word in ep[1].lower() for word in ['start', 'init', 'session'])]
        if start_endpoints:
            print(f"🚀 Endpoint para iniciar sesión: {start_endpoints[0][1]}")
        else:
            print("⚠️ No se encontró endpoint para iniciar sesión")
            
        # Buscar endpoint para QR
        qr_endpoints = [ep for ep in available_endpoints if 'qr' in ep[1].lower()]
        if qr_endpoints:
            print(f"📱 Endpoint para QR: {qr_endpoints[0][1]}")
        else:
            print("⚠️ No se encontró endpoint para QR")
    else:
        print("❌ No se encontraron endpoints funcionales")

if __name__ == "__main__":
    main()
