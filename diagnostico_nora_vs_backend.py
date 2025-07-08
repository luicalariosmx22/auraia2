#!/usr/bin/env python3
"""
Diagnóstico específico del problema entre NORA y el WebSocket
"""

import socketio
import time
import requests
from datetime import datetime

# URLs
NORA_URL = "http://localhost:5000"
BACKEND_URL = "https://whatsapp-server-production-8f61.up.railway.app"

class NORAWebSocketDiagnostic:
    def __init__(self):
        self.backend_events = []
        self.nora_responses = []
        
    def test_backend_directly(self):
        """Probar el backend WebSocket directamente (como en el log exitoso)"""
        print("🔗 PROBANDO BACKEND WEBSOCKET DIRECTAMENTE")
        print("=" * 50)
        
        # Cliente Socket.IO directo
        sio = socketio.Client(logger=False, engineio_logger=False)
        connected = False
        
        @sio.event
        def connect():
            nonlocal connected
            connected = True
            print("✅ Conectado al backend WebSocket")
        
        @sio.event
        def status(data):
            print(f"📊 Status recibido: {data}")
            self.backend_events.append(('status', data))
        
        @sio.event
        def error(data):
            print(f"❌ Error recibido: {data}")
            self.backend_events.append(('error', data))
        
        @sio.event
        def qr_code(data):
            print(f"📱 QR recibido: {data}")
            self.backend_events.append(('qr_code', data))
        
        try:
            # Conectar
            print(f"🔗 Conectando a {BACKEND_URL}...")
            sio.connect(BACKEND_URL)
            
            # Esperar conexión
            timeout = 10
            while timeout > 0 and not connected:
                time.sleep(0.1)
                timeout -= 0.1
            
            if not connected:
                print("❌ No se pudo conectar")
                return False
            
            # Probar get_status (como en el log exitoso)
            print("🧪 Enviando get_status...")
            start_time = time.time()
            sio.emit('get_status')
            
            # Esperar respuesta
            time.sleep(3)
            elapsed = time.time() - start_time
            print(f"⏱️ get_status completado en {elapsed:.2f}s")
            
            # Probar get_qr
            print("🧪 Enviando get_qr...")
            start_time = time.time()
            sio.emit('get_qr', {'session_id': 'test-nora-session'})
            
            # Esperar respuesta
            time.sleep(3)
            elapsed = time.time() - start_time
            print(f"⏱️ get_qr completado en {elapsed:.2f}s")
            
            # Desconectar
            sio.disconnect()
            print("✅ Prueba directa del backend completada")
            return True
            
        except Exception as e:
            print(f"❌ Error probando backend: {e}")
            return False
    
    def test_nora_endpoints(self):
        """Probar endpoints de NORA que usan el WebSocket"""
        print("\n🔗 PROBANDO ENDPOINTS DE NORA")
        print("=" * 50)
        
        endpoints = [
            ('/panel_cliente/aura/whatsapp/status', 'GET', 'Status endpoint'),
            ('/panel_cliente/aura/whatsapp/qr', 'GET', 'QR endpoint'),
            ('/panel_cliente/aura/whatsapp/get_qr_auto', 'POST', 'QR Auto endpoint'),
        ]
        
        for endpoint, method, description in endpoints:
            url = f"{NORA_URL}{endpoint}"
            print(f"\n🧪 {description}: {method} {endpoint}")
            
            try:
                start_time = time.time()
                
                if method == 'GET':
                    response = requests.get(url, timeout=10)
                else:
                    response = requests.post(url, json={}, timeout=10)
                
                elapsed = time.time() - start_time
                
                print(f"⏱️ Tiempo: {elapsed:.2f}s")
                print(f"📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"✅ Respuesta JSON exitosa")
                        if 'success' in data:
                            print(f"   Success: {data['success']}")
                        if 'message' in data:
                            print(f"   Message: {data['message']}")
                        self.nora_responses.append((endpoint, 'success', elapsed, data))
                    except:
                        print(f"✅ Respuesta HTML (panel)")
                        self.nora_responses.append((endpoint, 'html', elapsed, None))
                else:
                    print(f"❌ Error HTTP {response.status_code}")
                    self.nora_responses.append((endpoint, 'error', elapsed, response.status_code))
                    
            except requests.exceptions.Timeout:
                elapsed = time.time() - start_time
                print(f"⏱️ TIMEOUT después de {elapsed:.2f}s")
                self.nora_responses.append((endpoint, 'timeout', elapsed, None))
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"❌ Error: {e}")
                self.nora_responses.append((endpoint, 'exception', elapsed, str(e)))
    
    def test_nora_websocket_client(self):
        """Probar el cliente WebSocket de NORA específicamente"""
        print("\n🔗 PROBANDO CLIENTE WEBSOCKET DE NORA")
        print("=" * 50)
        
        try:
            # Importar el cliente de NORA
            from clientes.aura.utils.whatsapp_websocket_client import WhatsAppWebSocketClient
            
            print("✅ Cliente WebSocket importado exitosamente")
            
            # Crear cliente
            client = WhatsAppWebSocketClient(BACKEND_URL)
            print("✅ Cliente WebSocket creado")
            
            # Probar conexión
            print("🔗 Probando conexión...")
            start_time = time.time()
            success = client.connect()
            elapsed = time.time() - start_time
            
            if success:
                print(f"✅ Conexión exitosa en {elapsed:.2f}s")
                
                # Probar get_qr_code
                print("📱 Probando get_qr_code...")
                start_time = time.time()
                qr = client.get_qr_code()
                elapsed = time.time() - start_time
                
                print(f"⏱️ get_qr_code completado en {elapsed:.2f}s")
                if qr:
                    print(f"✅ QR obtenido: {len(qr)} chars")
                else:
                    print("⚠️ No hay QR disponible")
                
                # Desconectar
                client.disconnect()
                print("✅ Cliente desconectado")
                
            else:
                print(f"❌ Conexión falló en {elapsed:.2f}s")
                
        except Exception as e:
            print(f"❌ Error con cliente NORA: {e}")
            import traceback
            traceback.print_exc()
    
    def compare_results(self):
        """Comparar resultados entre backend directo y NORA"""
        print("\n📊 COMPARACIÓN DE RESULTADOS")
        print("=" * 50)
        
        print("🔗 Backend WebSocket directo:")
        for event_type, data in self.backend_events:
            print(f"  ✅ {event_type}: {data.get('message', 'OK')}")
        
        print("\n🔗 Endpoints de NORA:")
        for endpoint, status, elapsed, data in self.nora_responses:
            status_icon = "✅" if status == "success" else "⚠️" if status == "html" else "❌"
            print(f"  {status_icon} {endpoint}: {status} ({elapsed:.2f}s)")
        
        # Diagnóstico
        backend_works = len(self.backend_events) > 0
        nora_works = any(status in ['success', 'html'] for _, status, _, _ in self.nora_responses)
        
        print(f"\n🎯 DIAGNÓSTICO:")
        print(f"  Backend WebSocket: {'✅ Funciona' if backend_works else '❌ No funciona'}")
        print(f"  NORA Endpoints: {'✅ Funciona' if nora_works else '❌ No funciona'}")
        
        if backend_works and not nora_works:
            print(f"  💡 PROBLEMA: NORA no puede usar el WebSocket correctamente")
            print(f"     - Posible deadlock en el cliente Python")
            print(f"     - Timeouts excesivos en las operaciones")
            print(f"     - Bloqueo en la instancia global del cliente")
        elif backend_works and nora_works:
            print(f"  💡 TODO OK: Ambos funcionan correctamente")
        else:
            print(f"  💡 PROBLEMA: El backend WebSocket también tiene problemas")

