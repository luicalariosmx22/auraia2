#!/usr/bin/env python3
"""
Test específico para la conexión WebSocket del cliente WhatsApp
"""

import sys
import time
import socketio
import requests
from datetime import datetime

def test_websocket_connection():
    """Probar conexión WebSocket directa"""
    print("🧪 PRUEBA ESPECÍFICA DE CONEXIÓN WEBSOCKET")
    print("=" * 60)
    
    backend_url = "https://whatsapp-server-production-8f61.up.railway.app"
    
    # 1. Verificar que el backend esté disponible
    print("1️⃣ Verificando backend Railway...")
    try:
        response = requests.get(f"{backend_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend Railway disponible")
        else:
            print(f"⚠️ Backend Railway: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend Railway no disponible: {e}")
        return False
    
    # 2. Probar conexión WebSocket directa
    print("\n2️⃣ Probando conexión WebSocket directa...")
    
    try:
        # Crear cliente Socket.IO
        sio = socketio.Client(
            logger=False,
            engineio_logger=False,
            reconnection=True,
            reconnection_attempts=3,
            reconnection_delay=1
        )
        
        # Variables para capturar eventos
        connected = False
        error_occurred = False
        events_received = []
        
        @sio.event
        def connect():
            nonlocal connected
            connected = True
            print("✅ WebSocket conectado exitosamente")
            events_received.append("connect")
        
        @sio.event
        def disconnect():
            print("🔌 WebSocket desconectado")
            events_received.append("disconnect")
        
        @sio.event
        def connect_error(data):
            nonlocal error_occurred
            error_occurred = True
            print(f"❌ Error de conexión WebSocket: {data}")
            events_received.append(f"connect_error: {data}")
        
        @sio.event
        def qr_code(data):
            print(f"📱 QR recibido: {data}")
            events_received.append(f"qr_code: {data}")
        
        @sio.event
        def whatsapp_status(data):
            print(f"📊 Estado WhatsApp: {data}")
            events_received.append(f"whatsapp_status: {data}")
        
        print(f"🔗 Intentando conectar a: {backend_url}")
        
        # Intentar conectar
        sio.connect(backend_url, transports=['websocket', 'polling'])
        
        # Esperar un poco para la conexión
        time.sleep(3)
        
        if connected:
            print("✅ Conexión WebSocket exitosa")
            
            # Probar envío de eventos
            print("\n3️⃣ Probando eventos WebSocket...")
            
            # Solicitar QR
            print("📱 Solicitando QR...")
            sio.emit('get_qr', {
                'timestamp': datetime.now().isoformat()
            })
            
            # Esperar respuesta
            time.sleep(5)
            
            # Verificar estado
            print("📊 Verificando estado...")
            sio.emit('get_status', {
                'timestamp': datetime.now().isoformat()
            })
            
            time.sleep(3)
            
            print(f"\n📋 Eventos recibidos: {events_received}")
            
            # Desconectar
            sio.disconnect()
            
            return True
            
        else:
            print("❌ No se pudo conectar al WebSocket")
            print(f"📋 Eventos recibidos: {events_received}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba WebSocket: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_nora_websocket_client():
    """Probar el cliente WebSocket de NORA"""
    print("\n4️⃣ PROBANDO CLIENTE WEBSOCKET DE NORA")
    print("-" * 40)
    
    try:
        # Importar el cliente de NORA
        sys.path.append('/mnt/c/Users/PC/PYTHON/Auraai2')
        from clientes.aura.utils.whatsapp_websocket_client import WhatsAppWebSocketClient
        
        # Crear cliente
        client = WhatsAppWebSocketClient()
        print(f"✅ Cliente WebSocket creado: {client.backend_url}")
        
        # Probar health check
        print("🏥 Probando health check...")
        health = client.get_health_status()
        print(f"❤️ Health: {health}")
        
        # Probar conexión
        print("🔗 Probando conexión...")
        success = client.connect()
        print(f"📡 Conexión: {'✅ Exitosa' if success else '❌ Fallida'}")
        
        if success:
            print("⏰ Esperando eventos...")
            time.sleep(3)
            
            # Probar obtener QR
            print("📱 Probando obtener QR...")
            qr_data = client.get_qr_code()
            print(f"📱 QR: {qr_data[:50] + '...' if qr_data else 'No disponible'}")
            
            # Probar estado detallado
            print("📊 Probando estado detallado...")
            status = client.get_detailed_status()
            print(f"📋 Status: {status}")
            
            # Desconectar
            client.disconnect()
        
        return success
        
    except Exception as e:
        print(f"❌ Error probando cliente NORA: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("🧪 DIAGNÓSTICO COMPLETO WEBSOCKET WHATSAPP")
    print("=" * 60)
    
    # Probar conexión WebSocket directa
    ws_success = test_websocket_connection()
    
    # Probar cliente de NORA
    nora_success = test_nora_websocket_client()
    
    print("\n" + "=" * 60)
    print("🏁 RESUMEN DE PRUEBAS")
    print(f"WebSocket Directo: {'✅ OK' if ws_success else '❌ FALLO'}")
    print(f"Cliente NORA: {'✅ OK' if nora_success else '❌ FALLO'}")
    
    if not ws_success:
        print("\n⚠️ PROBLEMA: La conexión WebSocket directa falla")
        print("💡 Posibles causas:")
        print("   - El backend Railway no soporta WebSocket")
        print("   - Problemas de CORS")
        print("   - Configuración incorrecta del cliente")
    
    if not nora_success:
        print("\n⚠️ PROBLEMA: El cliente NORA falla")
        print("💡 Posibles causas:")
        print("   - Error en la implementación del cliente")
        print("   - Configuración incorrecta")
        print("   - Problemas de importación")

if __name__ == "__main__":
    main()
