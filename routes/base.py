#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Rutas base para la aplicación AuraAI
"""

from flask import Blueprint, jsonify

# Crear blueprint
base_bp = Blueprint('base', __name__)

@base_bp.route('/', methods=['GET'])
def index():
    """Ruta de bienvenida para la API"""
    return jsonify({
        "mensaje": "API de AuraAI funcionando correctamente",
        "version": "1.0.0"
    }), 200

@base_bp.route('/status', methods=['GET'])
def status():
    """Ruta de verificación de estado"""
    return jsonify({
        "status": "online",
        "timestamp": import_datetime().now().isoformat()
    }), 200

def import_datetime():
    """Importa el módulo datetime (usado para evitar importaciones cíclicas)"""
    from datetime import datetime
    return datetime
