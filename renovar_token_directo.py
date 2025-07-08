#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para renovar el token de acceso a Google Ads directamente con la API OAuth de Google
usando los datos almacenados en Supabase.

Este script:
1. Obtiene las credenciales de Supabase
2. Solicita un nuevo token de acceso a Google
3. Actualiza el token en Supabase
"""

import os
import sys
import json
import requests
import webbrowser
import http.server
import socketserver
import threading
import time
import traceback
from urllib.parse import urlparse, parse_qs
from datetime import datetime

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

# Variable global para almacenar el código recibido
AUTH_CODE = None

# Configuración
CONFIG = {
    "port": 8080,
    "redirect_uri": None,
    "scope": "https://www.googleapis.com/auth/adwords",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "client_id": None,
    "client_secret": None,
    "supabase_record_id": None
}

def cargar_variables_entorno():
    """Carga variables de entorno desde el archivo .env"""
    try:
        env_path = os.path.join(os.getcwd(), '.env')
        if os.path.isfile(env_path):
            print(f"ℹ️ Leyendo archivo .env: {env_path}")
            with open(env_path, 'r') as f:
                for line in f:
                    # Ignorar comentarios y líneas vacías
                    if line.strip() and not line.strip().startswith('#'):
                        # Dividir en clave y valor
                        parts = line.strip().split('=', 1)
                        if len(parts) == 2:
                            key, value = parts
                            # No sobrescribir si ya existe
                            if key not in os.environ:
                                os.environ[key] = value
    except Exception as e:
        print(f"⚠️ Error al cargar variables de entorno: {e}")

def obtener_credenciales():
    """Obtiene las credenciales de Google Ads desde Supabase"""
    print("\n🔑 Obteniendo credenciales de Google Ads desde Supabase...\n")
    
    # Cargar variables de entorno
    cargar_variables_entorno()
    
    # Obtener URL y clave de Supabase
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ No se encontraron credenciales de Supabase en las variables de entorno.")
        return False
    
    try:
        # Configurar encabezados
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json'
        }
        
        # Consultar la tabla
        endpoint = f"{supabase_url}/rest/v1/google_ads_config?select=*&limit=1"
        response = requests.get(endpoint, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            if not data:
                print("❌ No se encontraron registros de configuración de Google Ads.")
                return False
            
            registro = data[0]
            
            # Guardar los datos de configuración
            CONFIG["client_id"] = registro.get('client_id')
            CONFIG["client_secret"] = registro.get('client_secret')
            CONFIG["supabase_record_id"] = registro.get('id')
            CONFIG["redirect_uri"] = f"http://localhost:{CONFIG['port']}/oauth2callback"
            
            # Mostrar información (protegiendo datos sensibles)
            print("\n📋 Credenciales obtenidas:")
            print(f"ID de registro: {CONFIG['supabase_record_id']}")
            
            if CONFIG["client_id"]:
                client_id = CONFIG["client_id"]
                print(f"Client ID: {client_id[:8]}{'*' * 20}")
            else:
                print("⚠️ No se encontró Client ID.")
                return False
            
            if CONFIG["client_secret"]:
                print(f"Client Secret: {'*' * 10}")
            else:
                print("⚠️ No se encontró Client Secret.")
                return False
            
            print(f"Redirect URI: {CONFIG['redirect_uri']}")
            return True
            
        else:
            print(f"❌ Error al consultar la tabla: {response.status_code}")
            try:
                print(f"Detalle: {response.json()}")
            except:
                print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error obteniendo credenciales: {e}")
        traceback.print_exc()
        return False

# Servidor HTTP simple para capturar el código de autorización
class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Maneja la redirección de OAuth2 con el código de autorización."""
        global AUTH_CODE
        
        # Parsear la URL
        parsed_url = urlparse(self.path)
        
        # Verificar si es la ruta de callback
        if parsed_url.path == "/oauth2callback":
            # Extraer parámetros
            params = parse_qs(parsed_url.query)
            
            if "code" in params:
                AUTH_CODE = params["code"][0]
                
                # Enviar respuesta HTML
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Autorización Google Ads completada</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                        .success {{ color: green; }}
                    </style>
                </head>
                <body>
                    <h1 class="success">¡Autorización exitosa!</h1>
                    <p>La autorización de Google Ads se ha completado correctamente.</p>
                    <p>Puedes cerrar esta ventana y volver a la aplicación.</p>
                </body>
                </html>
                """
                
                self.wfile.write(html.encode())
            else:
                # Error - no hay código
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                
                error_msg = params.get("error", ["Error desconocido"])[0]
                
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Error de autorización</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                        .error {{ color: red; }}
                    </style>
                </head>
                <body>
                    <h1 class="error">Error de autorización</h1>
                    <p>No se pudo completar la autorización: {error_msg}</p>
                    <p>Por favor, cierre esta ventana y vuelva a intentarlo.</p>
                </body>
                </html>
                """
                
                self.wfile.write(html.encode())
        else:
            # Ruta no reconocida
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Not Found")
            
    def log_message(self, format, *args):
        # Desactivar logs del servidor
        return

def iniciar_servidor():
    """Inicia un servidor HTTP para recibir el callback de OAuth."""
    # Crear y configurar el servidor
    server = socketserver.TCPServer(("localhost", CONFIG["port"]), OAuthCallbackHandler)
    
    # Iniciar el servidor en un hilo separado
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    print(f"🌐 Servidor iniciado en puerto {CONFIG['port']}...")
    
    return server

