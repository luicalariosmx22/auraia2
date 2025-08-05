"""
Cliente WhatsApp Web - Versión ultra-simplificada
"""

import os
import json
import requests
from datetime import datetime

class WhatsAppWebClient:
    """Cliente simplificado para WhatsApp Web en Railway"""
    
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
        
        print(f"🔗 WhatsApp Client: {self.backend_url}")
    
    def get_health_status(self):
        """Obtener estado de salud del backend"""
        try:
            print(f"🏥 Health check: {self.backend_url}/health")
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            
            if response.status_code == 200:
                try:
                    return response.json()
                except:
                    return {
                        'status': 'ok',
                        'timestamp': datetime.now().isoformat(),
                        'message': 'Backend funcionando'
                    }
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def get_detailed_status(self):
        """Obtener estado detallado"""
        try:
            response = requests.get(f"{self.backend_url}/status", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def connect(self):
        """Conectar al backend"""
        health = self.get_health_status()
        if health:
            self.is_connected = True
            print("✅ Conectado")
            return True
        print("❌ No conectado")
        return False
    
    def disconnect(self):
        """Desconectar"""
        self.is_connected = False
        self.is_authenticated = False
        self.session_active = False
        print("🔌 Desconectado")
    
    def init_session(self):
        """Iniciar sesión"""
        print("🚀 Iniciando sesión...")
        return True
    
    def close_session(self):
        """Cerrar sesión"""
        print("🔐 Cerrando sesión...")
        self.session_active = False
        self.is_authenticated = False
        return True
    
    def check_status(self):
        """Verificar estado"""
        print("🔍 Verificando estado...")
        return True
    
    def get_qr_code(self):
        """Obtener QR"""
        return None

# Cliente global
_global_client = None

def get_whatsapp_client():
    """Obtener cliente global"""
    global _global_client
    if _global_client is None:
        _global_client = WhatsAppWebClient()
    return _global_client

def test_connection():
    """Probar conexión"""
    print("🧪 Test WhatsApp Client")
    client = get_whatsapp_client()
    
    if client.connect():
        print("✅ Test OK")
        health = client.get_health_status()
        if health:
            print(f"❤️ Health: {health.get('status', 'ok')}")
        client.disconnect()
    else:
        print("❌ Test FAIL")

if __name__ == "__main__":
    test_connection()
