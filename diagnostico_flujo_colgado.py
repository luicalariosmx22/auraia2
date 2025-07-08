#!/usr/bin/env python3
"""
Diagnóstico específico del flujo automático y QR que se cuelga
"""

import requests
import socketio
import time
import threading
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:5000"
CLIENTE = "aura"
WHATSAPP_URL = f"{BASE_URL}/panel_cliente/{CLIENTE}/whatsapp"
BACKEND_WS_URL = 'https://whatsapp-server-production-8f61.up.railway.app'

class FlowDiagnostic:
    def __init__(self):
        self.ws_connected = False
        self.ws_events = []
        self.sio = None
    
    def setup_websocket(self):
        """Configurar WebSocket para monitorear eventos"""
        self.sio = socketio.Client(logger=False, engineio_logger=False)
        
        @self.sio.event
        def connect():
            self.ws_connected = True
            self.ws_events.append(f"{datetime.now()} - WS CONNECT")
            print("🔗 WebSocket conectado")
        
        @self.sio.event
        def disconnect():
            self.ws_connected = False
            self.ws_events.append(f"{datetime.now()} - WS DISCONNECT")
            print("🔌 WebSocket desconectado")
        
        @self.sio.event
        def connected(data):
            self.ws_events.append(f"{datetime.now()} - WS CONNECTED: {data}")
            print(f"📡 WS Connected: {data}")
        
        @self.sio.event
        def qr_code(data):
            self.ws_events.append(f"{datetime.now()} - WS QR_CODE: {data}")
            print(f"📱 WS QR Code: {data}")
        
        @self.sio.event
        def error(data):
            self.ws_events.append(f"{datetime.now()} - WS ERROR: {data}")
            print(f"❌ WS Error: {data}")
    
    def test_http_endpoints(self):
        """Probar endpoints HTTP que usa el frontend"""
        print("\n🌐 PROBANDO ENDPOINTS HTTP")
        print("=" * 50)
        
        # 1. Test flujo automático
        print("\n1️⃣ Probando flujo automático...")
        try:
            start_time = time.time()
            response = requests.post(f"{WHATSAPP_URL}/get_qr_auto", 
                                   json={}, 
                                   headers={'Content-Type': 'application/json'},
                                   timeout=30)
            elapsed = time.time() - start_time
            
            print(f"⏱️ Tiempo respuesta: {elapsed:.2f}s")
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Respuesta: {data}")
            else:
                print(f"❌ Error: {response.text}")
                
        except requests.exceptions.Timeout:
            print("⏰ TIMEOUT - El endpoint se colgó")
        except Exception as e:
            print(f"❌ Excepción: {e}")
        
        # 2. Test refresh QR
        print("\n2️⃣ Probando refresh QR...")
        try:
            start_time = time.time()
            response = requests.get(f"{WHATSAPP_URL}/qr", timeout=30)
            elapsed = time.time() - start_time
            
            print(f"⏱️ Tiempo respuesta: {elapsed:.2f}s")
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Respuesta: {data}")
            else:
                print(f"❌ Error: {response.text}")
                
        except requests.exceptions.Timeout:
            print("⏰ TIMEOUT - El endpoint se colgó")
        except Exception as e:
            print(f"❌ Excepción: {e}")
        
        # 3. Test connect
        print("\n3️⃣ Probando connect...")
        try:
            start_time = time.time()
            response = requests.post(f"{WHATSAPP_URL}/connect", 
                                   json={}, 
                                   headers={'Content-Type': 'application/json'},
                                   timeout=30)
            elapsed = time.time() - start_time
            
            print(f"⏱️ Tiempo respuesta: {elapsed:.2f}s")
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Respuesta: {data}")
            else:
                print(f"❌ Error: {response.text}")
                
        except requests.exceptions.Timeout:
            print("⏰ TIMEOUT - El endpoint se colgó")
        except Exception as e:
            print(f"❌ Excepción: {e}")
    
    def test_websocket_flow(self):
        """Probar el flujo WebSocket directo"""
        print("\n🔗 PROBANDO FLUJO WEBSOCKET DIRECTO")
        print("=" * 50)
        
        try:
            # Conectar WebSocket
            print("🔄 Conectando WebSocket...")
            self.sio.connect(BACKEND_WS_URL, transports=['websocket', 'polling'])
            
            # Esperar conexión
            timeout = 10
            while timeout > 0 and not self.ws_connected:
                time.sleep(0.5)
                timeout -= 0.5
                print(f"⏱️ Esperando... {timeout:.1f}s")
            
            if self.ws_connected:
                print("✅ WebSocket conectado")
                
                # Solicitar QR
                print("📱 Solicitando QR via WebSocket...")
                self.sio.emit('get_qr', {
                    'session_id': 'test-flow',
                    'timestamp': datetime.now().isoformat()
                })
                
                # Esperar respuesta
                print("⏳ Esperando respuesta...")
                time.sleep(5)
                
                # Desconectar
                self.sio.disconnect()
                
            else:
                print("❌ No se pudo conectar WebSocket")
                
        except Exception as e:
            print(f"❌ Error WebSocket: {e}")
    
    def show_ws_events(self):
        """Mostrar eventos WebSocket capturados"""
        print("\n📋 EVENTOS WEBSOCKET CAPTURADOS")
        print("=" * 50)
        
        if self.ws_events:
            for event in self.ws_events:
                print(f"  {event}")
        else:
            print("  (No se capturaron eventos)")
    
    def test_frontend_simulation(self):
        """Simular exactamente lo que hace el frontend"""
        print("\n🎭 SIMULANDO FLUJO DEL FRONTEND")
        print("=" * 50)
        
        # Simular secuencia del botón "Flujo Automático"
        print("1️⃣ Simulando: connectToBackend() -> Conectar HTTP...")
        try:
            response = requests.post(f"{WHATSAPP_URL}/connect", 
                                   json={}, 
                                   headers={'Content-Type': 'application/json'},
                                   timeout=10)
            print(f"   Resultado: {response.status_code} - {response.json() if response.status_code == 200 else response.text}")
        except Exception as e:
            print(f"   Error: {e}")
        
        print("\n2️⃣ Simulando: initWhatsAppSession() -> Iniciar sesión...")
        try:
            response = requests.post(f"{WHATSAPP_URL}/init_session", 
                                   json={}, 
                                   headers={'Content-Type': 'application/json'},
                                   timeout=10)
            print(f"   Resultado: {response.status_code} - {response.json() if response.status_code == 200 else response.text}")
        except Exception as e:
            print(f"   Error: {e}")
        
        print("\n3️⃣ Simulando: refreshQR() -> Obtener QR...")
        try:
            response = requests.get(f"{WHATSAPP_URL}/qr", timeout=10)
            print(f"   Resultado: {response.status_code} - {response.json() if response.status_code == 200 else response.text}")
        except Exception as e:
            print(f"   Error: {e}")

def main():
    """Función principal de diagnóstico"""
    print("🔍 DIAGNÓSTICO DE FLUJO COLGADO")
    print("=" * 60)
    print(f"🕒 Inicio: {datetime.now()}")
    
    # Crear instancia de diagnóstico
    diagnostic = FlowDiagnostic()
    diagnostic.setup_websocket()
    
    try:
        # 1. Probar endpoints HTTP
        diagnostic.test_http_endpoints()
        
        # 2. Probar WebSocket directo
        diagnostic.test_websocket_flow()
        
        # 3. Simular frontend
        diagnostic.test_frontend_simulation()
        
        # 4. Mostrar eventos capturados
        diagnostic.show_ws_events()
        
    except KeyboardInterrupt:
        print("\n⛔ Diagnóstico interrumpido")
    
    print("\n🏁 DIAGNÓSTICO COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    main()
