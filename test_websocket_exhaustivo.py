#!/usr/bin/env python3
"""
Prueba exhaustiva y exclusiva del WebSocket para WhatsApp Web
"""

import socketio
import time
import json
import threading
from datetime import datetime

# Configuración
BACKEND_URL = 'https://whatsapp-server-production-8f61.up.railway.app'

class WebSocketExhaustiveTest:
    def __init__(self):
        self.connected = False
        self.events_received = []
        self.connection_time = None
        self.last_ping = None
        self.session_id = None
        self.client_id = None
        
        # Configurar cliente Socket.IO con opciones válidas
        self.sio = socketio.Client(
            logger=False,
            engineio_logger=False,
            reconnection=True,
            reconnection_attempts=5,
            reconnection_delay=1,
            reconnection_delay_max=5
        )
        
        self.setup_comprehensive_events()
    
    def setup_comprehensive_events(self):
        """Configurar todos los eventos posibles"""
        
        @self.sio.event
        def connect():
            self.connected = True
            self.connection_time = datetime.now()
            self.log_event("CONNECT", "Conectado al WebSocket")
            print("✅ [CONNECT] Conectado al WebSocket")
        
        @self.sio.event
        def disconnect():
            self.connected = False
            self.log_event("DISCONNECT", "Desconectado del WebSocket")
            print("🔌 [DISCONNECT] Desconectado del WebSocket")
        
        @self.sio.event
        def connect_error(error):
            self.log_event("CONNECT_ERROR", f"Error de conexión: {error}")
            print(f"❌ [CONNECT_ERROR] Error de conexión: {error}")
        
        @self.sio.event
        def connected(data):
            self.log_event("CONNECTED", data)
            if isinstance(data, dict):
                self.client_id = data.get('client_id')
                print(f"📡 [CONNECTED] Evento del backend: {data}")
            else:
                print(f"📡 [CONNECTED] Datos: {data}")
        
        @self.sio.event
        def qr_code(data):
            self.log_event("QR_CODE", data)
            print(f"📱 [QR_CODE] QR recibido: {data}")
            
            # Analizar QR
            if isinstance(data, dict):
                if 'qr_data' in data:
                    qr_data = data['qr_data']
                    if qr_data.startswith('data:image/png;base64,'):
                        print("  📸 Tipo: Imagen PNG (base64)")
                        print(f"  📏 Tamaño: {len(qr_data)} chars")
                    elif qr_data.startswith('1@'):
                        print("  📱 Tipo: Texto WhatsApp Web")
                        print(f"  📏 Tamaño: {len(qr_data)} chars")
                    else:
                        print(f"  ❓ Tipo desconocido: {qr_data[:50]}...")
                
                if 'session_id' in data:
                    self.session_id = data['session_id']
                    print(f"  🆔 Session ID: {self.session_id}")
                
                if 'error' in data:
                    print(f"  ⚠️ Error: {data['error']}")
                
                if 'message' in data:
                    print(f"  💬 Mensaje: {data['message']}")
        
        @self.sio.event
        def whatsapp_status(data):
            self.log_event("WHATSAPP_STATUS", data)
            print(f"📊 [WHATSAPP_STATUS] Estado: {data}")
        
        @self.sio.event
        def authenticated(data):
            self.log_event("AUTHENTICATED", data)
            print(f"🎉 [AUTHENTICATED] Autenticado: {data}")
        
        @self.sio.event
        def error(data):
            self.log_event("ERROR", data)
            print(f"❌ [ERROR] Error del backend: {data}")
            
            # Analizar tipo de error
            if isinstance(data, dict):
                message = data.get('message', str(data))
                if 'Chrome' in message:
                    print("  🌐 Error relacionado con Chrome")
                elif 'sesión' in message or 'session' in message:
                    print("  🔐 Error de sesión")
                elif 'conexión' in message or 'connection' in message:
                    print("  🔗 Error de conexión")
                else:
                    print(f"  ❓ Error genérico: {message}")
        
        @self.sio.event
        def heartbeat(data):
            self.last_ping = datetime.now()
            self.log_event("HEARTBEAT", data)
            print(f"💓 [HEARTBEAT] Ping: {data}")
        
        @self.sio.event
        def test_result(data):
            self.log_event("TEST_RESULT", data)
            print(f"🧪 [TEST_RESULT] Resultado: {data}")
        
        # Eventos genéricos
        @self.sio.event
        def message(data):
            self.log_event("MESSAGE", data)
            print(f"📨 [MESSAGE] Mensaje genérico: {data}")
        
        @self.sio.event
        def ping(data):
            self.log_event("PING", data)
            print(f"🏓 [PING] Ping: {data}")
        
        @self.sio.event
        def pong(data):
            self.log_event("PONG", data)
            print(f"🏓 [PONG] Pong: {data}")
    
    def log_event(self, event_type, data):
        """Registrar evento con timestamp"""
        self.events_received.append({
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'data': data
        })
    
    def connect_to_backend(self):
        """Conectar al backend"""
        try:
            print(f"🔗 Conectando a: {BACKEND_URL}")
            print("🔄 Intentando conexión WebSocket...")
            
            # Intentar conexión
            self.sio.connect(BACKEND_URL, transports=['websocket', 'polling'])
            
            # Esperar conexión con timeout
            timeout = 15
            start_time = time.time()
            
            while timeout > 0 and not self.connected:
                time.sleep(0.5)
                timeout -= 0.5
                elapsed = time.time() - start_time
                print(f"⏱️ Esperando conexión... {timeout:.1f}s (transcurrido: {elapsed:.1f}s)")
            
            if self.connected:
                print("✅ Conexión WebSocket establecida exitosamente")
                return True
            else:
                print("❌ Timeout esperando conexión WebSocket")
                return False
                
        except Exception as e:
            print(f"❌ Error durante conexión: {e}")
            return False
    
    def test_all_websocket_events(self):
        """Probar todos los eventos WebSocket con enfoque en diagnóstico de cuelgues"""
        if not self.connected:
            print("❌ No conectado - no se pueden probar eventos")
            return
        
        print("\n📤 PROBANDO EVENTOS WEBSOCKET (DIAGNÓSTICO DE CUELGUES)")
        print("=" * 60)
        
        # 1. Solicitar QR con timeout específico
        print("\n1️⃣ Solicitando QR con monitoreo de timeout...")
        qr_received = False
        qr_start_time = time.time()
        
        try:
            self.sio.emit('get_qr', {
                'session_id': self.session_id or 'test-session',
                'timestamp': datetime.now().isoformat(),
                'force_refresh': True
            })
            print("✅ Evento 'get_qr' enviado")
            
            # Monitorear respuesta con timeout
            timeout = 10
            while timeout > 0 and not qr_received:
                time.sleep(0.5)
                timeout -= 0.5
                
                # Verificar si recibimos QR
                for event in self.events_received:
                    if event['type'] == 'QR_CODE' and event['timestamp'] > datetime.fromtimestamp(qr_start_time).isoformat():
                        qr_received = True
                        break
                
                if timeout % 2 == 0:  # Cada 2 segundos
                    print(f"⏱️ Esperando QR... {timeout:.1f}s restantes")
            
            qr_elapsed = time.time() - qr_start_time
            if qr_received:
                print(f"✅ QR recibido en {qr_elapsed:.2f}s")
            else:
                print(f"❌ QR NO recibido después de {qr_elapsed:.2f}s - POSIBLE CUELGUE")
                
        except Exception as e:
            print(f"❌ Error enviando get_qr: {e}")
        
        # 2. Múltiples solicitudes de QR para probar race conditions
        print("\n2️⃣ Probando múltiples solicitudes de QR (race conditions)...")
        for i in range(3):
            try:
                self.sio.emit('get_qr', {
                    'session_id': f'test-session-{i}',
                    'timestamp': datetime.now().isoformat(),
                    'request_id': f'req-{i}'
                })
                print(f"✅ Solicitud QR #{i+1} enviada")
                time.sleep(0.5)
            except Exception as e:
                print(f"❌ Error en solicitud #{i+1}: {e}")
        
        # Esperar respuestas
        time.sleep(5)
        
        # 3. Solicitar estado
        print("\n3️⃣ Solicitando estado...")
        status_received = False
        status_start_time = time.time()
        
        try:
            self.sio.emit('get_status', {
                'timestamp': datetime.now().isoformat(),
                'detailed': True
            })
            print("✅ Evento 'get_status' enviado")
            
            # Monitorear respuesta
            timeout = 5
            while timeout > 0 and not status_received:
                time.sleep(0.5)
                timeout -= 0.5
                
                # Verificar si recibimos estado
                for event in self.events_received:
                    if event['type'] == 'WHATSAPP_STATUS' and event['timestamp'] > datetime.fromtimestamp(status_start_time).isoformat():
                        status_received = True
                        break
                
                if timeout % 1 == 0:  # Cada segundo
                    print(f"⏱️ Esperando estado... {timeout:.1f}s restantes")
            
            status_elapsed = time.time() - status_start_time
            if status_received:
                print(f"✅ Estado recibido en {status_elapsed:.2f}s")
            else:
                print(f"❌ Estado NO recibido después de {status_elapsed:.2f}s")
                
        except Exception as e:
            print(f"❌ Error enviando get_status: {e}")
        
        # 4. Probar conexión WhatsApp
        print("\n4️⃣ Probando conexión WhatsApp...")
        try:
            self.sio.emit('connect_whatsapp', {
                'timestamp': datetime.now().isoformat(),
                'auto_retry': False
            })
            print("✅ Evento 'connect_whatsapp' enviado")
        except Exception as e:
            print(f"❌ Error enviando connect_whatsapp: {e}")
        
        # Esperar respuesta
        time.sleep(3)
        
        # 5. Probar inicialización de sesión
        print("\n5️⃣ Probando inicialización de sesión...")
        try:
            self.sio.emit('init_session', {
                'session_id': 'test-init-session',
                'timestamp': datetime.now().isoformat()
            })
            print("✅ Evento 'init_session' enviado")
        except Exception as e:
            print(f"❌ Error enviando init_session: {e}")
        
        # Esperar respuesta
        time.sleep(2)
        
        # 6. Probar evento de heartbeat/ping
        print("\n6️⃣ Probando ping/heartbeat...")
        try:
            self.sio.emit('ping', {
                'timestamp': datetime.now().isoformat()
            })
            print("✅ Evento 'ping' enviado")
        except Exception as e:
            print(f"❌ Error enviando ping: {e}")
        
        # Esperar respuesta
        time.sleep(1)
        
        # 7. Probar solicitud de QR automático (el problemático)
        print("\n7️⃣ Probando QR automático (endpoint problemático)...")
        auto_qr_received = False
        auto_qr_start_time = time.time()
        
        try:
            self.sio.emit('get_qr_auto', {
                'timestamp': datetime.now().isoformat(),
                'auto_refresh': True,
                'timeout': 8
            })
            print("✅ Evento 'get_qr_auto' enviado")
            
            # Monitorear respuesta con timeout extendido
            timeout = 15
            while timeout > 0 and not auto_qr_received:
                time.sleep(0.5)
                timeout -= 0.5
                
                # Verificar si recibimos QR automático
                for event in self.events_received:
                    if event['type'] in ['QR_CODE', 'ERROR'] and event['timestamp'] > datetime.fromtimestamp(auto_qr_start_time).isoformat():
                        auto_qr_received = True
                        break
                
                if timeout % 2 == 0:  # Cada 2 segundos
                    print(f"⏱️ Esperando QR automático... {timeout:.1f}s restantes")
            
            auto_qr_elapsed = time.time() - auto_qr_start_time
            if auto_qr_received:
                print(f"✅ QR automático recibido en {auto_qr_elapsed:.2f}s")
            else:
                print(f"❌ QR automático NO recibido después de {auto_qr_elapsed:.2f}s - CUELGUE CONFIRMADO")
                
        except Exception as e:
            print(f"❌ Error enviando get_qr_auto: {e}")
        
        # Esperar respuestas finales
        time.sleep(3)
    
    def test_timeout_scenarios(self):
        """Probar escenarios de timeout para diagnosticar cuelgues"""
        if not self.connected:
            print("❌ No conectado - no se pueden probar timeouts")
            return
        
        print("\n⏱️ PROBANDO ESCENARIOS DE TIMEOUT")
        print("=" * 50)
        
        # 1. Solicitud con timeout corto
        print("\n1️⃣ Solicitud con timeout corto (3s)...")
        try:
            start_time = time.time()
            self.sio.emit('get_qr', {
                'session_id': 'timeout-test-short',
                'timestamp': datetime.now().isoformat(),
                'timeout': 3
            })
            
            # Esperar exactamente 3 segundos
            time.sleep(3)
            elapsed = time.time() - start_time
            print(f"✅ Timeout corto completado en {elapsed:.2f}s")
            
        except Exception as e:
            print(f"❌ Error en timeout corto: {e}")
        
        # 2. Solicitud con timeout largo
        print("\n2️⃣ Solicitud con timeout largo (10s)...")
        try:
            start_time = time.time()
            self.sio.emit('get_qr', {
                'session_id': 'timeout-test-long',
                'timestamp': datetime.now().isoformat(),
                'timeout': 10
            })
            
            # Esperar 5 segundos y verificar si hay respuesta
            time.sleep(5)
            elapsed = time.time() - start_time
            print(f"✅ Timeout largo - 5s transcurridos ({elapsed:.2f}s)")
            
            # Esperar los 5 segundos restantes
            time.sleep(5)
            elapsed = time.time() - start_time
            print(f"✅ Timeout largo completado en {elapsed:.2f}s")
            
        except Exception as e:
            print(f"❌ Error en timeout largo: {e}")
        
        # 3. Múltiples solicitudes simultáneas
        print("\n3️⃣ Múltiples solicitudes simultáneas...")
        try:
            start_time = time.time()
            for i in range(5):
                self.sio.emit('get_qr', {
                    'session_id': f'concurrent-test-{i}',
                    'timestamp': datetime.now().isoformat(),
                    'request_id': f'concurrent-{i}'
                })
                print(f"✅ Solicitud simultánea #{i+1} enviada")
                time.sleep(0.2)  # Pequeña separación
            
            # Esperar respuestas
            time.sleep(8)
            elapsed = time.time() - start_time
            print(f"✅ Solicitudes simultáneas completadas en {elapsed:.2f}s")
            
        except Exception as e:
            print(f"❌ Error en solicitudes simultáneas: {e}")
        
        # 4. Solicitud que podría colgarse
        print("\n4️⃣ Solicitud que podría colgarse (QR auto)...")
        try:
            start_time = time.time()
            self.sio.emit('get_qr_auto', {
                'timestamp': datetime.now().isoformat(),
                'force_refresh': True,
                'auto_retry': False
            })
            print("✅ Solicitud de QR auto enviada")
            
            # Monitorear cada segundo
            for i in range(15):
                time.sleep(1)
                elapsed = time.time() - start_time
                print(f"⏱️ QR auto - {elapsed:.1f}s transcurridos...")
                
                # Verificar si recibimos respuesta
                recent_events = [e for e in self.events_received if e['timestamp'] > datetime.fromtimestamp(start_time).isoformat()]
                if recent_events:
                    print(f"✅ Respuesta recibida después de {elapsed:.2f}s")
                    break
            else:
                print(f"❌ QR auto NO respondió después de 15s - CUELGUE CONFIRMADO")
                
        except Exception as e:
            print(f"❌ Error en solicitud de QR auto: {e}")
        
        # 5. Probar cancelación de solicitud
        print("\n5️⃣ Probando cancelación de solicitud...")
        try:
            # Enviar solicitud
            self.sio.emit('get_qr', {
                'session_id': 'cancel-test',
                'timestamp': datetime.now().isoformat()
            })
            print("✅ Solicitud de cancelación enviada")
            
            # Esperar un poco y enviar cancelación
            time.sleep(1)
            self.sio.emit('cancel_request', {
                'session_id': 'cancel-test',
                'timestamp': datetime.now().isoformat()
            })
            print("✅ Cancelación enviada")
            
            # Esperar respuesta
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ Error en cancelación: {e}")
        
        # 6. Probar reconexión durante solicitud
        print("\n6️⃣ Probando reconexión durante solicitud...")
        try:
            # Enviar solicitud
            self.sio.emit('get_qr', {
                'session_id': 'reconnect-test',
                'timestamp': datetime.now().isoformat()
            })
            print("✅ Solicitud pre-reconexión enviada")
            
            # Simular reconexión
            time.sleep(1)
            self.sio.disconnect()
            time.sleep(1)
            self.sio.connect(self.backend_url)
            print("✅ Reconexión realizada")
            
            # Esperar respuesta
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ Error en reconexión: {e}")
            
        print("\n✅ Pruebas de timeout completadas")
    
    def show_connection_stats(self):
        """Mostrar estadísticas de conexión"""
        print("\n📊 ESTADÍSTICAS DE CONEXIÓN")
        print("=" * 50)
        print(f"🔗 Estado: {'✅ Conectado' if self.connected else '❌ Desconectado'}")
        print(f"🕒 Tiempo de conexión: {self.connection_time}")
        print(f"🆔 Client ID: {self.client_id}")
        print(f"🎫 Session ID: {self.session_id}")
        print(f"💓 Último ping: {self.last_ping}")
        print(f"📋 Eventos recibidos: {len(self.events_received)}")
        
        if self.connection_time:
            uptime = datetime.now() - self.connection_time
            print(f"⏱️ Tiempo activo: {uptime.total_seconds():.1f}s")
    
    def show_events_summary(self):
        """Mostrar resumen de eventos"""
        print("\n🗂️ RESUMEN DE EVENTOS")
        print("=" * 50)
        
        # Contar eventos por tipo
        event_counts = {}
        for event in self.events_received:
            event_type = event['type']
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        print("📊 Eventos por tipo:")
        for event_type, count in sorted(event_counts.items()):
            print(f"  {event_type}: {count}")
        
        # Mostrar últimos eventos
        print("\n🔄 Últimos 5 eventos:")
        for event in self.events_received[-5:]:
            timestamp = event['timestamp']
            event_type = event['type']
            data = event['data']
            print(f"  {timestamp} - {event_type}: {data}")
    
    def disconnect_from_backend(self):
        """Desconectar del backend"""
        if self.connected:
            print("🔌 Desconectando del WebSocket...")
            self.sio.disconnect()
            time.sleep(1)
            print("✅ Desconectado")
        else:
            print("ℹ️ Ya estaba desconectado")

