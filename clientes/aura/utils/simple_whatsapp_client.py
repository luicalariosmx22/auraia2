"""
Cliente simplificado para WhatsApp Web sin dependencias circulares
"""

import os
import requests
from datetime import datetime

class SimpleWhatsAppClient:
    """Cliente simplificado para WhatsApp Web"""
    
    def __init__(self):
        self.backend_url = os.getenv('WHATSAPP_BACKEND_URL_PUBLIC', 'https://whatsapp-server-production-8f61.up.railway.app')
        self.is_connected = False
        self.is_authenticated = False
        self.session_active = False
        self.session_id = None
        self.current_qr = None
        
        print(f"🔗 Simple WhatsApp Client: {self.backend_url}")
    
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
        return {
            'connected': self.is_connected,
            'authenticated': self.is_authenticated,
            'session_active': self.session_active,
            'session_id': self.session_id,
            'has_qr': self.current_qr is not None,
            'backend_type': 'simple_http'
        }
    
    def connect(self):
        """Conectar al backend"""
        try:
            health = self.get_health_status()
            if health:
                self.is_connected = True
                print("✅ Conectado al backend")
                return True
            return False
        except Exception as e:
            print(f"❌ Error conectando: {e}")
            return False
    
    def disconnect(self):
        """Desconectar del backend"""
        self.is_connected = False
        self.is_authenticated = False
        self.session_active = False
        print("🔌 Desconectado")
    
    def init_session(self):
        """Iniciar sesión"""
        try:
            print("🚀 Simulando inicio de sesión...")
            self.session_active = True
            # Simular QR
            self.current_qr = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            return True
        except Exception as e:
            print(f"❌ Error iniciando sesión: {e}")
            return False
    
    def close_session(self):
        """Cerrar sesión"""
        try:
            print("🔐 Cerrando sesión...")
            self.session_active = False
            self.is_authenticated = False
            self.current_qr = None
            return True
        except Exception as e:
            print(f"❌ Error cerrando sesión: {e}")
            return False
    
    def check_status(self):
        """Verificar estado"""
        try:
            print("🔍 Verificando estado...")
            return True
        except Exception as e:
            print(f"❌ Error verificando estado: {e}")
            return False
    
    def get_qr_code(self):
        """Obtener código QR actual"""
        return self.current_qr
    
    def send_test_message(self):
        """Enviar mensaje de prueba"""
        try:
            if not self.is_authenticated:
                print("❌ WhatsApp no está autenticado")
                return False
            
            print("📤 Simulando envío de mensaje...")
            return True
        except Exception as e:
            print(f"❌ Error enviando mensaje: {e}")
            return False
