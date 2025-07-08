#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para obtener un nuevo refresh token de Google Ads a través del flujo OAuth2.
Este script:
1. Inicia un servidor local para recibir la redirección de OAuth2
2. Abre un navegador para que el usuario autorice la aplicación
3. Captura el código de autorización que devuelve Google
4. Intercambia el código de autorización por un token de acceso y refresh token
5. Actualiza la tabla google_ads_config en Supabase con el nuevo refresh token
"""

import os
import sys
import json
import traceback
import requests
import webbrowser
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time
import re

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

def cargar_variables_entorno():
    """Carga variables de entorno desde archivos .env y .env.local usando regex para manejar múltiples signos ="""
    try:
        # Lista de posibles archivos de entorno - intentar todos los que puedan existir
        env_files = []
        root_dir = os.getcwd()
        for file in os.listdir(root_dir):
            if file.startswith('.env') or file.endswith('.env') or 'env' in file.lower():
                env_files.append(os.path.join(root_dir, file))
        
        # También añadir las rutas estándar por si acaso
        standard_files = [
            os.path.join(os.getcwd(), '.env'),
            os.path.join(os.getcwd(), '.env.local'),
            os.path.join(os.getcwd(), '.env.development'),
            os.path.join(os.getcwd(), '.env.production')
        ]
        
        for file in standard_files:
            if file not in env_files:
                env_files.append(file)
        
        for env_path in env_files:
            if os.path.isfile(env_path):
                print(f"ℹ️ Leyendo archivo de entorno: {env_path}")
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
                                key = match.group(1).strip()
                                value = match.group(2).strip()
                                
                                # Eliminar comillas si existen
                                if (value.startswith('"') and value.endswith('"')) or \
                                   (value.startswith("'") and value.endswith("'")):
                                    value = value[1:-1]
                                
                                # No sobrescribir si ya existe
                                if key not in os.environ:
                                    os.environ[key] = value
                                    if not key.upper().startswith('PASS') and not 'SECRET' in key.upper() and not 'TOKEN' in key.upper():
                                        print(f"  ✓ Variable cargada: {key}")
                                    else:
                                        print(f"  ✓ Variable sensible cargada: {key} (valor oculto)")
                            else:
                                print(f"  ⚠️ Formato incorrecto: {linea}")
                except Exception as e:
                    print(f"  ⚠️ Error al leer archivo {env_path}: {e}")
                    
    except Exception as e:
        print(f"⚠️ Error al cargar variables de entorno: {e}")
        traceback.print_exc()

def obtener_credenciales_supabase():
    """
    Obtiene las credenciales de Supabase del entorno
    """
    # Cargar variables de entorno
    cargar_variables_entorno()
    
    # Verificar si tenemos las credenciales de Supabase
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ No se encontraron credenciales de Supabase en las variables de entorno.")
        print("Asegúrate de tener SUPABASE_URL y SUPABASE_KEY definidas en tu archivo .env")
        return None, None
    
    return supabase_url, supabase_key

def obtener_credenciales_google():
    """
    Obtiene las credenciales de Google Ads desde la base de datos o el entorno
    """
    # Obtener credenciales de Supabase
    supabase_url, supabase_key = obtener_credenciales_supabase()
    if not supabase_url or not supabase_key:
        return None
    
    try:
        # Configurar encabezados
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        # Consultar la tabla
        endpoint = f"{supabase_url}/rest/v1/google_ads_config?select=*&limit=1"
        response = requests.get(endpoint, headers=headers)
        
        if response.status_code == 200 and response.json():
            credenciales = response.json()[0]
            
            # Verificar credenciales mínimas
            if credenciales.get('client_id') and credenciales.get('client_secret'):
                print("✅ Credenciales obtenidas correctamente de Supabase")
                return credenciales
        
        # Si no hay credenciales en la BD, intentar obtenerlas del entorno
        print("⚠️ No se encontraron credenciales en la base de datos, buscando en variables de entorno...")
        
        client_id = os.environ.get('GOOGLE_CLIENT_ID') or os.environ.get('GOOGLE_ADS_CLIENT_ID')
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET') or os.environ.get('GOOGLE_ADS_CLIENT_SECRET')
        
        if client_id and client_secret:
            print("✅ Credenciales obtenidas correctamente de variables de entorno")
            return {
                'client_id': client_id,
                'client_secret': client_secret
            }
        
        print("❌ No se encontraron credenciales de Google Ads")
        return None
        
    except Exception as e:
        print(f"❌ Error al obtener credenciales: {e}")
        traceback.print_exc()
        return None

# Variables globales para el servidor OAuth
auth_code = None
server_running = False
server = None

class OAuthHandler(BaseHTTPRequestHandler):
    """
    Manejador para el servidor HTTP que recibe la redirección de OAuth2
    """
    def do_GET(self):
        global auth_code
        
        # Analizar la URL de la solicitud
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        # Verificar si tenemos un código de autorización
        if 'code' in query_params:
            auth_code = query_params['code'][0]
            
            # Responder al cliente
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            response = """
            <html>
            <head>
                <title>Autorización completada</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
                    .success { color: green; font-size: 24px; margin-bottom: 20px; }
                    .info { color: #555; margin-bottom: 30px; }
                </style>
            </head>
            <body>
                <h1 class="success">✅ Autorización completada</h1>
                <p class="info">La autorización de Google Ads se ha completado correctamente.</p>
                <p>Puedes cerrar esta ventana y volver a la aplicación.</p>
            </body>
            </html>
            """
            
            self.wfile.write(response.encode('utf-8'))
        else:
            # Error en la autorización
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            response = """
            <html>
            <head>
                <title>Error de autorización</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
                    .error { color: red; font-size: 24px; margin-bottom: 20px; }
                    .info { color: #555; margin-bottom: 30px; }
                </style>
            </head>
            <body>
                <h1 class="error">❌ Error de autorización</h1>
                <p class="info">No se recibió el código de autorización de Google.</p>
                <p>Por favor, cierra esta ventana y vuelve a intentarlo.</p>
            </body>
            </html>
            """
            
            self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args):
        # Suprimir logs del servidor
        pass

def iniciar_servidor():
    """
    Inicia el servidor HTTP para recibir la redirección de OAuth2
    """
    global server_running, server
    
    server_address = ('localhost', 8080)
    server = HTTPServer(server_address, OAuthHandler)
    server_running = True
    
    print("🌐 Iniciando servidor local en http://localhost:8080")
    server.serve_forever()

def detener_servidor():
    """
    Detiene el servidor HTTP
    """
    global server_running, server
    
    if server_running and server:
        server.shutdown()
        server_running = False
        print("🛑 Servidor local detenido")

def obtener_nuevo_refresh_token():
    """
    Obtiene un nuevo refresh token a través del flujo OAuth2
    """
    # Obtener credenciales
    credenciales = obtener_credenciales_google()
    if not credenciales:
        print("❌ No se pudieron obtener las credenciales necesarias")
        return False
    
    # Iniciar servidor en un hilo separado
    server_thread = threading.Thread(target=iniciar_servidor)
    server_thread.daemon = True
    server_thread.start()
    
    # Permitir que el servidor se inicie
    time.sleep(1)
    
    # Construir URL de autorización
    redirect_uri = "http://localhost:8080"
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={credenciales['client_id']}&redirect_uri={redirect_uri}&response_type=code&scope=https://www.googleapis.com/auth/adwords&access_type=offline&prompt=consent"
    
    # Abrir navegador
    print(f"🔗 Abriendo navegador para autorización. Por favor, autoriza la aplicación...")
    webbrowser.open(auth_url)
    
    # Esperar a que el usuario autorice
    print("⏳ Esperando autorización del usuario...")
    
    # Esperar hasta 2 minutos para la autorización
    timeout = 120
    start_time = time.time()
    
    while auth_code is None:
        if time.time() - start_time > timeout:
            print("❌ Tiempo de espera agotado. No se recibió autorización.")
            detener_servidor()
            return False
        
        time.sleep(1)
    
    # Detener el servidor
    detener_servidor()
    
    print("✅ Código de autorización recibido")
    
    # Intercambiar código por tokens
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": credenciales['client_id'],
        "client_secret": credenciales['client_secret'],
        "code": auth_code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    
    try:
        print("🔄 Intercambiando código por tokens...")
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            
            if "refresh_token" in token_data:
                print("✅ Refresh token obtenido correctamente")
                
                # Actualizar en la base de datos
                actualizar_tokens_en_bd(credenciales.get('id'), token_data)
                
                return True
            else:
                print("❌ No se recibió refresh_token en la respuesta")
                print(f"Respuesta: {json.dumps(token_data, indent=2)}")
                return False
        else:
            print(f"❌ Error en la solicitud de token: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Respuesta: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error en el intercambio de tokens: {e}")
        traceback.print_exc()
        return False

def actualizar_tokens_en_bd(id_registro, token_data):
    """
    Actualiza los tokens en la base de datos
    """
    # Obtener credenciales de Supabase
    supabase_url, supabase_key = obtener_credenciales_supabase()
    if not supabase_url or not supabase_key:
        return False
    
    try:
        # Configurar encabezados
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        # Preparar datos para actualizar
        update_data = {
            "refresh_token": token_data["refresh_token"],
            "access_token": token_data["access_token"],
            "token_type": token_data.get("token_type", "Bearer"),
            "expires_in": token_data.get("expires_in", 3600),
            "token_updated_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "refresh_token_valid": True
        }
        
        if id_registro:
            # Actualizar registro existente
            endpoint = f"{supabase_url}/rest/v1/google_ads_config?id=eq.{id_registro}"
            response = requests.patch(endpoint, headers=headers, json=update_data)
        else:
            # Buscar si hay algún registro para actualizar
            endpoint = f"{supabase_url}/rest/v1/google_ads_config?select=id"
            response = requests.get(endpoint, headers=headers)
            
            if response.status_code == 200 and response.json():
                # Actualizar el primer registro
                id_registro = response.json()[0]['id']
                endpoint = f"{supabase_url}/rest/v1/google_ads_config?id=eq.{id_registro}"
                response = requests.patch(endpoint, headers=headers, json=update_data)
            else:
                # Crear nuevo registro
                endpoint = f"{supabase_url}/rest/v1/google_ads_config"
                
                # Asegurarnos de tener client_id y client_secret
                if "client_id" not in update_data or "client_secret" not in update_data:
                    update_data["client_id"] = os.environ.get('GOOGLE_CLIENT_ID') or os.environ.get('GOOGLE_ADS_CLIENT_ID')
                    update_data["client_secret"] = os.environ.get('GOOGLE_CLIENT_SECRET') or os.environ.get('GOOGLE_ADS_CLIENT_SECRET')
                
                update_data["created_at"] = datetime.now().isoformat()
                update_data["activo"] = True
                
                response = requests.post(endpoint, headers=headers, json=update_data)
        
        if response.status_code in [200, 201]:
            print("✅ Tokens actualizados correctamente en la base de datos")
            return True
        else:
            print(f"❌ Error al actualizar tokens en la base de datos: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Respuesta: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error al actualizar tokens: {e}")
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("\n🚀 OBTENCIÓN DE NUEVO REFRESH TOKEN DE GOOGLE ADS\n")
    print("="*80 + "\n")
    
    try:
        # Cargar variables de entorno
        print("📁 Cargando variables de entorno...")
        cargar_variables_entorno()
        
        # Obtener nuevo refresh token
        print("\n🔑 Iniciando proceso de autorización OAuth2...")
        resultado = obtener_nuevo_refresh_token()
        
        if resultado:
            print("\n✅ Proceso completado correctamente.")
            print("El refresh token ha sido renovado y actualizado en la base de datos.")
            print("\nAhora puedes usar la API de Google Ads sin problemas.")
        else:
            print("\n❌ No se pudo completar el proceso de renovación del token.")
            print("Por favor, verifica las credenciales y vuelve a intentarlo.")
        
        return 0 if resultado else 1
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        traceback.print_exc()
        return 1
    finally:
        # Asegurarnos de que el servidor se detenga si sigue ejecutándose
        if server_running:
            detener_servidor()

if __name__ == "__main__":
    sys.exit(main())
