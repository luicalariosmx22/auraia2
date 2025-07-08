#!/usr/bin/env python3
"""
Diagnóstico de conexión WebSocket con el backend de Railway
"""

import os
import sys
import json
import requests
import socketio
import threading
import time
from datetime import datetime

# URLs del backend
BACKEND_URL = 'https://whatsapp-server-production-8f61.up.railway.app'

def test_health_endpoint():
    """Verificar endpoint de salud"""
    print("🏥 VERIFICANDO ENDPOINT DE SALUD")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        print(f"📊 Status: {response.status_code}")
        print(f"📝 Headers: {dict(response.headers)}")
        print(f"📄 Content: {response.text[:200]}...")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ JSON Response: {json.dumps(data, indent=2)}")
            except:
                print("✅ HTML Response (OK)")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_websocket_connection():
    """Probar conexión WebSocket"""
    print("\n🔗 PROBANDO CONEXIÓN WEBSOCKET")
    print("=" * 60)
    
    # Variables para tracking
    connected = False
    events_received = []
    
    # Crear cliente Socket.IO
    sio = socketio.Client(
        logger=True,
        engineio_logger=True,
        reconnection=True,
        reconnection_attempts=3,
        reconnection_delay=1
    )
    
    # Event handlers
    @sio.event
    def connect():
        nonlocal connected
        connected = True
        events_received.append('connect')
        print("✅ Conectado al WebSocket")
    
    @sio.event
    def disconnect():
        nonlocal connected
        connected = False
        events_received.append('disconnect')
        print("🔌 Desconectado del WebSocket")
    
    @sio.event
    def connect_error(data):
        events_received.append(f'connect_error: {data}')
        print(f"❌ Error de conexión: {data}")
    
    @sio.event
    def qr_code(data):
        events_received.append(f'qr_code: {data}')
        print(f"📱 QR recibido: {data}")
    
    @sio.event
    def authenticated(data):
        events_received.append(f'authenticated: {data}')
        print(f"🎉 Autenticado: {data}")
    
    @sio.event
    def error(data):
        events_received.append(f'error: {data}')
        print(f"❌ Error: {data}")
    
    try:
        print(f"🔗 Intentando conectar a: {BACKEND_URL}")
        
        # Intentar conexión
        sio.connect(BACKEND_URL, transports=['websocket', 'polling'])
        
        # Esperar conexión
        timeout = 10
        while timeout > 0 and not connected:
            time.sleep(1)
            timeout -= 1
            print(f"⏱️ Esperando conexión... {timeout}s")
        
        if connected:
            print("✅ Conexión establecida exitosamente")
            
            # Probar envío de evento
            print("📤 Enviando evento de prueba...")
            sio.emit('get_qr', {
                'session_id': 'test-session',
                'timestamp': datetime.now().isoformat()
            })
            
            # Esperar respuesta
            time.sleep(5)
            
            # Mostrar eventos recibidos
            print("\n📋 EVENTOS RECIBIDOS:")
            for event in events_received:
                print(f"  - {event}")
            
            # Desconectar
            sio.disconnect()
            
        else:
            print("❌ No se pudo conectar al WebSocket")
            
    except Exception as e:
        print(f"❌ Error durante la conexión: {e}")
        import traceback
        traceback.print_exc()
    
    return connected

def test_http_endpoints():
    """Probar endpoints HTTP alternativos"""
    print("\n🌐 PROBANDO ENDPOINTS HTTP")
    print("=" * 60)
    
    endpoints = [
        "/",
        "/health",
        "/status",
        "/qr",
        "/socket.io/",
        "/socket.io/?EIO=4&transport=polling"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{BACKEND_URL}{endpoint}"
            response = requests.get(url, timeout=5)
            print(f"📍 {endpoint}: {response.status_code} - {response.text[:50]}...")
        except Exception as e:
            print(f"📍 {endpoint}: ERROR - {e}")

def main():
    """Función principal de diagnóstico"""
    print("🔍 DIAGNÓSTICO DE CONEXIÓN WEBSOCKET")
    print("=" * 60)
    print(f"🎯 Backend: {BACKEND_URL}")
    print(f"🕒 Timestamp: {datetime.now().isoformat()}")
    
    # 1. Verificar salud del backend
    health_ok = test_health_endpoint()
    
    # 2. Probar endpoints HTTP
    test_http_endpoints()
    
    # 3. Probar conexión WebSocket
    websocket_ok = test_websocket_connection()
    
    # Resumen
    print("\n🏁 RESUMEN")
    print("=" * 60)
    print(f"🏥 Health Check: {'✅ OK' if health_ok else '❌ FAIL'}")
    print(f"🔗 WebSocket: {'✅ OK' if websocket_ok else '❌ FAIL'}")
    
    if not health_ok:
        print("\n❌ El backend no está respondiendo correctamente")
        print("💡 Verifique que el backend esté desplegado y funcionando")
    
    if not websocket_ok:
        print("\n❌ La conexión WebSocket falló")
        print("💡 Posibles causas:")
        print("  - El backend no soporta Socket.IO")
        print("  - Configuración incorrecta de transporte")
        print("  - Problemas de red o firewall")
        print("  - El backend usa WebSocket nativo (no Socket.IO)")

if __name__ == "__main__":
    main()
