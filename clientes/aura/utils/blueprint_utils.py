# ✅ Archivo: clientes/aura/utils/blueprint_utils.py

from flask import Flask, Blueprint
import logging

logger = logging.getLogger(__name__)

def safe_register_blueprint(app: Flask, blueprint: Blueprint, url_prefix: str = None):
    """
    Registra un blueprint solo si no está ya registrado.
    ✅ Esto evita errores de 'ya estaba registrado' y elimina duplicados.
    """
    blueprint_name = blueprint.name
    if blueprint_name in app.blueprints:
        logger.warning(f"⚠️ Blueprint ya estaba registrado: {blueprint_name}")
    else:
        app.register_blueprint(blueprint, url_prefix=url_prefix)
        logger.info(f"✅ Blueprint registrado: {blueprint_name} con prefijo: {url_prefix}")
