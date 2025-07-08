"""
Blueprint WhatsApp Web - Versión limpia sin recursión
"""

import os
from flask import Blueprint, render_template, request, jsonify
from clientes.aura.utils.whatsapp_websocket_client import get_whatsapp_client

# Crear blueprint
panel_cliente_whatsapp_web_bp = Blueprint(
    'panel_cliente_whatsapp_web',
    __name__,
    template_folder='../../templates',
    static_folder='../../static'
)

# URLs de Railway
BACKEND_URL_PUBLIC = 'https://whatsapp-server-production-8f61.up.railway.app'

@panel_cliente_whatsapp_web_bp.route('/panel_cliente/<nombre_nora>/whatsapp')
def whatsapp_dashboard(nombre_nora):
    """Dashboard principal de WhatsApp Web"""
    try:
        print(f"🚀 Cargando dashboard WhatsApp para {nombre_nora}")
        
        # Crear cliente simple
        client = WhatsAppWebClient()
        
        # Obtener estado básico
        health_status = client.get_health_status()
        
        print(f"💚 Health status: {health_status}")
        
        return render_template(
            'panel_cliente_whatsapp_web.html',
            nombre_nora=nombre_nora,
            backend_url=BACKEND_URL_PUBLIC,
            health_status=health_status,
            detailed_status=None,
            client_status={'connected': False, 'authenticated': False, 'session_active': False}
        )
        
    except Exception as e:
        print(f"❌ Error en dashboard: {e}")
        return f"Error cargando WhatsApp Web: {str(e)}", 500

@panel_cliente_whatsapp_web_bp.route('/panel_cliente/<nombre_nora>/whatsapp/status')
def get_status(nombre_nora):
    """Obtener estado del sistema"""
    try:
        print(f"📊 Obteniendo status para {nombre_nora}")
        
        client = WhatsAppWebClient()
        health_status = client.get_health_status()
        
        return jsonify({
            'success': True,
            'health_status': health_status,
            'backend_url': BACKEND_URL_PUBLIC,
            'message': 'Status obtenido correctamente'
        })
        
    except Exception as e:
        print(f"❌ Error obteniendo status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@panel_cliente_whatsapp_web_bp.route('/panel_cliente/<nombre_nora>/whatsapp/connect', methods=['POST'])
def connect_backend(nombre_nora):
    """Conectar con backend"""
    try:
        print(f"🔗 Conectando backend para {nombre_nora}")
        
        client = WhatsAppWebClient()
        success = client.connect()
        
        return jsonify({
            'success': success,
            'message': 'Conectado exitosamente' if success else 'Error conectando'
        })
        
    except Exception as e:
        print(f"❌ Error conectando: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@panel_cliente_whatsapp_web_bp.route('/panel_cliente/<nombre_nora>/whatsapp/init_session', methods=['POST'])
def init_session(nombre_nora):
    """Iniciar sesión WhatsApp"""
    try:
        print(f"🚀 Iniciando sesión para {nombre_nora}")
        
        client = WhatsAppWebClient()
        success = client.init_session()
        
        return jsonify({
            'success': success,
            'message': 'Sesión iniciada - Revisa el QR en el backend'
        })
        
    except Exception as e:
        print(f"❌ Error iniciando sesión: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@panel_cliente_whatsapp_web_bp.route('/panel_cliente/<nombre_nora>/whatsapp/test')
def test_endpoint(nombre_nora):
    """Endpoint de prueba"""
    return jsonify({
        'success': True,
        'message': f'WhatsApp Web funcionando para {nombre_nora}',
        'backend_url': BACKEND_URL_PUBLIC
    })
