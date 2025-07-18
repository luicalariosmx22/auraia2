# ✅ Archivo: clientes/aura/utils/blueprint_utils.py

from flask import Flask, Blueprint
from clientes.aura.auth.login import login_bp  # 🛠 Corrected import to reference auth.login

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

# 🚀 Debug para confirmar que este archivo sí se está cargando
print("🚀 DEBUG: blueprints_utils_v2.py cargado - función registrar_blueprints_login actualizada")

def registrar_blueprints_login(app, safe_register_blueprint):
    safe_register_blueprint(app, login_bp)  # 🛠 Register login_bp
