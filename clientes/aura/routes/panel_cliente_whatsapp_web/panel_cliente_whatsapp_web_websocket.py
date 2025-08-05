"""
Blueprint para la integración de WhatsApp Web con Railway - VERSIÓN WEBSOCKET
Usa WebSocket para toda la comunicación con el backend
"""

import os
import json
import logging
import asyncio
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
WHATSAPP_BACKEND_URL_PUBLIC = os.getenv('WHATSAPP_BACKEND_URL_PUBLIC', 'https://whatsapp-server-production-8f61.up.railway.app')

# Cliente global para WhatsApp Web
_whatsapp_client_singleton = None

def get_whatsapp_websocket_client():
    """Obtener cliente WebSocket para WhatsApp Web"""
    global _whatsapp_client_singleton
    if _whatsapp_client_singleton is None:
        try:
            from clientes.aura.utils.whatsapp_websocket_client import WhatsAppWebSocketClient
            _whatsapp_client_singleton = WhatsAppWebSocketClient()
            print("✅ Cliente WebSocket WhatsApp Web creado exitosamente")
        except Exception as e:
            print(f"❌ Error creando cliente WebSocket: {e}")
            raise
    return _whatsapp_client_singleton

@panel_cliente_whatsapp_web_bp.route('/panel_cliente/<nombre_nora>/whatsapp')
def panel_whatsapp_web(nombre_nora):
    """Panel principal de WhatsApp Web"""
    try:
        client = get_whatsapp_websocket_client()
        
        # Obtener estado básico
        health_status = client.get_health_status()
        
        # Estado detallado (basado en cliente WebSocket)
        detailed_status = {
            'status': 'ok' if health_status else 'error',
            'session_active': client.session_active,
            'authenticated': client.is_authenticated,
            'connected': client.is_connected,
            'timestamp': health_status.get('timestamp', '') if health_status else '',
            'message': 'Estado obtenido vía WebSocket'
        }
        
        return render_template('panel_cliente_whatsapp_web.html',
                             nombre_nora=nombre_nora,
                             backend_url=WHATSAPP_BACKEND_URL_PUBLIC,
                             health_status=health_status,
                             detailed_status=detailed_status)
                             
    except Exception as e:
        logger.error(f"Error en panel WhatsApp Web: {e}")
        return f"Error: {str(e)}", 500

@panel_cliente_whatsapp_web_bp.route('/panel_cliente/<nombre_nora>/whatsapp/status')
def get_status(nombre_nora):
    """Obtener estado actual del sistema WhatsApp Web"""
    try:
        client = get_whatsapp_websocket_client()
        
        # Obtener todos los estados
        health_status = client.get_health_status()
        detailed_status = {
            'status': 'ok' if health_status else 'error',
            'session_active': client.session_active,
            'authenticated': client.is_authenticated,
            'connected': client.is_connected,
            'timestamp': health_status.get('timestamp', '') if health_status else '',
            'message': 'Estado obtenido vía WebSocket'
        }
        
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
    """Conectar al backend WhatsApp Web vía WebSocket"""
    try:
        client = get_whatsapp_websocket_client()
        
        # Conectar WebSocket
        success = client.connect()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Conectado al backend WhatsApp Web vía WebSocket'
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
        client = get_whatsapp_websocket_client()
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
    """Iniciar sesión de WhatsApp Web vía WebSocket"""
    try:
        client = get_whatsapp_websocket_client()
        
        # Conectar si no está conectado
        if not client.is_connected:
            client.connect()
        
        # Iniciar sesión
        success = client.init_session()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Sesión WhatsApp Web iniciada exitosamente'
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
    """Obtener QR automáticamente vía WebSocket"""
    try:
        client = get_whatsapp_websocket_client()
        
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
        
        # Esperar un poco para que se genere el QR
        import time
        time.sleep(3)
        
        # Obtener QR del cliente WebSocket
        qr_data = client.get_qr_code()
        
        return jsonify({
            'success': True,
            'has_qr': qr_data is not None,
            'qr_data': qr_data,
            'session_id': getattr(client, 'session_id', None),
            'authenticated': client.is_authenticated,
            'message': 'QR obtenido exitosamente vía WebSocket' if qr_data else 'QR no disponible aún'
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
        client = get_whatsapp_websocket_client()
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
        client = get_whatsapp_websocket_client()
        
        # Conectar si no está conectado
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
    """Obtener código QR actual vía WebSocket"""
    try:
        client = get_whatsapp_websocket_client()
        
        # Obtener QR del cliente WebSocket
        qr_data = client.get_qr_code()
        
        if qr_data:
            return jsonify({
                'success': True,
                'qr_data': qr_data,
                'message': 'Código QR obtenido exitosamente vía WebSocket'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No hay código QR disponible - use WebSocket'
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
        client = get_whatsapp_websocket_client()
        
        if not client.is_authenticated:
            return jsonify({
                'success': False,
                'message': 'WhatsApp no está autenticado'
            }), 400
        
        # Enviar mensaje de prueba
        success = client.send_test_message()
        
        return jsonify({
            'success': success,
            'message': 'Mensaje de prueba enviado exitosamente' if success else 'Error enviando mensaje de prueba'
        })
        
    except Exception as e:
        logger.error(f"Error enviando mensaje de prueba: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Registro del blueprint
def register_blueprint(app):
    """Registrar el blueprint en la aplicación Flask"""
    app.register_blueprint(panel_cliente_whatsapp_web_bp)
    print(f"✅ Blueprint WhatsApp Web registrado: {panel_cliente_whatsapp_web_bp.name}")

if __name__ == "__main__":
    print("🧪 Prueba del blueprint WhatsApp Web WebSocket")
    
    # Probar cliente WebSocket
    try:
        client = get_whatsapp_websocket_client()
        print(f"✅ Cliente creado: {client}")
        
        # Probar conexión
        if client.connect():
            print("✅ Conexión exitosa")
            
            # Iniciar sesión
            if client.init_session():
                print("✅ Sesión iniciada")
                
                # Esperar QR
                import time
                time.sleep(5)
                
                qr = client.get_qr_code()
                if qr:
                    print(f"✅ QR obtenido: {len(qr)} caracteres")
                else:
                    print("❌ No se obtuvo QR")
                    
            client.disconnect()
        else:
            print("❌ Error de conexión")
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
