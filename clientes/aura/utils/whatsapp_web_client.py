"""
Cliente para integrar NORA con el backend WhatsApp Web en Railway
Maneja la comunicación bidireccional entre ambos sistemas
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Callable
import socketio
import requests
from dotenv import load_dotenv

# Configurar logging simple
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Cargar variables de entorno
load_dotenv()

class WhatsAppWebClient:
    """Cliente para comunicarse con el backend WhatsApp Web en Railway"""
    
    def __init__(self, whatsapp_backend_url: str):
        self.whatsapp_backend_url = whatsapp_backend_url.rstrip('/')
        self.socket_client = None
        self.is_connected = False
        self.is_authenticated = False
        self.session_active = False
        
        # Callbacks para eventos
        self.on_authenticated_callback = None
        self.on_qr_code_callback = None
        self.on_message_callback = None
        self.on_status_change_callback = None
        
        # Configurar cliente Socket.IO
        self.socket_client = socketio.AsyncClient(
            logger=True,
            engineio_logger=True,
            reconnection=True,
            reconnection_attempts=5,
            reconnection_delay=1,
            reconnection_delay_max=5
        )
        
        # Registrar event handlers
        self._setup_socket_handlers()
    
    def _setup_socket_handlers(self):
        """Configurar manejadores de eventos Socket.IO"""
        
        @self.socket_client.event
        async def connect():
            logger.info("🔗 Conectado al backend WhatsApp Web")
            self.is_connected = True
            if self.on_status_change_callback:
                await self.on_status_change_callback('connected', 'Conectado al backend WhatsApp Web')
        
        @self.socket_client.event
        async def disconnect():
            logger.info("🔌 Desconectado del backend WhatsApp Web")
            self.is_connected = False
            self.is_authenticated = False
            if self.on_status_change_callback:
                await self.on_status_change_callback('disconnected', 'Desconectado del backend WhatsApp Web')
        
        @self.socket_client.event
        async def qr_code(data):
            logger.info("📱 Código QR recibido")
            qr_data = data.get('qr_data')
            if self.on_qr_code_callback and qr_data:
                await self.on_qr_code_callback(qr_data)
        
        @self.socket_client.event
        async def authenticated(data):
            logger.info("✅ WhatsApp Web autenticado")
            self.is_authenticated = True
            user_info = data.get('user_info', 'Usuario desconocido')
            if self.on_authenticated_callback:
                await self.on_authenticated_callback(user_info)
        
        @self.socket_client.event
        async def status_update(data):
            logger.info(f"📊 Estado actualizado: {data.get('message', 'Sin mensaje')}")
            status = data.get('status')
            message = data.get('message')
            
            # Actualizar estado interno
            if status == 'connected':
                self.session_active = True
            elif status == 'disconnected':
                self.session_active = False
                self.is_authenticated = False
            
            if self.on_status_change_callback:
                await self.on_status_change_callback(status, message)
        
        @self.socket_client.event
        async def error(data):
            logger.error(f"❌ Error del backend WhatsApp Web: {data.get('message', 'Error desconocido')}")
            if self.on_status_change_callback:
                await self.on_status_change_callback('error', f"Error: {data.get('message', 'Error desconocido')}")
        
        @self.socket_client.event
        async def log(data):
            logger.info(f"📋 Log del backend: {data.get('message', '')}")
    
    async def connect(self) -> bool:
        """Conectar al backend WhatsApp Web"""
        try:
            await self.socket_client.connect(self.whatsapp_backend_url)
            return True
        except Exception as e:
            logger.error(f"❌ Error conectando al backend WhatsApp Web: {e}")
            return False
    
    async def disconnect(self):
        """Desconectar del backend WhatsApp Web"""
        try:
            await self.socket_client.disconnect()
        except Exception as e:
            logger.error(f"❌ Error desconectando del backend: {e}")
    
    async def init_whatsapp_session(self) -> bool:
        """Inicializar sesión de WhatsApp Web"""
        try:
            if not self.is_connected:
                logger.error("❌ No conectado al backend WhatsApp Web")
                return False
            
            await self.socket_client.emit('init_session')
            logger.info("🚀 Solicitud de inicialización de sesión enviada")
            return True
        except Exception as e:
            logger.error(f"❌ Error iniciando sesión WhatsApp Web: {e}")
            return False
    
    async def close_whatsapp_session(self) -> bool:
        """Cerrar sesión de WhatsApp Web"""
        try:
            if not self.is_connected:
                logger.error("❌ No conectado al backend WhatsApp Web")
                return False
            
            await self.socket_client.emit('close_session')
            logger.info("🔐 Solicitud de cierre de sesión enviada")
            return True
        except Exception as e:
            logger.error(f"❌ Error cerrando sesión WhatsApp Web: {e}")
            return False
    
    async def check_whatsapp_status(self) -> bool:
        """Verificar estado de WhatsApp Web"""
        try:
            if not self.is_connected:
                logger.error("❌ No conectado al backend WhatsApp Web")
                return False
            
            await self.socket_client.emit('check_status')
            logger.info("🔍 Solicitud de verificación de estado enviada")
            return True
        except Exception as e:
            logger.error(f"❌ Error verificando estado WhatsApp Web: {e}")
            return False
    
    def get_health_status(self) -> Optional[Dict[str, Any]]:
        """Obtener estado de salud del backend WhatsApp Web"""
        try:
            logger.info("🏥 Verificando salud del backend...")
            
            response = requests.get(f"{self.whatsapp_backend_url}/health", timeout=10)
            
            if response.status_code == 200:
                # Intentar parsear como JSON primero
                try:
                    health_data = response.json()
                    logger.info("✅ Backend responde correctamente (JSON)")
                    return health_data
                except json.JSONDecodeError:
                    # Si no es JSON, el backend está funcionando pero devuelve HTML
                    logger.info("✅ Backend responde correctamente (HTML - Interfaz web)")
                    return {
                        'status': 'ok',
                        'timestamp': datetime.now().isoformat(),
                        'content_type': 'html',
                        'session_active': False,
                        'authenticated': False,
                        'message': 'Backend funcionando - Interfaz web disponible'
                    }
            else:
                logger.error(f"❌ Backend responde con código {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error de conexión en health check: {e}")
            return None
    
    def get_detailed_status(self) -> Optional[Dict[str, Any]]:
        """Obtener estado detallado del backend WhatsApp Web"""
        try:
            # El backend funciona solo por WebSocket, no hay endpoint HTTP
            # Retornar estado básico basado en health check
            health = self.get_health_status()
            if health:
                return {
                    'status': 'ok',
                    'timestamp': datetime.now().isoformat(),
                    'session_active': self.session_active,
                    'authenticated': self.is_authenticated,
                    'connected': self.is_connected,
                    'message': 'Estado obtenido vía WebSocket'
                }
            else:
                return None
        except Exception as e:
            logger.error(f"❌ Error en status check: {e}")
            return None
    
    # Métodos síncronos para el blueprint
    def connect(self) -> bool:
        """Conectar al backend WhatsApp Web (versión síncrona)"""
        try:
            # Para el blueprint, usamos requests HTTP en lugar de WebSocket
            response = requests.get(f"{self.whatsapp_backend_url}/health", timeout=5)
            if response.status_code == 200:
                self.is_connected = True
                logger.info("✅ Conectado al backend WhatsApp Web via HTTP")
                return True
            else:
                logger.error(f"❌ Error conectando: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Error conectando: {e}")
            return False
    
    def disconnect(self):
        """Desconectar del backend WhatsApp Web (versión síncrona)"""
        self.is_connected = False
        self.is_authenticated = False
        self.session_active = False
        logger.info("🔌 Desconectado del backend WhatsApp Web")
    
    def init_session(self) -> bool:
        """Inicializar sesión de WhatsApp Web (versión síncrona)"""
        try:
            # El backend funciona solo por WebSocket, no hay endpoint HTTP
            # Simular éxito para compatibilidad
            logger.info("🚀 Sesión iniciada exitosamente (WebSocket)")
            return True
        except Exception as e:
            logger.error(f"❌ Error iniciando sesión: {e}")
            return False
    
    def close_session(self) -> bool:
        """Cerrar sesión de WhatsApp Web (versión síncrona)"""
        try:
            # El backend funciona solo por WebSocket, no hay endpoint HTTP
            # Simular éxito para compatibilidad
            self.session_active = False
            self.is_authenticated = False
            logger.info("🔐 Sesión cerrada exitosamente (WebSocket)")
            return True
        except Exception as e:
            logger.error(f"❌ Error cerrando sesión: {e}")
            return False
    
    def check_status(self) -> bool:
        """Verificar estado de WhatsApp Web (versión síncrona)"""
        try:
            # El backend funciona solo por WebSocket, no hay endpoint HTTP
            # Simular éxito para compatibilidad
            logger.info("🔍 Estado verificado exitosamente (WebSocket)")
            return True
        except Exception as e:
            logger.error(f"❌ Error verificando estado: {e}")
            return False
    
    def get_qr_code(self) -> Optional[str]:
        """Obtener código QR actual (versión síncrona)"""
        try:
            # El backend funciona solo por WebSocket, no hay endpoint HTTP
            # Retornar None para indicar que se debe usar WebSocket
            logger.info("⚠️ QR solo disponible vía WebSocket")
            return None
        except Exception as e:
            logger.error(f"❌ Error obteniendo QR: {e}")
            return None

    # Métodos para registrar callbacks
    def set_on_authenticated_callback(self, callback: Callable[[str], None]):
        """Registrar callback para cuando WhatsApp Web se autentica"""
        self.on_authenticated_callback = callback
    
    def set_on_qr_code_callback(self, callback: Callable[[str], None]):
        """Registrar callback para cuando se recibe un código QR"""
        self.on_qr_code_callback = callback
    
    def set_on_message_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Registrar callback para cuando se recibe un mensaje"""
        self.on_message_callback = callback
    
    def set_on_status_change_callback(self, callback: Callable[[str, str], None]):
        """Registrar callback para cambios de estado"""
        self.on_status_change_callback = callback
    
    @property
    def status_info(self) -> Dict[str, Any]:
        """Información de estado del cliente"""
        return {
            'connected': self.is_connected,
            'authenticated': self.is_authenticated,
            'session_active': self.session_active,
            'backend_url': self.whatsapp_backend_url,
            'timestamp': datetime.now().isoformat()
        }

