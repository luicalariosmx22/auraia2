import json
import os
from datetime import datetime
from twilio.rest import Client
from flask import session, redirect, url_for
from dotenv import load_dotenv

load_dotenv()

# Decorador reutilizable
def login_requerido(func):
    def wrapper(*args, **kwargs):
        if not session.get('logueado'):
            return redirect(url_for('main.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

def cargar_configuracion():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"usar_openai": False}

def guardar_configuracion(data):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def obtener_info_twilio():
    try:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        client = Client(account_sid, auth_token)
        cuenta = client.api.accounts(account_sid).fetch()
        return {
            "nombre": cuenta.friendly_name,
            "estado": cuenta.status,
            "fecha_creado": cuenta.date_created.strftime("%Y-%m-%d")
        }
    except Exception as e:
        return {"error": str(e)}

def obtener_info_openai():
    return {"estado": "activo"}
