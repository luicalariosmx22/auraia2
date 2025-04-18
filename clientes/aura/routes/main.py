from flask import Blueprint, render_template, request, redirect, url_for, session
from supabase import create_client
from dotenv import load_dotenv
import json
import os
from utils.config import cargar_configuracion

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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

        # 👇 Prints de depuración para Railway Logs
        print("👉 ADMIN_PASSWORD:", os.getenv("ADMIN_PASSWORD"))
        print("👉 LOGIN_PASSWORD:", os.getenv("LOGIN_PASSWORD"))
        print("👉 Password ingresado:", password)

        if password in [os.getenv("ADMIN_PASSWORD"), os.getenv("LOGIN_PASSWORD")]:
            session['logueado'] = True
            return redirect(url_for('main.index'))
        else:
            error = "Contraseña incorrecta."

    return render_template('login.html', error=error)

# TOGGLE IA
@main_bp.route('/toggle_ia', methods=['POST'])
@login_requerido
def toggle_ia():
    try:
        response = supabase.table("bot_data").select("*").execute()
        if not response.data:
            print(f"❌ Error al cargar configuración: {response.error}")
            return redirect(url_for('main.index'))

        config = response.data[0]
        usar_openai = not config.get("usar_openai", False)

        # Actualizar configuración en Supabase
        supabase.table("bot_data").update({"usar_openai": usar_openai}).eq("id", config["id"]).execute()
    except Exception as e:
        print(f"❌ Error al actualizar configuración: {str(e)}")

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
        # Cargar datos desde Supabase
        response_bot_data = supabase.table("bot_data").select("*").execute()
        response_categorias = supabase.table("categorias").select("*").execute()

        if response_bot_data.error or not response_bot_data.data:
            print(f"❌ Error al cargar bot_data: {response_bot_data.error}")
            data = {}
        else:
            data = response_bot_data.data[0]

        if response_categorias.error or not response_categorias.data:
            print(f"❌ Error al cargar categorias: {response_categorias.error}")
            categorias = []
        else:
            categorias = [c["nombre"] for c in response_categorias.data]

    except Exception as e:
        print(f"❌ Error al cargar datos: {str(e)}")
        data = {}
        categorias = []

    info_twilio = {
        "nombre": os.getenv("TWILIO_ACCOUNT_SID", "No disponible"),
        "estado": "activo",
        "fecha_creado": "N/A"
    }

    info_openai = {
        "estado": "activo" if data.get("usar_openai", False) else "inactivo"
    }

    return render_template(
        'index.html',
        datos=data,
        categorias=categorias,
        usar_openai=data.get("usar_openai", False),
        info_twilio=info_twilio,
        info_openai=info_openai
    )

# PANEL EN TIEMPO REAL
@main_bp.route('/panel')
@login_requerido
def panel_conversaciones():
    return render_template('panel_conversaciones.html')

# ✅ ÚNICO BLOQUE PARA INICIAR LA APP
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