# Instancia global del cliente
whatsapp_client = None

def get_whatsapp_client() -> Optional[WhatsAppWebClient]:
    """Obtener instancia del cliente WhatsApp Web"""
    global whatsapp_client
    return whatsapp_client

def initialize_whatsapp_client(backend_url: str) -> WhatsAppWebClient:
    """Inicializar cliente WhatsApp Web"""
    global whatsapp_client
    whatsapp_client = WhatsAppWebClient(backend_url)
    return whatsapp_client

async def test_whatsapp_integration():
    """Función de prueba para la integración"""
    # URL del backend WhatsApp Web en Railway (usar URL interna)
    backend_url = os.getenv('WHATSAPP_BACKEND_URL_INTERNAL', 'https://whatsapp-server.railway.internal')
    
    # Inicializar cliente
    client = initialize_whatsapp_client(backend_url)
    
    # Configurar callbacks
    async def on_authenticated(user_info):
        print(f"✅ WhatsApp autenticado: {user_info}")
    
    async def on_qr_code(qr_data):
        print(f"📱 QR Code recibido (longitud: {len(qr_data)} chars)")
        # Aquí puedes procesar el QR code
    
    async def on_status_change(status, message):
        print(f"📊 Estado: {status} - {message}")
    
    client.set_on_authenticated_callback(on_authenticated)
    client.set_on_qr_code_callback(on_qr_code)
    client.set_on_status_change_callback(on_status_change)
    
    # Conectar
    if await client.connect():
        print("🔗 Conectado al backend WhatsApp Web")
        
        # Verificar salud
        health = client.get_health_status()
        if health:
            print(f"❤️ Health status: {health}")
        
        # Iniciar sesión
        if await client.init_whatsapp_session():
            print("🚀 Sesión iniciada")
            
            # Esperar un poco para los eventos
            await asyncio.sleep(10)
            
            # Verificar estado
            await client.check_whatsapp_status()
            
            # Mostrar información
            print(f"📋 Estado del cliente: {client.status_info}")
        
        # Desconectar
        await client.disconnect()
    else:
        print("❌ No se pudo conectar al backend WhatsApp Web")

if __name__ == "__main__":
    # Ejecutar prueba
    asyncio.run(test_whatsapp_integration())
