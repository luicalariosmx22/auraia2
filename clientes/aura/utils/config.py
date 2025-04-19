import os
from datetime import datetime
from twilio.rest import Client
from flask import session, redirect, url_for
from dotenv import load_dotenv
from supabase import create_client
import json
from functools import wraps

# Cargar variables de entorno
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Decorador reutilizable
def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login.login_google"))
        return f(*args, **kwargs)
    return decorated_function

# Cargar configuración desde Supabase
def cargar_configuracion():
    try:
        response = supabase.table("configuracion_bot").select("*").limit(1).execute()
        if not response.data:
            print(f"❌ Error al cargar configuración: {not response.data}")
            return {"usar_openai": False}  # Valor predeterminado
        return response.data[0]  # Devuelve la primera configuración encontrada
    except Exception as e:
        print(f"❌ Error al cargar configuración: {str(e)}")
        return {"usar_openai": False}  # Valor predeterminado

# Guardar configuración en Supabase
def guardar_configuracion(data):
    try:
        response = supabase.table("configuracion_bot").upsert(data).execute()
        if not response.data:
            print(f"❌ Error al guardar configuración: {not response.data}")
        else:
            print("✅ Configuración guardada correctamente en Supabase")
    except Exception as e:
        print(f"❌ Error al guardar configuración: {str(e)}")

# Obtener información de Twilio
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

# Obtener información de OpenAI
def obtener_info_openai():
    return {"estado": "activo"}