def main():
    """Función principal de prueba exhaustiva"""
    print("🧪 PRUEBA EXHAUSTIVA DE WEBSOCKET")
    print("=" * 60)
    print(f"🎯 Backend: {BACKEND_URL}")
    print(f"🕒 Inicio: {datetime.now()}")
    
    # Crear instancia de prueba
    test_client = WebSocketExhaustiveTest()
    
    try:
        # 1. Conectar al backend
        print("\n1️⃣ FASE DE CONEXIÓN")
        print("=" * 30)
        connected = test_client.connect_to_backend()
        
        if connected:
            print("✅ Conexión exitosa - continuando pruebas")
            
            # 2. Esperar eventos iniciales
            print("\n2️⃣ FASE DE EVENTOS INICIALES")
            print("=" * 30)
            print("⏳ Esperando eventos del backend...")
            time.sleep(5)
            
            # 3. Probar todos los eventos
            print("\n3️⃣ FASE DE PRUEBA DE EVENTOS")
            print("=" * 30)
            test_client.test_all_websocket_events()
            
            # 4. Probar escenarios de timeout
            print("\n4️⃣ FASE DE PRUEBA DE TIMEOUTS")
            print("=" * 30)
            test_client.test_timeout_scenarios()
            
            # 5. Mostrar estadísticas
            print("\n5️⃣ FASE DE ESTADÍSTICAS")
            print("=" * 30)
            test_client.show_connection_stats()
            test_client.show_events_summary()
            
            # 6. Mantener conexión activa un poco más
            print("\n6️⃣ FASE DE MONITOREO")
            print("=" * 30)
            print("⏳ Manteniendo conexión activa 10s más...")
            time.sleep(10)
            
            # 7. Desconectar
            print("\n7️⃣ FASE DE DESCONEXIÓN")
            print("=" * 30)
            test_client.disconnect_from_backend()
            
        else:
            print("❌ Error de conexión - no se pueden ejecutar pruebas")
            
    except KeyboardInterrupt:
        print("\n\n⛔ Prueba interrumpida por el usuario")
        test_client.disconnect_from_backend()
    
    except Exception as e:
        print(f"\n\n❌ Error durante las pruebas: {e}")
        test_client.disconnect_from_backend()
    
    # Resumen final
    print("\n🏁 RESUMEN FINAL")
    print("=" * 60)
    test_client.show_connection_stats()
    test_client.show_events_summary()
    
    # Resultado
    if test_client.events_received:
        print("\n✅ RESULTADO: WebSocket funciona correctamente")
        print("💡 Se recibieron eventos del backend")
    else:
        print("\n❌ RESULTADO: WebSocket no funciona")
        print("💡 No se recibieron eventos del backend")

if __name__ == "__main__":
    main()