def main():
    """Función principal"""
    print("🔍 DIAGNÓSTICO ESPECÍFICO NORA vs BACKEND WEBSOCKET")
    print("=" * 70)
    print(f"🎯 Backend: {BACKEND_URL}")
    print(f"🎯 NORA: {NORA_URL}")
    print(f"🕒 Inicio: {datetime.now()}")
    
    diagnostic = NORAWebSocketDiagnostic()
    
    try:
        # 1. Probar backend directamente
        print("\n1️⃣ FASE: BACKEND DIRECTO")
        print("=" * 30)
        diagnostic.test_backend_directly()
        
        # 2. Probar endpoints de NORA
        print("\n2️⃣ FASE: ENDPOINTS DE NORA")
        print("=" * 30)
        diagnostic.test_nora_endpoints()
        
        # 3. Probar cliente específico de NORA
        print("\n3️⃣ FASE: CLIENTE WEBSOCKET DE NORA")
        print("=" * 30)
        diagnostic.test_nora_websocket_client()
        
        # 4. Comparar resultados
        print("\n4️⃣ FASE: COMPARACIÓN")
        print("=" * 30)
        diagnostic.compare_results()
        
    except KeyboardInterrupt:
        print("\n⛔ Diagnóstico interrumpido")
    except Exception as e:
        print(f"\n❌ Error durante diagnóstico: {e}")

if __name__ == "__main__":
    main()
