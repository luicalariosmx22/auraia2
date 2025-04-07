from flask import Blueprint, render_template, request, redirect, url_for, session
import json
import os
from utils.config import cargar_configuracion

main_bp = Blueprint('main', __name__)

# Middleware login requerido
def login_requerido(func):
    def wrapper(*args, **kwargs):
        if not session.get('logueado'):
            return redirect(url_for('main.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# LOGIN
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form['password']
        if password == os.getenv("ADMIN_PASSWORD"):
            session['logueado'] = True
            return redirect(url_for('main.index'))
        else:
            error = "Contraseña incorrecta."
    return render_template('login.html', error=error)

# TOGGLE IA
@main_bp.route('/toggle_ia', methods=['POST'])
@login_requerido
def toggle_ia():
    from utils.config_helper import cargar_configuracion, guardar_configuracion
    config = cargar_configuracion()
    config["usar_openai"] = not config.get("usar_openai", False)
    guardar_configuracion(config)
    return redirect(url_for('main.index'))

# LOGOUT
@main_bp.route('/logout')
def logout():
    session.pop('logueado', None)
    return redirect(url_for('main.login'))

# HOME (Panel principal)
@main_bp.route('/')
@login_requerido
def index():
    try:
        with open('bot_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    try:
        with open('categorias.json', 'r', encoding='utf-8') as f:
            categorias = json.load(f)
    except FileNotFoundError:
        categorias = []

    config = cargar_configuracion()

    info_twilio = {
        "nombre": os.getenv("TWILIO_ACCOUNT_SID", "No disponible"),
        "estado": "activo",
        "fecha_creado": "N/A"
    }

    info_openai = {
        "estado": "activo" if config.get("usar_openai", False) else "inactivo"
    }

    return render_template(
        'index.html',
        datos=data,
        categorias=categorias,
        usar_openai=config.get("usar_openai", False),
        info_twilio=info_twilio,
        info_openai=info_openai
    )

# PANEL EN TIEMPO REAL
@main_bp.route('/panel')
@login_requerido
def panel_conversaciones():
    return render_template('panel_conversaciones.html')

# ✅ Solo este bloque debe quedar
if __name__ == "__main__":
    from app import app, socketio

    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.getenv('FLASK_ENV') == 'development'

    print(f"🚀 Iniciando desde main.py - Puerto: {port}")

    socketio.run(app,
                 host="0.0.0.0",
                 port=port,
                 debug=debug_mode,
                 use_reloader=debug_mode,
                 allow_unsafe_werkzeug=debug_mode)
