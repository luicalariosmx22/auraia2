"""
Blueprint para la integración de WhatsApp Web con Railway
Conecta NORA con el backend WhatsApp Web desplegado en Railway
VERSIÓN CORREGIDA - Sin recursión
"""

import os
import json
import logging
from flask import Blueprint, render_template, request, jsonify
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint
panel_cliente_whatsapp_web_bp = Blueprint(
    'panel_cliente_whatsapp_web',
    __name__,
    template_folder='../../templates',
    static_folder='../../static'
)

# Configuración URLs Railway
WHATSAPP_BACKEND_URL_INTERNAL = os.getenv('WHATSAPP_BACKEND_URL_INTERNAL', 'https://whatsapp-server.railway.internal')
WHATSAPP_BACKEND_URL_PUBLIC = os.getenv('WHATSAPP_BACKEND_URL_PUBLIC', 'https://whatsapp-server-production-8f61.up.railway.app')

# Cliente global para WhatsApp Web
_whatsapp_client_singleton = None

def create_whatsapp_client():
    """Crear cliente WhatsApp Web WebSocket"""
    try:
        from clientes.aura.utils.whatsapp_websocket_client import WhatsAppWebSocketClient
        client = WhatsAppWebSocketClient()
        print("✅ Cliente WhatsApp Web WebSocket creado exitosamente")
        return client
    except Exception as e:
        print(f"❌ Error creando cliente WhatsApp Web: {e}")
        raise

def get_whatsapp_singleton():
    """Obtener cliente WhatsApp Web (singleton sin recursión)"""
    global _whatsapp_client_singleton
    if _whatsapp_client_singleton is None:
        _whatsapp_client_singleton = create_whatsapp_client()
    return _whatsapp_client_singleton

@panel_cliente_whatsapp_web_bp.route('/panel_cliente/<nombre_nora>/whatsapp')
def whatsapp_dashboard(nombre_nora):
    """Página principal del dashboard WhatsApp Web"""
    print(f"🌐 Accediendo a dashboard WhatsApp Web para: {nombre_nora}")
    try:
        print("🔄 Obteniendo cliente WhatsApp...")
        client = get_whatsapp_singleton()
        print(f"✅ Cliente obtenido: {type(client)}")
        
        print("🏥 Obteniendo health status...")
        health_status = client.get_health_status()
        print(f"❤️ Health status: {health_status}")
        
        print("📊 Obteniendo detailed status...")
        detailed_status = client.get_detailed_status()
        print(f"📋 Detailed status: {detailed_status}")
        
        client_status = {
            'connected': client.is_connected,
            'authenticated': client.is_authenticated,
            'session_active': client.session_active
        }
        print(f"🔗 Client status: {client_status}")
        
        print("🎨 Renderizando template...")
        return render_template(
            'panel_cliente_whatsapp_web.html',
            nombre_nora=nombre_nora,
            backend_url=WHATSAPP_BACKEND_URL_PUBLIC,
            health_status=health_status,
            detailed_status=detailed_status,
            client_status=client_status
        )
        
    except Exception as e:
        logger.error(f"Error cargando dashboard WhatsApp Web: {e}")
        return render_template(
            'panel_cliente_whatsapp_web.html',
            nombre_nora=nombre_nora,
            backend_url=WHATSAPP_BACKEND_URL_PUBLIC,
            health_status=None,
            detailed_status=None,
            client_status={'connected': False, 'authenticated': False, 'session_active': False},
            error=str(e)
        )

