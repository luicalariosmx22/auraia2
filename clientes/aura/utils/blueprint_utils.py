# ✅ Archivo: clientes/aura/utils/blueprint_utils.py

from flask import Flask, Blueprint

def safe_register_blueprint(app: Flask, blueprint: Blueprint, url_prefix: str = None):
    """
    Registra un blueprint si no ha sido registrado aún.
    """
    name = blueprint.name
    if name in app.blueprints:
        print(f"⚠️ Blueprint ya estaba registrado: {name}")
    else:
        app.register_blueprint(blueprint, url_prefix=url_prefix)
        print(f"✅ Blueprint registrado: {name} con prefijo: {url_prefix}")
