"""
Blueprint para integrar WhatsApp Web con NORA
Conecta con el backend WhatsApp Web desplegado en Railway
"""

import os
import asyncio
import logging
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from clientes.aura.utils.whatsapp_web_client import get_whatsapp_client, initialize_whatsapp_client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint
panel_cliente_whatsapp_web_bp = Blueprint(
    "panel_cliente_whatsapp_web", 
    __name__, 
    template_folder="../../templates"
)

# URL del backend WhatsApp Web en Railway
WHATSAPP_BACKEND_URL_INTERNAL = os.getenv('WHATSAPP_BACKEND_URL_INTERNAL', 'https://whatsapp-server.railway.internal')
WHATSAPP_BACKEND_URL_PUBLIC = os.getenv('WHATSAPP_BACKEND_URL_PUBLIC', 'https://whatsapp-server-production-8f61.up.railway.app')

# Instancia global del cliente
whatsapp_client = None

def get_or_create_whatsapp_client():
    """Obtener o crear cliente WhatsApp Web"""
    global whatsapp_client
    if whatsapp_client is None:
        # Usar URL interna para comunicación entre servicios
        whatsapp_client = initialize_whatsapp_client(WHATSAPP_BACKEND_URL_INTERNAL)
    return whatsapp_client

@panel_cliente_whatsapp_web_bp.route("/whatsapp")
def panel_whatsapp_web(nombre_nora):
    """Panel principal de WhatsApp Web"""
    try:
        # Obtener cliente
        client = get_or_create_whatsapp_client()
        
        # Obtener estado de salud
        health_status = client.get_health_status()
        detailed_status = client.get_detailed_status()
        
        return render_template(
            "panel_cliente_whatsapp_web.html",
            nombre_nora=nombre_nora,
            backend_url=WHATSAPP_BACKEND_URL_PUBLIC,  # URL pública para iframe
            health_status=health_status,
            detailed_status=detailed_status,
            client_status=client.status_info if client else None
        )
    except Exception as e:
        logger.error(f"Error en panel WhatsApp Web: {e}")
        flash(f"Error cargando panel WhatsApp Web: {str(e)}", "error")
        return redirect(url_for("panel_cliente_bp.panel_cliente", nombre_nora=nombre_nora))

@panel_cliente_whatsapp_web_bp.route("/whatsapp/status")
def whatsapp_status(nombre_nora):
    """Obtener estado de WhatsApp Web"""
    try:
        client = get_or_create_whatsapp_client()
        
        # Obtener todos los estados
        health_status = client.get_health_status()
        detailed_status = client.get_detailed_status()
        client_status = client.status_info
        
        return jsonify({
            "success": True,
            "health_status": health_status,
            "detailed_status": detailed_status,
            "client_status": client_status,
            "backend_url": WHATSAPP_BACKEND_URL
        })
    except Exception as e:
        logger.error(f"Error obteniendo estado WhatsApp Web: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@panel_cliente_whatsapp_web_bp.route("/whatsapp/connect", methods=["POST"])
def connect_whatsapp(nombre_nora):
    """Conectar al backend WhatsApp Web"""
    try:
        client = get_or_create_whatsapp_client()
        
        # Conectar de forma asíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(client.connect())
        
        if success:
            return jsonify({
                "success": True,
                "message": "Conectado al backend WhatsApp Web",
                "status": client.status_info
            })
        else:
            return jsonify({
                "success": False,
                "message": "No se pudo conectar al backend WhatsApp Web"
            }), 500
            
    except Exception as e:
        logger.error(f"Error conectando WhatsApp Web: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@panel_cliente_whatsapp_web_bp.route("/whatsapp/disconnect", methods=["POST"])
def disconnect_whatsapp(nombre_nora):
    """Desconectar del backend WhatsApp Web"""
    try:
        client = get_or_create_whatsapp_client()
        
        # Desconectar de forma asíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        loop.run_until_complete(client.disconnect())
        
        return jsonify({
            "success": True,
            "message": "Desconectado del backend WhatsApp Web",
            "status": client.status_info
        })
        
    except Exception as e:
        logger.error(f"Error desconectando WhatsApp Web: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@panel_cliente_whatsapp_web_bp.route("/whatsapp/init_session", methods=["POST"])
def init_whatsapp_session(nombre_nora):
    """Inicializar sesión de WhatsApp Web"""
    try:
        client = get_or_create_whatsapp_client()
        
        # Conectar primero si no está conectado
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if not client.is_connected:
            connected = loop.run_until_complete(client.connect())
            if not connected:
                return jsonify({
                    "success": False,
                    "message": "No se pudo conectar al backend WhatsApp Web"
                }), 500
        
        # Inicializar sesión
        success = loop.run_until_complete(client.init_whatsapp_session())
        
        if success:
            return jsonify({
                "success": True,
                "message": "Sesión de WhatsApp Web iniciada",
                "status": client.status_info
            })
        else:
            return jsonify({
                "success": False,
                "message": "No se pudo iniciar la sesión de WhatsApp Web"
            }), 500
            
    except Exception as e:
        logger.error(f"Error iniciando sesión WhatsApp Web: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@panel_cliente_whatsapp_web_bp.route("/whatsapp/close_session", methods=["POST"])
def close_whatsapp_session(nombre_nora):
    """Cerrar sesión de WhatsApp Web"""
    try:
        client = get_or_create_whatsapp_client()
        
        # Cerrar sesión de forma asíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(client.close_whatsapp_session())
        
        if success:
            return jsonify({
                "success": True,
                "message": "Sesión de WhatsApp Web cerrada",
                "status": client.status_info
            })
        else:
            return jsonify({
                "success": False,
                "message": "No se pudo cerrar la sesión de WhatsApp Web"
            }), 500
            
    except Exception as e:
        logger.error(f"Error cerrando sesión WhatsApp Web: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@panel_cliente_whatsapp_web_bp.route("/whatsapp/check_status", methods=["POST"])
def check_whatsapp_status(nombre_nora):
    """Verificar estado de WhatsApp Web"""
    try:
        client = get_or_create_whatsapp_client()
        
        # Verificar estado de forma asíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(client.check_whatsapp_status())
        
        return jsonify({
            "success": success,
            "message": "Estado verificado" if success else "No se pudo verificar estado",
            "status": client.status_info
        })
        
    except Exception as e:
        logger.error(f"Error verificando estado WhatsApp Web: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@panel_cliente_whatsapp_web_bp.route("/whatsapp/iframe")
def whatsapp_iframe(nombre_nora):
    """Mostrar iframe del backend WhatsApp Web"""
    return render_template(
        "whatsapp_web_iframe.html",
        nombre_nora=nombre_nora,
        backend_url=WHATSAPP_BACKEND_URL
    )
