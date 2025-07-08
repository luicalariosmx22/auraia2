#!/usr/bin/env python3
"""
Diagnóstico simple de WebSocket
"""

import socketio
import time
import sys

BACKEND_URL = 'https://whatsapp-server-production-8f61.up.railway.app'

def test_simple_connection():
    """Prueba básica de conexión WebSocket"""
    print("🔗 PRUEBA SIMPLE DE WEBSOCKET")
    print("=" * 50)
    
    # Variables de estado
    connected = False
    events = []
    
    # Crear cliente Socket.IO simple
    sio = socketio.Client()
    
    # Event handlers
    @sio.event
    def connect():
        nonlocal connected
        connected = True
        events.append("CONNECT")
        print("✅ Conectado al WebSocket")
    
    @sio.event
    def disconnect():
        nonlocal connected
        connected = False
        events.append("DISCONNECT")
        print("🔌 Desconectado del WebSocket")
    
    @sio.event
    def connected(data):
        events.append(f"CONNECTED_EVENT: {data}")
        print(f"📡 Evento 'connected': {data}")
    
    @sio.event
    def connect_error(error):
        events.append(f"CONNECT_ERROR: {error}")
        print(f"❌ Error de conexión: {error}")
    
    @sio.event
    def error(data):
        events.append(f"ERROR: {data}")
        print(f"❌ Error: {data}")
    
    @sio.event
    def qr_code(data):
        events.append(f"QR_CODE: {data}")
        print(f"📱 QR Code: {data}")
    
    try:
        print(f"📡 Conectando a: {BACKEND_URL}")
        
        # Intentar conexión simple
        sio.connect(BACKEND_URL)
        
        # Esperar conexión
        timeout = 15
        while timeout > 0 and not connected:
            time.sleep(1)
            timeout -= 1
            print(f"⏱️ Esperando conexión... {timeout}s")
        
        if connected:
            print("✅ CONEXIÓN EXITOSA")
            
            # Esperar eventos iniciales
            print("📡 Esperando eventos del backend...")
            time.sleep(3)
            
            # Intentar solicitar QR
            print("📱 Solicitando QR...")
            try:
                sio.emit('get_qr', {
                    'test': True,
                    'timestamp': time.time()
                })
                
                # Esperar respuesta
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ Error enviando evento: {e}")
            
            # Desconectar
            print("🔌 Desconectando...")
            sio.disconnect()
            
        else:
            print("❌ CONEXIÓN FALLÓ")
        
        # Mostrar eventos recibidos
        print("\n📋 EVENTOS RECIBIDOS:")
        for i, event in enumerate(events, 1):
            print(f"  {i}. {event}")
        
        return connected
        
    except Exception as e:
        print(f"❌ EXCEPCIÓN: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 DIAGNÓSTICO WEBSOCKET SIMPLE")
    print("=" * 60)
    
    success = test_simple_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ RESULTADO: WebSocket funcionando correctamente")
    else:
        print("❌ RESULTADO: WebSocket no funciona")
        print("💡 Posibles causas:")
        print("  - Backend no soporta Socket.IO")
        print("  - Configuración incorrecta")
        print("  - Problemas de red")

if __name__ == "__main__":
    main()