@panel_cliente_whatsapp_web_bp.route('/panel_cliente/<nombre_nora>/whatsapp/status')
def get_status(nombre_nora):
    """Obtener estado actual del sistema WhatsApp Web"""
    try:
        client = get_whatsapp_singleton()
        
        # Obtener todos los estados
        health_status = client.get_health_status()
        detailed_status = client.get_detailed_status()
        client_status = {
            'connected': client.is_connected,
            'authenticated': client.is_authenticated,
            'session_active': client.session_active,
            'session_id': getattr(client, 'session_id', None),
            'has_qr': getattr(client, 'current_qr', None) is not None
        }
        
        return jsonify({
            'success': True,
            'health_status': health_status,
            'detailed_status': detailed_status,
            'client_status': client_status
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@panel_cliente_whatsapp_web_bp.route('/panel_cliente/<nombre_nora>/whatsapp/connect', methods=['POST'])
def connect_backend(nombre_nora):
    """Conectar al backend WhatsApp Web"""
    try:
        client = get_whatsapp_singleton()
        success = client.connect()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Conectado al backend WhatsApp Web exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error conectando al backend WhatsApp Web'
            }), 500
            
    except Exception as e:
        logger.error(f"Error conectando: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@panel_cliente_whatsapp_web_bp.route('/panel_cliente/<nombre_nora>/whatsapp/disconnect', methods=['POST'])
def disconnect_backend(nombre_nora):
    """Desconectar del backend WhatsApp Web"""
    try:
        client = get_whatsapp_singleton()
        client.disconnect()
        
        return jsonify({
            'success': True,
            'message': 'Desconectado del backend WhatsApp Web'
        })
        
    except Exception as e:
        logger.error(f"Error desconectando: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@panel_cliente_whatsapp_web_bp.route('/panel_cliente/<nombre_nora>/whatsapp/init_session', methods=['POST'])
def init_whatsapp_session(nombre_nora):
    """Iniciar sesión de WhatsApp Web"""
    try:
        client = get_whatsapp_singleton()
        
        # Primero conectar si no está conectado
        if not client.is_connected:
            client.connect()
        
        # Iniciar sesión
        success = client.init_session()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Sesión WhatsApp Web iniciada - Revisa el QR en el backend'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error iniciando sesión de WhatsApp Web'
            }), 500
            
    except Exception as e:
        logger.error(f"Error iniciando sesión: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@panel_cliente_whatsapp_web_bp.route('/panel_cliente/<nombre_nora>/whatsapp/get_qr_auto', methods=['POST'])
def get_qr_auto(nombre_nora):
    """Obtener QR automáticamente (conecta e inicia sesión si es necesario)"""
    try:
        client = get_whatsapp_singleton()
        
        # Conectar si no está conectado
        if not client.is_connected:
            print("🔗 Conectando WebSocket...")
            success = client.connect()
            if not success:
                return jsonify({
                    'success': False,
                    'message': 'No se pudo conectar al backend WebSocket'
                }), 500
        
        # Iniciar sesión si no está activa
        if not client.session_active:
            print("🚀 Iniciando sesión...")
            success = client.init_session()
            if not success:
                return jsonify({
                    'success': False,
                    'message': 'No se pudo iniciar sesión'
                }), 500
        
        # Obtener QR
        qr_data = client.get_qr_code()
        
        return jsonify({
            'success': True,
            'has_qr': qr_data is not None,
            'qr_data': qr_data,
            'session_id': getattr(client, 'session_id', None),
            'authenticated': client.is_authenticated,
            'message': 'QR obtenido exitosamente' if qr_data else 'QR no disponible aún'
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo QR automático: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@panel_cliente_whatsapp_web_bp.route('/panel_cliente/<nombre_nora>/whatsapp/close_session', methods=['POST'])
def close_whatsapp_session(nombre_nora):
    """Cerrar sesión de WhatsApp Web"""
    try:
        client = get_whatsapp_singleton()
        success = client.close_session()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Sesión WhatsApp Web cerrada exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error cerrando sesión de WhatsApp Web'
            }), 500
            
    except Exception as e:
        logger.error(f"Error cerrando sesión: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@panel_cliente_whatsapp_web_bp.route('/panel_cliente/<nombre_nora>/whatsapp/check_status', methods=['POST'])
def check_whatsapp_status(nombre_nora):
    """Verificar estado de la sesión WhatsApp Web"""
    try:
        client = get_whatsapp_singleton()
        
        # Primero conectar si no está conectado
        if not client.is_connected:
            client.connect()
        
        # Verificar estado
        success = client.check_status()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Estado verificado exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error verificando estado de WhatsApp Web'
            }), 500
            
    except Exception as e:
        logger.error(f"Error verificando estado: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@panel_cliente_whatsapp_web_bp.route('/panel_cliente/<nombre_nora>/whatsapp/qr')
def get_qr_code(nombre_nora):
    """Obtener código QR actual"""
    try:
        client = get_whatsapp_singleton()
        
        # Obtener QR del backend
        qr_data = client.get_qr_code()
        
        if qr_data:
            return jsonify({
                'success': True,
                'qr_data': qr_data,
                'message': 'Código QR obtenido exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No hay código QR disponible'
            }), 404
            
    except Exception as e:
        logger.error(f"Error obteniendo QR: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@panel_cliente_whatsapp_web_bp.route('/panel_cliente/<nombre_nora>/whatsapp/send_test', methods=['POST'])
def send_test_message(nombre_nora):
    """Enviar mensaje de prueba"""
    try:
        client = get_whatsapp_singleton()
        
        if not client.is_authenticated:
            return jsonify({
                'success': False,
                'message': 'WhatsApp no está autenticado'
            }), 400
        
        # Enviar mensaje de prueba
        success = client.send_test_message()
        
        return jsonify({
            'success': success,
            'message': 'Mensaje de prueba enviado' if success else 'Error enviando mensaje'
        })
        
    except Exception as e:
        logger.error(f"Error enviando mensaje de prueba: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@panel_cliente_whatsapp_web_bp.route('/panel_cliente/<nombre_nora>/whatsapp/events')
def whatsapp_events(nombre_nora):
    """Endpoint para eventos de WhatsApp Web (futuro)"""
    return jsonify({
        'success': True,
        'message': 'Eventos WhatsApp Web - En desarrollo',
        'events': []
    })

@panel_cliente_whatsapp_web_bp.route('/panel_cliente/<nombre_nora>/whatsapp/health')
def module_health(nombre_nora):
    """Health check del módulo WhatsApp Web"""
    try:
        client = get_whatsapp_singleton()
        health_status = client.get_health_status()
        
        return jsonify({
            'success': True,
            'module': 'whatsapp_web',
            'nora': nombre_nora,
            'backend_status': health_status,
            'internal_url': WHATSAPP_BACKEND_URL_INTERNAL,
            'public_url': WHATSAPP_BACKEND_URL_PUBLIC,
            'client_connected': client.is_connected if client else False
        })
        
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return jsonify({
            'success': False,
            'module': 'whatsapp_web',
            'nora': nombre_nora,
            'error': str(e)
        }), 500
