# ✅ Archivo: clientes/aura/utils/blueprint_utils.py

from flask import Flask, Blueprint
from clientes.aura.routes.login import login_bp

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

print("🚀 DEBUG: blueprints_utils.py cargado - función registrar_blueprints_login actualizada")

def registrar_blueprints_login(app, safe_register_blueprint=None):
    if safe_register_blueprint:
        # ✅ Registramos el blueprint de manera segura usando la función proporcionada.
        safe_register_blueprint(app, login_bp)
    else:
        # ✅ Registro directo (sin manejo seguro).
        app.register_blueprint(login_bp)
