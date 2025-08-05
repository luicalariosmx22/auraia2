"""
Cliente simplificado para integrar NORA con el backend WhatsApp Web en Railway
Solo métodos síncronos para evitar problemas de threading
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class WhatsAppWebClient:
    """Cliente simple para comunicarse con el backend WhatsApp Web en Railway"""
    
    def __init__(self, whatsapp_backend_url: str):
        self.whatsapp_backend_url = whatsapp_backend_url.rstrip('/')
        self.is_connected = False
        self.is_authenticated = False
        self.session_active = False
        
        # Configurar logging simple
        self.logger = logging.getLogger(f"{__name__}.{id(self)}")
        self.logger.setLevel(logging.INFO)
    
    def connect(self) -> bool:
        """Conectar al backend WhatsApp Web"""
        try:
            response = requests.get(f"{self.whatsapp_backend_url}/health", timeout=5)
            if response.status_code == 200:
                self.is_connected = True
                self.logger.info("✅ Conectado al backend WhatsApp Web")
                return True
            else:
                self.logger.error(f"❌ Error conectando: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Error conectando: {e}")
            return False
    
    def disconnect(self):
        """Desconectar del backend WhatsApp Web"""
        self.is_connected = False
        self.is_authenticated = False
        self.session_active = False
        self.logger.info("🔌 Desconectado del backend WhatsApp Web")
    
    def init_session(self) -> bool:
        """Inicializar sesión de WhatsApp Web"""
        try:
            # El backend usa WebSocket, pero desde HTTP podemos verificar estado
            response = requests.get(f"{self.whatsapp_backend_url}/health", timeout=10)
            if response.status_code == 200:
                self.logger.info("🚀 Sesión iniciada (verificar QR en backend)")
                return True
            else:
                self.logger.error(f"❌ Error iniciando sesión: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Error iniciando sesión: {e}")
            return False
    
    def close_session(self) -> bool:
        """Cerrar sesión de WhatsApp Web"""
        try:
            # Simular cierre de sesión
            self.session_active = False
            self.is_authenticated = False
            self.logger.info("🔐 Sesión cerrada")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error cerrando sesión: {e}")
            return False
    
    def check_status(self) -> bool:
        """Verificar estado de WhatsApp Web"""
        try:
            response = requests.get(f"{self.whatsapp_backend_url}/health", timeout=10)
            if response.status_code == 200:
                self.logger.info("🔍 Estado verificado")
                return True
            else:
                self.logger.error(f"❌ Error verificando estado: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Error verificando estado: {e}")
            return False
    
    def get_qr_code(self) -> Optional[str]:
        """Obtener código QR actual"""
        try:
            # El QR se maneja desde la interfaz web del backend
            self.logger.info("📱 QR disponible en la interfaz web del backend")
            return None
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo QR: {e}")
            return None
    
    def get_health_status(self) -> Optional[Dict[str, Any]]:
        """Obtener estado de salud del backend WhatsApp Web"""
        try:
            self.logger.info("🏥 Verificando salud del backend...")
            
            response = requests.get(f"{self.whatsapp_backend_url}/health", timeout=10)
            
            if response.status_code == 200:
                # Intentar parsear como JSON primero
                try:
                    health_data = response.json()
                    self.logger.info("✅ Backend responde correctamente (JSON)")
                    return health_data
                except json.JSONDecodeError:
                    # Si no es JSON, el backend está funcionando pero devuelve HTML
                    self.logger.info("✅ Backend responde correctamente (HTML)")
                    return {
                        'status': 'ok',
                        'timestamp': datetime.now().isoformat(),
                        'content_type': 'html',
                        'session_active': False,
                        'authenticated': False,
                        'message': 'Backend funcionando - Interfaz web disponible'
                    }
            else:
                self.logger.error(f"❌ Backend responde con código {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error en health check: {e}")
            return None
    
    def get_detailed_status(self) -> Optional[Dict[str, Any]]:
        """Obtener estado detallado del backend WhatsApp Web"""
        try:
            # Intentar endpoint /status primero
            response = requests.get(f"{self.whatsapp_backend_url}/status", timeout=10)
            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    pass
            
            # Si no funciona, usar health check
            health = self.get_health_status()
            if health:
                return {
                    'session_active': False,
                    'authenticated': False,
                    'last_activity': datetime.now().isoformat(),
                    'driver_active': health.get('status') == 'ok'
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo estado detallado: {e}")
            return None
    
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
_whatsapp_client = None

def get_whatsapp_client() -> WhatsAppWebClient:
    """Obtener instancia del cliente WhatsApp Web (singleton)"""
    global _whatsapp_client
    if _whatsapp_client is None:
        # URLs configuradas
        internal_url = os.getenv('WHATSAPP_BACKEND_URL_INTERNAL', 'https://whatsapp-server.railway.internal')
        public_url = os.getenv('WHATSAPP_BACKEND_URL_PUBLIC', 'https://whatsapp-server-production-8f61.up.railway.app')
        
        # Detectar si estamos en Railway o en local
        is_railway = os.getenv('RAILWAY_ENVIRONMENT') is not None
        
        # Usar URL interna si estamos en Railway, pública si estamos en local
        backend_url = internal_url if is_railway else public_url
        
        print(f"🔗 Entorno: {'Railway' if is_railway else 'Local'}")
        print(f"🔗 Backend URL: {backend_url}")
        
        _whatsapp_client = WhatsAppWebClient(backend_url)
    
    return _whatsapp_client

def test_whatsapp_integration():
    """Función de prueba para la integración"""
    print("🧪 Probando integración WhatsApp Web...")
    
    # Obtener cliente
    client = get_whatsapp_client()
    
    print(f"🔗 Backend URL: {client.whatsapp_backend_url}")
    
    # Verificar conexión
    if client.connect():
        print("✅ Conectado al backend")
        
        # Verificar salud
        health = client.get_health_status()
        if health:
            print(f"❤️ Health status: {health.get('status', 'unknown')}")
            print(f"📄 Mensaje: {health.get('message', 'Sin mensaje')}")
        
        # Verificar estado detallado
        detailed = client.get_detailed_status()
        if detailed:
            print(f"📊 Estado detallado: {detailed}")
        
        # Mostrar información
        print(f"📋 Estado del cliente: {client.status_info}")
        
        # Desconectar
        client.disconnect()
        print("🔌 Desconectado")
    else:
        print("❌ No se pudo conectar al backend")
    
    print("=========================")

if __name__ == "__main__":
    # Ejecutar prueba
    test_whatsapp_integration()
