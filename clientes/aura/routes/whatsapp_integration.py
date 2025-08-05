"""
Blueprint para integrar WhatsApp Web con NORA
Conecta con el backend WhatsApp Web en Railway
"""

import os
import json
import asyncio
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session
from flask_socketio import emit, join_room, leave_room
from dotenv import load_dotenv

from clientes.aura.utils.whatsapp_web_client import get_whatsapp_client, initialize_whatsapp_client

# Cargar variables de entorno
load_dotenv()

# Crear blueprint
whatsapp_integration_bp = Blueprint(
    'whatsapp_integration',
    __name__,
    template_folder='../../templates'
)

# URL del backend WhatsApp Web en Railway
WHATSAPP_BACKEND_URL = os.getenv('WHATSAPP_BACKEND_URL', 'https://whatsapp-server-production-7e82.up.railway.app')

# Estado global de la integración
integration_status = {
    'connected': False,
    'authenticated': False,
    'session_active': False,
    'last_update': None,
    'qr_code': None,
    'user_info': None
}

@whatsapp_integration_bp.route('/panel_cliente/<nombre_nora>/whatsapp')
def panel_whatsapp(nombre_nora):
    """Panel de control de WhatsApp Web"""
    return render_template('whatsapp_integration.html', 
                         nombre_nora=nombre_nora,
                         backend_url=WHATSAPP_BACKEND_URL)

@whatsapp_integration_bp.route('/api/whatsapp/status')
def get_whatsapp_status():
    """Obtener estado actual de WhatsApp Web"""
    client = get_whatsapp_client()
    if client:
        # Obtener estado del backend
        backend_status = client.get_detailed_status()
        if backend_status:
            integration_status.update(backend_status)
        
        return jsonify({
            'success': True,
            'status': integration_status,
            'client_info': client.status_info
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Cliente WhatsApp Web no inicializado'
        })

@whatsapp_integration_bp.route('/api/whatsapp/init', methods=['POST'])
def init_whatsapp():
    """Inicializar conexión con WhatsApp Web"""
    try:
        # Inicializar cliente si no existe
        client = get_whatsapp_client()
        if not client:
            client = initialize_whatsapp_client(WHATSAPP_BACKEND_URL)
        
        # Configurar callbacks
        setup_whatsapp_callbacks(client)
        
        return jsonify({
            'success': True,
            'message': 'Inicialización solicitada',
            'backend_url': WHATSAPP_BACKEND_URL
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error iniciando WhatsApp Web: {str(e)}'
        })

@whatsapp_integration_bp.route('/api/whatsapp/connect', methods=['POST'])
def connect_whatsapp():
    """Conectar al backend WhatsApp Web"""
    try:
        client = get_whatsapp_client()
        if not client:
            return jsonify({
                'success': False,
                'message': 'Cliente no inicializado'
            })
        
        # Conectar en background
        import threading
        
        def connect_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(client.connect())
        
        thread = threading.Thread(target=connect_async)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Conexión iniciada'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error conectando: {str(e)}'
        })

@whatsapp_integration_bp.route('/api/whatsapp/start_session', methods=['POST'])
def start_whatsapp_session():
    """Iniciar sesión de WhatsApp Web"""
    try:
        client = get_whatsapp_client()
        if not client:
            return jsonify({
                'success': False,
                'message': 'Cliente no inicializado'
            })
        
        # Iniciar sesión en background
        import threading
        
        def start_session_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(client.init_whatsapp_session())
        
        thread = threading.Thread(target=start_session_async)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Sesión iniciada'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error iniciando sesión: {str(e)}'
        })

@whatsapp_integration_bp.route('/api/whatsapp/close_session', methods=['POST'])
def close_whatsapp_session():
    """Cerrar sesión de WhatsApp Web"""
    try:
        client = get_whatsapp_client()
        if not client:
            return jsonify({
                'success': False,
                'message': 'Cliente no inicializado'
            })
        
        # Cerrar sesión en background
        import threading
        
        def close_session_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(client.close_whatsapp_session())
        
        thread = threading.Thread(target=close_session_async)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Sesión cerrada'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error cerrando sesión: {str(e)}'
        })

@whatsapp_integration_bp.route('/api/whatsapp/health')
def whatsapp_health():
    """Health check del backend WhatsApp Web"""
    try:
        client = get_whatsapp_client()
        if not client:
            return jsonify({
                'success': False,
                'message': 'Cliente no inicializado'
            })
        
        health = client.get_health_status()
        if health:
            return jsonify({
                'success': True,
                'health': health
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Backend no disponible'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error en health check: {str(e)}'
        })

def setup_whatsapp_callbacks(client):
    """Configurar callbacks para eventos de WhatsApp Web"""
    
    async def on_authenticated(user_info):
        """Callback cuando WhatsApp Web se autentica"""
        integration_status['authenticated'] = True
        integration_status['user_info'] = user_info
        integration_status['last_update'] = datetime.now().isoformat()
        
        # Emitir evento a frontend (requiere socketio)
        # emit('whatsapp_authenticated', {'user_info': user_info}, broadcast=True)
        print(f"✅ WhatsApp autenticado: {user_info}")
    
    async def on_qr_code(qr_data):
        """Callback cuando se recibe un código QR"""
        integration_status['qr_code'] = qr_data
        integration_status['last_update'] = datetime.now().isoformat()
        
        # Emitir evento a frontend (requiere socketio)
        # emit('whatsapp_qr_code', {'qr_data': qr_data}, broadcast=True)
        print(f"📱 QR Code recibido (longitud: {len(qr_data)} chars)")
    
    async def on_status_change(status, message):
        """Callback para cambios de estado"""
        integration_status['connected'] = status == 'connected'
        integration_status['session_active'] = status in ['connected', 'authenticated']
        integration_status['last_update'] = datetime.now().isoformat()
        
        # Emitir evento a frontend (requiere socketio)
        # emit('whatsapp_status_change', {'status': status, 'message': message}, broadcast=True)
        print(f"📊 Estado WhatsApp: {status} - {message}")
    
    # Registrar callbacks
    client.set_on_authenticated_callback(on_authenticated)
    client.set_on_qr_code_callback(on_qr_code)
    client.set_on_status_change_callback(on_status_change)

# Función para auto-inicializar en startup
def auto_initialize_whatsapp():
    """Auto-inicializar WhatsApp Web al startup"""
    try:
        client = get_whatsapp_client()
        if not client:
            client = initialize_whatsapp_client(WHATSAPP_BACKEND_URL)
            setup_whatsapp_callbacks(client)
            print(f"🚀 Cliente WhatsApp Web inicializado para {WHATSAPP_BACKEND_URL}")
    except Exception as e:
        print(f"❌ Error auto-inicializando WhatsApp Web: {e}")

# Auto-inicializar cuando se importa el módulo
auto_initialize_whatsapp()
