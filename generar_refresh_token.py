#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para generar un nuevo refresh token para Google Ads API.
Este script inicia un servidor web local que maneja el flujo de autorización OAuth2.

1. Abre un navegador para que el usuario inicie sesión en Google
2. Recibe el código de autorización de Google
3. Intercambia el código por tokens de acceso y actualización
4. Guarda los tokens en la tabla google_ads_config en Supabase
"""

import os
import sys
import json
import traceback
import webbrowser
from urllib.parse import urlencode
from datetime import datetime
import requests
from flask import Flask, request, redirect
import threading
import time

# Configurar codificación para Windows
if sys.platform == 'win32':
    import io
    import codecs
    # Configurar codificación para consola en Windows
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        # Forzar codificación UTF-8 para entrada/salida
        codecs.register_error('strict', codecs.replace_errors)
    except Exception as e:
        print(f"Advertencia: No se pudo configurar la codificación: {e}")
    
    # Intentar configurar la consola de Windows para UTF-8
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCP(65001)  # Establecer codificación de entrada a UTF-8
        kernel32.SetConsoleOutputCP(65001)  # Establecer codificación de salida a UTF-8
    except Exception:
        pass  # Si falla, continuamos con la configuración predeterminada

# Variables para el flujo OAuth2
auth_code = None
auth_completed = False
app = Flask(__name__)

# Intentar importar el cliente Supabase
try:
    from clientes.aura.utils.supabase_client import supabase
    SUPABASE_CLIENT_AVAILABLE = True
except ImportError:
    SUPABASE_CLIENT_AVAILABLE = False
    print("⚠️ No se pudo importar el cliente de Supabase. Se usará la API REST directamente.")

def cargar_credenciales_env():
    """Carga las credenciales de Google OAuth desde los archivos .env"""
    import re
    
    credenciales = {
        "client_id": None,
        "client_secret": None,
        "developer_token": None,
        "login_customer_id": None,
    }
    
    # Mapeo de nombres de variables en .env a nombres en nuestra estructura
    mapeo_variables = {
        "GOOGLE_CLIENT_ID": "client_id",
        "GOOGLE_CLIENT_SECRET": "client_secret",
        "GOOGLE_DEVELOPER_TOKEN": "developer_token",
        "GOOGLE_LOGIN_CUSTOMER_ID": "login_customer_id",
        # Variables alternativas
        "GOOGLE_ADS_CLIENT_ID": "client_id",
        "GOOGLE_ADS_CLIENT_SECRET": "client_secret",
        "GOOGLE_ADS_DEVELOPER_TOKEN": "developer_token",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID": "login_customer_id",
    }
    
    # Lista de archivos a revisar
    env_files = [
        os.path.join(os.getcwd(), '.env'),
        os.path.join(os.getcwd(), '.env.local'),
        os.path.join(os.getcwd(), '.env.development'),
    ]
    
    for env_path in env_files:
        if os.path.isfile(env_path):
            try:
                with open(env_path, 'r', encoding='utf-8', errors='replace') as f:
                    contenido = f.read()
                    
                    # Procesar cada línea
                    for linea in contenido.splitlines():
                        linea = linea.strip()
                        
                        # Ignorar líneas vacías o comentarios
                        if not linea or linea.startswith('#'):
                            continue
                        
                        # Usar expresión regular para separar en la primera ocurrencia de =
                        match = re.match(r'^([^=]+)=(.*)$', linea)
                        if match:
                            clave = match.group(1).strip()
                            valor = match.group(2).strip()
                            
                            # Eliminar comillas si existen
                            if (valor.startswith('"') and valor.endswith('"')) or \
                               (valor.startswith("'") and valor.endswith("'")):
                                valor = valor[1:-1]
                            
                            # Verificar si esta clave nos interesa
                            if clave in mapeo_variables and not credenciales[mapeo_variables[clave]]:
                                credenciales[mapeo_variables[clave]] = valor
            except Exception as e:
                print(f"⚠️ Error leyendo {env_path}: {e}")
    
    return credenciales

def obtener_credenciales_supabase():
    """Obtiene las credenciales existentes desde Supabase"""
    if SUPABASE_CLIENT_AVAILABLE:
        try:
            response = supabase.table("google_ads_config").select("*").limit(1).execute()
            if response.data:
                return response.data[0], response.data[0]['id']
            return None, None
        except Exception as e:
            print(f"⚠️ Error obteniendo credenciales desde Supabase: {e}")
            return None, None
    else:
        # Usar la API REST directamente
        try:
            supabase_url = os.environ.get('SUPABASE_URL')
            supabase_key = os.environ.get('SUPABASE_KEY')
            
            if not supabase_url or not supabase_key:
                print("❌ No se encontraron credenciales de Supabase en variables de entorno.")
                return None, None
                
            headers = {
                'apikey': supabase_key,
                'Authorization': f'Bearer {supabase_key}',
                'Content-Type': 'application/json',
            }
            
            endpoint = f"{supabase_url}/rest/v1/google_ads_config?select=*&limit=1"
            response = requests.get(endpoint, headers=headers)
            
            if response.status_code == 200 and response.json():
                data = response.json()[0]
                return data, data['id']
            return None, None
        except Exception as e:
            print(f"⚠️ Error obteniendo credenciales con API REST: {e}")
            return None, None

def actualizar_credenciales_supabase(id_registro, datos):
    """Actualiza las credenciales en Supabase"""
    if SUPABASE_CLIENT_AVAILABLE and id_registro:
        try:
            response = supabase.table("google_ads_config").update(
                datos
            ).eq("id", id_registro).execute()
            
            return response.data is not None
        except Exception as e:
            print(f"⚠️ Error actualizando credenciales en Supabase: {e}")
            return False
    else:
        # Usar la API REST directamente
        try:
            supabase_url = os.environ.get('SUPABASE_URL')
            supabase_key = os.environ.get('SUPABASE_KEY')
            
            if not supabase_url or not supabase_key:
                print("❌ No se encontraron credenciales de Supabase en variables de entorno.")
                return False
                
            headers = {
                'apikey': supabase_key,
                'Authorization': f'Bearer {supabase_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            }
            
            if id_registro:
                # Actualizar registro existente
                endpoint = f"{supabase_url}/rest/v1/google_ads_config?id=eq.{id_registro}"
                response = requests.patch(endpoint, headers=headers, json=datos)
                return response.status_code == 200
            else:
                # Crear nuevo registro
                endpoint = f"{supabase_url}/rest/v1/google_ads_config"
                response = requests.post(endpoint, headers=headers, json=datos)
                return response.status_code == 201
        except Exception as e:
            print(f"⚠️ Error actualizando credenciales con API REST: {e}")
            return False

# Rutas para el servidor Flask
@app.route('/')
def index():
    """Página inicial que informa sobre el proceso"""
    return """
    <html>
    <head><title>Autorización de Google Ads</title></head>
    <body>
        <h1>Generador de Refresh Token para Google Ads</h1>
        <p>Este servidor local maneja el flujo de autorización OAuth2 para Google Ads API.</p>
        <p>Presiona el botón para iniciar el proceso de autorización.</p>
        <a href="/login" style="display: inline-block; background: #4285F4; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
            Iniciar autorización con Google
        </a>
    </body>
    </html>
    """

@app.route('/login')
def login():
    """Inicia el flujo de autorización redirigiendo al usuario a Google"""
    # Cargar credenciales
    credenciales = cargar_credenciales_env()
    
    if not credenciales["client_id"]:
        return "Error: No se encontró el Client ID en los archivos .env"
    
    # Construir la URL de autorización
    auth_params = {
        'client_id': credenciales["client_id"],
        'redirect_uri': 'http://localhost:8000/callback',
        'scope': 'https://www.googleapis.com/auth/adwords',
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent',  # Forzar a mostrar pantalla de consentimiento para obtener refresh_token
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(auth_params)}"
    
    # Redirigir al usuario a la URL de autorización
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """Maneja la respuesta de Google después de la autorización"""
    global auth_code, auth_completed
    
    # Obtener el código de autorización
    if 'code' in request.args:
        auth_code = request.args.get('code')
        auth_completed = True
        
        return """
        <html>
        <head><title>Autorización completada</title></head>
        <body>
            <h1>¡Autorización completada correctamente!</h1>
            <p>Se ha obtenido el código de autorización.</p>
            <p>Puedes cerrar esta ventana y volver al terminal.</p>
        </body>
        </html>
        """
    else:
        auth_completed = True
        return """
        <html>
        <head><title>Error de autorización</title></head>
        <body>
            <h1>Error en la autorización</h1>
            <p>No se ha podido obtener el código de autorización.</p>
            <p>Por favor, revisa los logs en el terminal.</p>
        </body>
        </html>
        """

def exchange_code_for_tokens(auth_code, client_id, client_secret):
    """Intercambia el código de autorización por tokens de acceso y actualización"""
    token_url = "https://oauth2.googleapis.com/token"
    
    data = {
        'code': auth_code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': 'http://localhost:8000/callback',
        'grant_type': 'authorization_code',
    }
    
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Error obteniendo tokens: {response.status_code}")
        print(f"Respuesta: {response.json()}")
        return None

def iniciar_servidor():
    """Inicia el servidor Flask en un hilo separado"""
    thread = threading.Thread(target=lambda: app.run(host='localhost', port=8000, debug=False))
    thread.daemon = True
    thread.start()
    
    # Abrir navegador automáticamente
    webbrowser.open('http://localhost:8000')
    
    return thread

def main():
    """Función principal"""
    global auth_code, auth_completed
    
    print("\n🚀 GENERADOR DE REFRESH TOKEN PARA GOOGLE ADS\n")
    print("="*80 + "\n")
    
    try:
        # Cargar credenciales existentes
        print("🔍 Buscando credenciales existentes...")
        credenciales_env = cargar_credenciales_env()
        credenciales_db, id_registro = obtener_credenciales_supabase()
        
        # Combinar credenciales (prioridad a las de .env)
        credenciales_combinadas = {}
        if credenciales_db:
            credenciales_combinadas.update(credenciales_db)
        for key, value in credenciales_env.items():
            if value:
                credenciales_combinadas[key] = value
        
        # Verificar credenciales mínimas necesarias
        if not credenciales_combinadas.get('client_id') or not credenciales_combinadas.get('client_secret'):
            print("❌ Faltan credenciales necesarias para el proceso de autorización.")
            print(f"   Client ID: {'✅' if credenciales_combinadas.get('client_id') else '❌'}")
            print(f"   Client Secret: {'✅' if credenciales_combinadas.get('client_secret') else '❌'}")
            return 1
        
        # Mostrar resumen de credenciales
        print("\n📋 Credenciales disponibles:")
        client_id = credenciales_combinadas.get('client_id')
        client_secret = credenciales_combinadas.get('client_secret')
        developer_token = credenciales_combinadas.get('developer_token')
        login_customer_id = credenciales_combinadas.get('login_customer_id')
        
        print(f"   Client ID: {client_id[:10]}...{client_id[-10:] if client_id else ''}")
        print(f"   Client Secret: {'✅ Disponible' if client_secret else '❌ No disponible'}")
        print(f"   Developer Token: {'✅ Disponible' if developer_token else '❌ No disponible'}")
        print(f"   Login Customer ID: {login_customer_id if login_customer_id else '❌ No disponible'}")
        
        # Iniciar servidor web para el flujo OAuth2
        print("\n🌐 Iniciando servidor web local para autorización OAuth2...")
        print("   Se abrirá una ventana del navegador automáticamente.")
        print("   Si no se abre, accede a http://localhost:8000 manualmente.\n")
        
        servidor = iniciar_servidor()
        
        # Esperar a que se complete el flujo de autorización
        print("⏳ Esperando autorización del usuario...")
        timeout = 300  # 5 minutos de tiempo límite
        start_time = time.time()
        
        while not auth_completed and time.time() - start_time < timeout:
            time.sleep(1)
        
        if not auth_completed:
            print("\n❌ Tiempo de espera agotado. No se completó la autorización.")
            return 1
        
        if not auth_code:
            print("\n❌ No se obtuvo el código de autorización.")
            return 1
        
        print("✅ Código de autorización recibido!")
        
        # Intercambiar código por tokens
        print("\n🔄 Intercambiando código por tokens...")
        tokens = exchange_code_for_tokens(auth_code, client_id, client_secret)
        
        if not tokens or 'refresh_token' not in tokens:
            print("\n❌ No se pudo obtener el refresh token.")
            return 1
        
        print("✅ Tokens obtenidos correctamente!")
        
        # Preparar datos para actualizar en Supabase
        datos_actualizacion = {
            'refresh_token': tokens['refresh_token'],
            'access_token': tokens['access_token'],
            'token_type': tokens.get('token_type', 'Bearer'),
            'expires_in': tokens.get('expires_in', 3600),
            'refresh_token_valid': True,
            'token_updated_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }
        
        if not id_registro:
            # Si no hay registro, crear uno nuevo con todas las credenciales
            datos_actualizacion.update({
                'client_id': client_id,
                'client_secret': client_secret,
                'developer_token': developer_token,
                'login_customer_id': login_customer_id,
                'created_at': datetime.now().isoformat(),
                'activo': True,
            })
        
        # Actualizar en Supabase
        print("\n📝 Actualizando tokens en Supabase...")
        resultado = actualizar_credenciales_supabase(id_registro, datos_actualizacion)
        
        if resultado:
            print("✅ Tokens actualizados correctamente en Supabase!")
        else:
            print("❌ Error al actualizar tokens en Supabase.")
        
        # Mostrar información sobre el refresh token
        refresh_token = tokens['refresh_token']
        print("\n📋 Información del refresh token:")
        print(f"   Primeros caracteres: {refresh_token[:10]}...")
        print(f"   Últimos caracteres: ...{refresh_token[-10:]}")
        print(f"   Longitud: {len(refresh_token)} caracteres")
        
        print("\n✅ Proceso completado correctamente!")
        print("\nℹ️ Siguientes pasos:")
        print("1. Verifica el funcionamiento con: python verificar_directo_google_ads.py")
        print("2. Actualiza las métricas con: python actualizar_y_verificar_google_ads.py")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        traceback.print_exc()
        return 1
    finally:
        print("\n🔄 Deteniendo servidor web local...")
        os._exit(0)  # Forzar la terminación del programa para cerrar el servidor Flask

if __name__ == "__main__":
    sys.exit(main())
