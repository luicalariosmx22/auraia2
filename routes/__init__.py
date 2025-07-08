#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Definición y registro de rutas para la aplicación AuraAI
"""

from flask import Blueprint, Flask

def register_blueprints(app: Flask):
    """
    Registra todos los blueprints de la aplicación
    """
    # Importar blueprints
    from routes.base import base_bp
    from routes.google_ads import google_ads_bp
    # Importar otros blueprints aquí según sea necesario
    
    # Registrar blueprints
    app.register_blueprint(base_bp)
    app.register_blueprint(google_ads_bp)
    # Registrar otros blueprints aquí
    
    return app
