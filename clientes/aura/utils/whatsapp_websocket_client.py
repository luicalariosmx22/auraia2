"""
Cliente WebSocket para integrar NORA con el backend WhatsApp Web real de Railway
Usa Socket.IO para comunicación en tiempo real
"""

import os
import json
import requests
from datetime import datetime
import socketio
import threading
import time

class WhatsAppWebSocketClient:
    """Cliente WebSocket para WhatsApp Web en Railway"""
    
    def __init__(self, backend_url=None):
        # Auto-detectar URL según entorno
        if backend_url is None:
            if os.getenv('RAILWAY_ENVIRONMENT'):
                backend_url = 'https://whatsapp-server.railway.internal'
            else:
                backend_url = 'https://whatsapp-server-production-8f61.up.railway.app'
        
        self.backend_url = backend_url.rstrip('/')
        self.is_connected = False
        self.is_authenticated = False
        self.session_active = False
        self.session_id = None
        self.current_qr = None
        
        # Cliente Socket.IO
        self.sio = socketio.Client(
            logger=True,
            engineio_logger=True,
            reconnection=True,
            reconnection_attempts=3,
            reconnection_delay=1
        )
        
        # Configurar event handlers
        self._setup_handlers()
        
        print(f"🔗 WhatsApp WebSocket Client: {self.backend_url}")
    
    def _setup_handlers(self):
        """Configurar manejadores de eventos Socket.IO"""
        
        @self.sio.event
        def connect():
            print("✅ Conectado al backend WebSocket")
            self.is_connected = True
        
        @self.sio.event
        def disconnect():
            print("🔌 Desconectado del backend WebSocket")
            self.is_connected = False
            self.is_authenticated = False
            self.session_active = False
        
        @self.sio.event
        def connected(data):
            print(f"📡 Sesión iniciada: {data}")
            self.session_active = True
            # Actualizar session_id si viene
            if isinstance(data, dict) and 'client_id' in data:
                self.session_id = data['client_id']
                print(f"🆔 Session ID actualizado: {self.session_id}")
        
        @self.sio.event
        def qr_code(data):
            print(f"📱 QR recibido: {data.get('message', 'QR generado')}")
            
            # Capturar QR data del backend
            if 'qr_data' in data:
                self.current_qr = data['qr_data']
                print(f"✅ QR actualizado: {type(self.current_qr)} - {len(self.current_qr) if self.current_qr else 0} chars")
                
                # Si es una imagen PNG, confirmar que es válida
                if isinstance(self.current_qr, str) and self.current_qr.startswith('data:image/png;base64,'):
                    print("📸 QR es imagen PNG válida del backend")
                elif isinstance(self.current_qr, str) and self.current_qr.startswith('1@'):
                    print("📱 QR es texto plano de WhatsApp Web")
                else:
                    print(f"❓ QR en formato inesperado: {self.current_qr[:50] if self.current_qr else 'None'}...")
            
            # Si viene QR como string directo
            if isinstance(data, dict) and 'qr_data' not in data and 'message' in data:
                # Podría ser que el QR venga en message
                qr_text = data.get('message', '')
                if qr_text and ('1@' in qr_text or 'data:image' in qr_text):
                    self.current_qr = qr_text
                    print(f"✅ QR capturado desde message: {len(qr_text)} chars")
            
            # Actualizar session_id si viene en la respuesta
            if isinstance(data, dict) and 'session_id' in data:
                self.session_id = data['session_id']
                print(f"🆔 Session ID actualizado: {self.session_id}")
            
            # Verificar si hay error específico de QR
            if isinstance(data, dict) and 'error' in data:
                print(f"⚠️ Error en QR: {data['error']}")
                # No es un error de conexión, es un error específico de QR
            
            # Verificar mensaje
            if isinstance(data, dict) and 'message' in data:
                print(f"💬 Mensaje del backend: {data['message']}")
        
        @self.sio.event
        def authenticated(data):
            print(f"🎉 Autenticado: {data.get('message', 'Éxito')}")
            self.is_authenticated = True
            self.session_active = True
        
        @self.sio.event
        def error(data):
            error_msg = data.get('message', 'Error desconocido') if isinstance(data, dict) else str(data)
            print(f"❌ Error del backend: {error_msg}")
            
            # Distinguir entre errores de conexión y errores de aplicación
            if 'conexión' in error_msg.lower() or 'connection' in error_msg.lower():
                print("🔌 Error de conexión detectado")
                self.is_connected = False
            elif 'chrome' in error_msg.lower() or 'browser' in error_msg.lower():
                print("🌐 Error de navegador - backend necesita Chrome")
                # No es un error de conexión, el WebSocket funciona
            else:
                print("⚠️ Error de aplicación - conexión WebSocket OK")
        
        @self.sio.event
        def test_result(data):
            print(f"🧪 Resultado de prueba: {data}")
        
        @self.sio.event
        def heartbeat(data):
            print(f"💓 Heartbeat: {data.get('timestamp', 'Sin timestamp')}")
    
    def get_health_status(self):
        """Obtener estado de salud del backend"""
        try:
            print(f"🏥 Health check: {self.backend_url}/health")
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("✅ Backend OK (JSON)")
                    return data
                except:
                    print("✅ Backend OK (HTML)")
                    return {
                        'status': 'ok',
                        'timestamp': datetime.now().isoformat(),
                        'message': 'Backend funcionando'
                    }
            return None
        except Exception as e:
            print(f"❌ Error health check: {e}")
            return None
    
    def get_detailed_status(self):
        """Obtener estado detallado"""
        # El backend real no tiene endpoint /status HTTP
        # Devolver estado basado en WebSocket
        return {
            'connected': self.is_connected,
            'authenticated': self.is_authenticated,
            'session_active': self.session_active,
            'session_id': self.session_id,
            'has_qr': self.current_qr is not None,
            'backend_type': 'websocket'
        }
    
    def connect(self):
        """Conectar al backend WebSocket de forma completamente no bloqueante"""
        try:
            if self.is_connected:
                print("✅ Ya conectado")
                return True
            
            print(f"🔗 Conectando a WebSocket: {self.backend_url}")
            
            # Conexión asíncrona sin bloqueo
            try:
                # Usar threading para no bloquear el hilo principal
                def _connect_async():
                    try:
                        self.sio.connect(self.backend_url, transports=['websocket', 'polling'])
                    except Exception as e:
                        print(f"❌ Error async conectando: {e}")
                
                # Iniciar conexión en hilo separado
                connection_thread = threading.Thread(target=_connect_async, daemon=True)
                connection_thread.start()
                
                # Esperar muy poco tiempo para no bloquear
                timeout = 0.5  # Solo 0.5 segundos
                start_time = time.time()
                
                while timeout > 0 and not self.is_connected:
                    time.sleep(0.1)  # Verificar cada 100ms
                    timeout -= 0.1
                    
                    if time.time() - start_time > timeout:
                        break
                
                if self.is_connected:
                    print("✅ Conexión WebSocket establecida exitosamente")
                    return True
                else:
                    print("⚠️ Conexión WebSocket en progreso (no bloquear)")
                    return False  # No es un error, solo está en progreso
                    
            except Exception as e:
                print(f"❌ Error conectando WebSocket: {e}")
                return False
            
        except Exception as e:
            print(f"❌ Error general en conexión: {e}")
            return False
    
    def disconnect(self):
        """Desconectar del backend"""
        try:
            if self.is_connected:
                self.sio.disconnect()
            print("🔌 Desconectado")
        except Exception as e:
            print(f"❌ Error desconectando: {e}")
    
    def init_session(self):
        """Iniciar sesión WhatsApp Web (obtener QR) - rápido"""
        try:
            if not self.is_connected:
                print("❌ No conectado al WebSocket")
                return False
            
            print("🚀 Solicitando QR de WhatsApp Web...")
            self.sio.emit('get_qr', {
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat()
            })
            
            # Esperar menos tiempo para la respuesta
            time.sleep(1)  # Reducido de 3s a 1s
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando sesión: {e}")
            return False
    
    def close_session(self):
        """Cerrar sesión WhatsApp Web"""
        try:
            if not self.is_connected:
                return True
            
            print("🔐 Cerrando sesión WhatsApp Web...")
            self.sio.emit('disconnect_whatsapp', {
                'session_id': self.session_id
            })
            
            self.session_active = False
            self.is_authenticated = False
            self.current_qr = None
            self.session_id = None
            
            return True
            
        except Exception as e:
            print(f"❌ Error cerrando sesión: {e}")
            return False
    
    def check_status(self):
        """Verificar estado de WhatsApp Web"""
        try:
            if not self.is_connected:
                return False
            
            print("🔍 Verificando estado...")
            # No hay evento específico para esto en el backend
            # Usar estado interno
            return True
            
        except Exception as e:
            print(f"❌ Error verificando estado: {e}")
            return False
    
    def get_qr_code(self, force_refresh=False):
        """Obtener código QR actual - rápido"""
        # Si se solicita refresh o no hay QR, solicitarlo al backend
        if force_refresh or not self.current_qr:
            if self.is_connected:
                print("📱 Solicitando QR fresco al backend...")
                self.sio.emit('get_qr', {
                    'session_id': self.session_id,
                    'timestamp': datetime.now().isoformat(),
                    'force_refresh': force_refresh
                })
                
                # Esperar menos tiempo para la respuesta
                time.sleep(1)  # Reducido de 3s a 1s
        
        return self.current_qr
    
    def send_test_message(self):
        """Enviar mensaje de prueba"""
        try:
            if not self.is_authenticated:
                print("❌ WhatsApp no está autenticado")
                return False
            
            print("📤 Enviando mensaje de prueba...")
            self.sio.emit('test_whatsapp', {
                'session_id': self.session_id,
                'action': 'send_test_message',
                'phone_number': '123456789',
                'message': 'Mensaje de prueba desde NORA'
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Error enviando mensaje: {e}")
            return False

# Cliente global
_global_client = None

def get_whatsapp_client():
    """Obtener cliente global"""
    global _global_client
    if _global_client is None:
        _global_client = WhatsAppWebSocketClient()
    return _global_client

def test_websocket_client():
    """Probar cliente WebSocket"""
    print("🧪 Test WebSocket WhatsApp Client")
    client = get_whatsapp_client()
    
    # Health check primero
    health = client.get_health_status()
    if not health:
        print("❌ Backend no responde")
        return
    
    print(f"❤️ Backend health: {health.get('status', 'unknown')}")
    
    # Conectar WebSocket
    if client.connect():
        print("✅ WebSocket conectado")
        
        # Solicitar QR
        if client.init_session():
            print("🚀 Sesión iniciada")
            
            # Esperar QR
            time.sleep(5)
            
            qr = client.get_qr_code()
            if qr:
                print(f"📱 QR obtenido: {qr[:50]}...")
            else:
                print("⏳ QR aún no disponible")
            
            # Status
            status = client.get_detailed_status()
            print(f"📊 Estado: {status}")
        
        # Desconectar
        client.disconnect()
    else:
        print("❌ No se pudo conectar WebSocket")

if __name__ == "__main__":
    test_websocket_client()
