#!/usr/bin/env python3
"""
Test para simular la conexión WebSocket del frontend
"""

import socketio
import time
import threading
from datetime import datetime

# URL del backend Railway
BACKEND_URL = 'https://whatsapp-server-production-8f61.up.railway.app'

class FrontendWebSocketTest:
    def __init__(self):
        self.connected = False
        self.authenticated = False
        self.has_qr = False
        self.events_log = []
        
        # Cliente Socket.IO como en el frontend
        self.sio = socketio.Client(
            logger=False,
            engineio_logger=False,
            reconnection=True,
            reconnection_attempts=3,
            reconnection_delay=1
        )
        
        self.setup_events()
    
    def setup_events(self):
        """Configurar eventos como en el frontend"""
        
        @self.sio.event
        def connect():
            print("✅ Frontend conectado al backend WebSocket")
            self.connected = True
            self.events_log.append("CONNECT")
        
        @self.sio.event
        def disconnect():
            print("🔌 Frontend desconectado del backend")
            self.connected = False
            self.authenticated = False
            self.events_log.append("DISCONNECT")
        
        @self.sio.event
        def connected(data):
            print(f"📡 Evento 'connected' recibido: {data}")
            self.events_log.append(f"CONNECTED: {data}")
        
        @self.sio.event
        def qr_code(data):
            print(f"📱 QR Code recibido: {data}")
            self.has_qr = True
            self.events_log.append(f"QR_CODE: {data}")
        
        @self.sio.event
        def whatsapp_status(data):
            print(f"📊 Estado WhatsApp: {data}")
            self.events_log.append(f"STATUS: {data}")
        
        @self.sio.event
        def authenticated(data):
            print(f"🎉 Autenticado: {data}")
            self.authenticated = True
            self.events_log.append(f"AUTHENTICATED: {data}")
        
        @self.sio.event
        def error(data):
            print(f"❌ Error: {data}")
            self.events_log.append(f"ERROR: {data}")
        
        @self.sio.event
        def connect_error(error):
            print(f"❌ Error de conexión: {error}")
            self.events_log.append(f"CONNECT_ERROR: {error}")
    
    def connect_to_backend(self):
        """Conectar al backend como lo hace el frontend"""
        try:
            print(f"🔗 Conectando a: {BACKEND_URL}")
            self.sio.connect(BACKEND_URL, transports=['websocket', 'polling'])
            
            # Esperar conexión
            timeout = 10
            while timeout > 0 and not self.connected:
                time.sleep(1)
                timeout -= 1
                print(f"⏱️ Esperando conexión... {timeout}s")
            
            return self.connected
            
        except Exception as e:
            print(f"❌ Error conectando: {e}")
            return False
    
    def request_qr(self):
        """Solicitar QR como lo hace el frontend"""
        if not self.connected:
            print("❌ No conectado")
            return False
        
        try:
            print("📱 Solicitando QR...")
            self.sio.emit('get_qr', {
                'session_id': 'frontend-test',
                'timestamp': datetime.now().isoformat()
            })
            return True
        except Exception as e:
            print(f"❌ Error solicitando QR: {e}")
            return False
    
    def show_status(self):
        """Mostrar estado actual"""
        print("\n📊 ESTADO ACTUAL")
        print("=" * 40)
        print(f"🔗 Conectado: {self.connected}")
        print(f"🎉 Autenticado: {self.authenticated}")
        print(f"📱 Tiene QR: {self.has_qr}")
        print(f"📋 Eventos: {len(self.events_log)}")
        
        if self.events_log:
            print("\n🗂️ LOG DE EVENTOS:")
            for i, event in enumerate(self.events_log[-5:], 1):  # Últimos 5 eventos
                print(f"  {i}. {event}")
    
    def disconnect_from_backend(self):
        """Desconectar del backend"""
        if self.connected:
            self.sio.disconnect()
            print("🔌 Desconectado")

def main():
    """Función principal de prueba"""
    print("🧪 TEST DE CONEXIÓN WEBSOCKET FRONTEND")
    print("=" * 50)
    
    # Crear instancia de prueba
    test_client = FrontendWebSocketTest()
    
    # 1. Conectar al backend
    print("\n1️⃣ CONECTANDO AL BACKEND")
    connected = test_client.connect_to_backend()
    
    if connected:
        print("✅ Conexión exitosa")
        
        # 2. Esperar eventos iniciales
        print("\n2️⃣ ESPERANDO EVENTOS INICIALES")
        time.sleep(3)
        test_client.show_status()
        
        # 3. Solicitar QR
        print("\n3️⃣ SOLICITANDO QR")
        qr_requested = test_client.request_qr()
        
        if qr_requested:
            print("✅ QR solicitado")
            
            # 4. Esperar respuesta del QR
            print("\n4️⃣ ESPERANDO QR")
            time.sleep(5)
            test_client.show_status()
        
        # 5. Desconectar
        print("\n5️⃣ DESCONECTANDO")
        test_client.disconnect_from_backend()
        
    else:
        print("❌ Error de conexión")
    
    print("\n🏁 TEST COMPLETADO")

if __name__ == "__main__":
    main()
