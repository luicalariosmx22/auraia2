import os
from flask import Blueprint, request, redirect, url_for, render_template
from clientes.aura.auth.login import login_bp
from clientes.aura.auth.simple_login import simple_login_bp

def registrar_blueprints_login(app, safe_register_blueprint):
    # ✅ Login principal (Google OAuth)
    safe_register_blueprint(app, login_bp, url_prefix="/login")
    
    # 🔑 Login simple para testing y desarrollo
    safe_register_blueprint(app, simple_login_bp, url_prefix="/login")