def detener_servidor(server):
    """Detiene el servidor HTTP."""
    if server:
        server.shutdown()
        server.server_close()
        print("🛑 Servidor detenido.")

def generar_url_autorizacion():
    """Genera la URL para la autorización de OAuth2."""
    auth_params = {
        "client_id": CONFIG["client_id"],
        "redirect_uri": CONFIG["redirect_uri"],
        "scope": CONFIG["scope"],
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent"  # Forzar prompt para obtener refresh_token
    }
    
    # Construir la URL
    auth_url = f"{CONFIG['auth_uri']}?"
    auth_url += "&".join([f"{key}={value}" for key, value in auth_params.items()])
    
    return auth_url

def solicitar_token(auth_code):
    """Solicita un token de acceso usando el código de autorización."""
    print("\n🔄 Solicitando token de acceso...\n")
    
    token_params = {
        "code": auth_code,
        "client_id": CONFIG["client_id"],
        "client_secret": CONFIG["client_secret"],
        "redirect_uri": CONFIG["redirect_uri"],
        "grant_type": "authorization_code"
    }
    
    try:
        response = requests.post(CONFIG["token_uri"], data=token_params)
        
        if response.status_code == 200:
            token_data = response.json()
            
            print("✅ Token obtenido correctamente.")
            print(f"Tipo: {token_data.get('token_type', 'Bearer')}")
            print(f"Expira en: {token_data.get('expires_in', 3600)} segundos")
            
            # Verificar si obtuvo refresh_token
            if "refresh_token" in token_data:
                print("✅ Se obtuvo refresh_token.")
            else:
                print("⚠️ No se obtuvo refresh_token. Es posible que ya haya uno almacenado.")
            
            return token_data
        else:
            print(f"❌ Error obteniendo token: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Detalle: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error solicitando token: {e}")
        traceback.print_exc()
        return None

def actualizar_token_en_supabase(token_data):
    """Actualiza el token en la tabla de Supabase."""
    print("\n💾 Actualizando token en Supabase...\n")
    
    if not token_data:
        print("❌ No hay datos de token para actualizar.")
        return False
    
    # Cargar variables de entorno
    cargar_variables_entorno()
    
    # Obtener URL y clave de Supabase
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ No se encontraron credenciales de Supabase en las variables de entorno.")
        return False
    
    # Preparar datos para actualizar
    update_data = {
        "updated_at": datetime.now().isoformat(),
        "access_token": token_data.get("access_token"),
        "token_type": token_data.get("token_type", "Bearer"),
        "expires_in": token_data.get("expires_in", 3600),
    }
    
    # Añadir refresh_token solo si está presente
    if "refresh_token" in token_data:
        update_data["refresh_token"] = token_data["refresh_token"]
        update_data["refresh_token_valid"] = True
    
    try:
        # Configurar encabezados
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        # Actualizar el registro
        record_id = CONFIG["supabase_record_id"]
        endpoint = f"{supabase_url}/rest/v1/google_ads_config?id=eq.{record_id}"
        
        response = requests.patch(endpoint, headers=headers, json=update_data)
        
        if response.status_code in (200, 201, 204):
            print("✅ Token actualizado correctamente en Supabase.")
            return True
        else:
            print(f"❌ Error actualizando token: {response.status_code}")
            try:
                print(f"Detalle: {response.json()}")
            except:
                print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error actualizando token en Supabase: {e}")
        traceback.print_exc()
        return False

def renovar_token():
    """Función principal para renovar el token."""
    global AUTH_CODE
    
    print("\n🚀 RENOVACIÓN DE TOKEN DE GOOGLE ADS\n")
    print("="*80 + "\n")
    
    try:
        # Obtener credenciales de Google Ads desde Supabase
        if not obtener_credenciales():
            print("❌ No se pudieron obtener las credenciales.")
            return 1
        
        # Iniciar servidor para callback
        server = iniciar_servidor()
        
        # Generar URL de autorización
        auth_url = generar_url_autorizacion()
        print(f"\n🌐 URL de autorización generada.")
        print(f"\n✅ Abriendo navegador para autorizar la aplicación...")
        
        # Abrir navegador para autorización
        webbrowser.open(auth_url)
        
        # Esperar por el código de autorización
        print("\n⏳ Esperando autorización del usuario...")
        timeout = 300  # 5 minutos
        start_time = time.time()
        
        while AUTH_CODE is None:
            time.sleep(1)
            if time.time() - start_time > timeout:
                print("❌ Tiempo de espera agotado.")
                detener_servidor(server)
                return 1
        
        # Detener servidor
        detener_servidor(server)
        
        # Solicitar token con el código recibido
        token_data = solicitar_token(AUTH_CODE)
        
        if not token_data:
            print("❌ No se pudo obtener el token.")
            return 1
        
        # Actualizar token en Supabase
        if not actualizar_token_en_supabase(token_data):
            print("❌ No se pudo actualizar el token en Supabase.")
            return 1
        
        print("\n✅ Proceso de renovación de token completado correctamente.")
        print("\nLa configuración de Google Ads ahora está lista para usar.")
        print("\n" + "="*80 + "\n")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        traceback.print_exc()
        return 1
    
if __name__ == "__main__":
    sys.exit(renovar_token())
