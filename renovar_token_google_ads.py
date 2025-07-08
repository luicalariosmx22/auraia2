#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Herramienta para renovar automáticamente el token de acceso de Google Ads.

Este script facilita el proceso de renovación del token de acceso para Google Ads
cuando ha expirado o ha sido revocado.
"""

import os
import sys
import json
import argparse
import webbrowser
from datetime import datetime
import time
from urllib.parse import parse_qs, urlparse
import http.server
import socketserver
import threading
import requests
import traceback

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

try:
    from clientes.aura.utils.supabase_client import supabase
except ImportError as e:
    print(f"❌ Error importando dependencias: {e}")
    print("Asegúrate de estar en el directorio raíz del proyecto y que las dependencias estén instaladas.")
    sys.exit(1)

# Configuración global
CONFIG = {
    "port": 8080,
    "client_id": None,
    "client_secret": None,
    "redirect_uri": None,
    "scope": "https://www.googleapis.com/auth/adwords",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
}

# Variable global para almacenar el código recibido
AUTH_CODE = None

class AuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Maneja las solicitudes GET al servidor local."""
        global AUTH_CODE
        
        # Procesar la ruta para extraer el código
        if self.path.startswith("/oauth2callback"):
            # Extraer parámetros de la URL
            query = urlparse(self.path).query
            params = parse_qs(query)
            
            if "code" in params:
                # Guardar el código de autorización
                AUTH_CODE = params["code"][0]
                
                # Enviar respuesta HTML
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                
                html_content = """
                <html>
                <head>
                    <title>Autorización Completada</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            max-width: 600px;
                            margin: 0 auto;
                            padding: 20px;
                            text-align: center;
                        }
                        .success {
                            color: green;
                            font-size: 24px;
                            margin: 30px 0;
                        }
                        .info {
                            background-color: #f5f5f5;
                            border-radius: 5px;
                            padding: 15px;
                            margin: 20px 0;
                        }
                    </style>
                </head>
                <body>
                    <h1>Google Ads - Autorización</h1>
                    <div class="success">¡Autorización exitosa!</div>
                    <div class="info">
                        El código de autorización ha sido recibido correctamente.<br>
                        Puedes cerrar esta ventana y volver a la terminal.
                    </div>
                </body>
                </html>
                """
                
                self.wfile.write(html_content.encode())
                
                # Notificar en consola
                print("✅ Código de autorización recibido correctamente.")
                print("   Puedes cerrar la ventana del navegador y volver a esta terminal.")
                
                return
            
            elif "error" in params:
                # Manejar error en la autorización
                error = params["error"][0]
                
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                
                html_content = f"""
                <html>
                <head>
                    <title>Error de Autorización</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            max-width: 600px;
                            margin: 0 auto;
                            padding: 20px;
                            text-align: center;
                        }}
                        .error {{
                            color: red;
                            font-size: 24px;
                            margin: 30px 0;
                        }}
                        .info {{
                            background-color: #f5f5f5;
                            border-radius: 5px;
                            padding: 15px;
                            margin: 20px 0;
                        }}
                    </style>
                </head>
                <body>
                    <h1>Google Ads - Error de Autorización</h1>
                    <div class="error">Error: {error}</div>
                    <div class="info">
                        Ha ocurrido un error durante el proceso de autorización.<br>
                        Por favor, cierra esta ventana y vuelve a intentarlo.
                    </div>
                </body>
                </html>
                """
                
                self.wfile.write(html_content.encode())
                
                # Notificar en consola
                print(f"❌ Error en la autorización: {error}")
                
                return
        
        # Para cualquier otra ruta, mostrar una página de ayuda
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        html_content = """
        <html>
        <head>
            <title>Renovación de Token Google Ads</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }
                h1 {
                    color: #4285f4;
                }
            </style>
        </head>
        <body>
            <h1>Renovación de Token de Google Ads</h1>
            <p>Esta es una herramienta para renovar el token de acceso a Google Ads.</p>
            <p>El proceso de autorización debería iniciarse automáticamente.</p>
        </body>
        </html>
        """
        
        self.wfile.write(html_content.encode())

def iniciar_servidor_local():
    """Inicia un servidor HTTP local para recibir la redirección OAuth."""
    
    # Configurar y iniciar el servidor
    handler = AuthCallbackHandler
    httpd = socketserver.TCPServer(("", CONFIG["port"]), handler)
    
    # Ejecutar en un hilo separado
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    print(f"🌐 Servidor local iniciado en el puerto {CONFIG['port']}...")
    
    return httpd

def cerrar_servidor(httpd):
    """Cierra el servidor HTTP local."""
    httpd.shutdown()
    httpd.server_close()
    print("🔒 Servidor local cerrado.")

def obtener_configuracion_supabase():
    """Obtiene la configuración de OAuth desde Supabase."""
    print("🔍 Obteniendo configuración desde Supabase...")
    
    try:
        # Consultar configuración de Google Ads en Supabase
        response = supabase.table("google_ads_config").select("*").execute()
        config = response.data
        
        if not config:
            print("⚠️ No hay configuración de Google Ads en Supabase.")
            print("¿Deseas usar configuración de ejemplo? (solo para desarrollo)")
            
            usar_ejemplo = input("Usar configuración de ejemplo? (s/n): ")
            if usar_ejemplo.lower() == 's':
                print("ℹ️ Usando configuración de ejemplo.")
                
                # Configuración de ejemplo
                CONFIG["client_id"] = "ejemplo-client-id.apps.googleusercontent.com"
                CONFIG["client_secret"] = "GOCSPX-ejemplo-client-secret"
                CONFIG["redirect_uri"] = f"http://localhost:{CONFIG['port']}/oauth2callback"
                
                print("⚠️ Esta configuración de ejemplo NO funcionará para autenticación real.")
                print("⚠️ Por favor configura credenciales reales ejecutando 'python configurar_google_ads.py'")
                
                return True
            else:
                return False
        
        # Usar el primer registro (debería ser único)
        cfg = config[0]
        
        # Verificar campos requeridos
        required_fields = ["client_id", "client_secret"]
        missing_fields = []
        
        for field in required_fields:
            if field not in cfg or not cfg.get(field):
                missing_fields.append(field)
                
        if missing_fields:
            print(f"⚠️ Campos requeridos no encontrados: {', '.join(missing_fields)}")
            print("¿Deseas usar una configuración de ejemplo? (solo para desarrollo)")
            
            usar_ejemplo = input("Usar configuración de ejemplo? (s/n): ")
            if usar_ejemplo.lower() == 's':
                print("ℹ️ Usando configuración de ejemplo.")
                
                # Configuración de ejemplo
                CONFIG["client_id"] = "ejemplo-client-id.apps.googleusercontent.com"
                CONFIG["client_secret"] = "GOCSPX-ejemplo-client-secret"
                CONFIG["redirect_uri"] = f"http://localhost:{CONFIG['port']}/oauth2callback"
                
                print("⚠️ Esta configuración de ejemplo NO funcionará para autenticación real.")
                return True
            else:
                return False
        
        # Actualizar configuración global
        CONFIG["client_id"] = cfg["client_id"]
        CONFIG["client_secret"] = cfg["client_secret"]
        CONFIG["redirect_uri"] = f"http://localhost:{CONFIG['port']}/oauth2callback"
        
        print("✅ Configuración cargada correctamente:")
        print(f"  - Client ID: {CONFIG['client_id'][:10]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al obtener configuración desde Supabase: {e}")
        print("\nDetalles del error:")
        traceback.print_exc()
        
        print("\n⚠️ ¿Deseas usar una configuración de ejemplo? (solo para desarrollo)")
        usar_ejemplo = input("Usar configuración de ejemplo? (s/n): ")
        
        if usar_ejemplo.lower() == 's':
            print("ℹ️ Usando configuración de ejemplo.")
            
            # Configuración de ejemplo
            CONFIG["client_id"] = "ejemplo-client-id.apps.googleusercontent.com"
            CONFIG["client_secret"] = "GOCSPX-ejemplo-client-secret"
            CONFIG["redirect_uri"] = f"http://localhost:{CONFIG['port']}/oauth2callback"
            
            print("⚠️ Esta configuración de ejemplo NO funcionará para autenticación real.")
            print("⚠️ Por favor configura credenciales reales ejecutando 'python configurar_google_ads.py'")
            
            return True
        
        return False

def generar_url_autorizacion():
    """Genera la URL de autorización OAuth para Google Ads."""
    params = {
        "client_id": CONFIG["client_id"],
        "redirect_uri": CONFIG["redirect_uri"],
        "scope": CONFIG["scope"],
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",  # Forzar nuevo refresh_token
    }
    
    # Construir URL con parámetros
    url = f"{CONFIG['auth_uri']}?"
    url += "&".join([f"{key}={value}" for key, value in params.items()])
    
    return url

def intercambiar_codigo_por_token(codigo):
    """Intercambia el código de autorización por tokens de acceso y actualización."""
    print("\n🔄 Intercambiando código por tokens...")
    
    data = {
        "client_id": CONFIG["client_id"],
        "client_secret": CONFIG["client_secret"],
        "code": codigo,
        "grant_type": "authorization_code",
        "redirect_uri": CONFIG["redirect_uri"],
    }
    
    try:
        response = requests.post(CONFIG["token_uri"], data=data)
        response_data = response.json()
        
        if "error" in response_data:
            print(f"❌ Error al obtener tokens: {response_data['error']}")
            if "error_description" in response_data:
                print(f"   Descripción: {response_data['error_description']}")
            return None
        
        print("✅ Tokens obtenidos correctamente.")
        
        # Mostrar información del token (parcial)
        access_token = response_data.get("access_token", "")
        refresh_token = response_data.get("refresh_token", "")
        
        if access_token:
            print(f"   Access Token: {access_token[:5]}...{access_token[-5:] if len(access_token) > 10 else ''}")
        
        if refresh_token:
            print(f"   Refresh Token: {refresh_token[:5]}...{refresh_token[-5:] if len(refresh_token) > 10 else ''}")
        else:
            print("⚠️ No se recibió refresh_token. Asegúrate de usar 'prompt=consent' y 'access_type=offline'.")
        
        return response_data
        
    except Exception as e:
        print(f"❌ Error en la solicitud de tokens: {e}")
        return None

def actualizar_token_en_supabase(tokens):
    """Actualiza los tokens en Supabase."""
    print("\n🔄 Actualizando tokens en Supabase...")
    
    if not tokens or "access_token" not in tokens:
        print("❌ No hay tokens válidos para actualizar.")
        return False
    
    try:
        # Primero obtenemos el registro actual para actualizar el correcto
        response = supabase.table("google_ads_config").select("id").execute()
        
        if not response.data:
            print("❌ No se encontró ningún registro para actualizar.")
            return False
        
        # Usar el primer registro (debería ser único)
        record_id = response.data[0]["id"]
        
        # Datos para actualizar
        update_data = {
            "access_token": tokens["access_token"],
            "token_type": tokens.get("token_type", "Bearer"),
            "expires_in": tokens.get("expires_in", 3600),
            "updated_at": datetime.now().isoformat(),
        }
        
        # Incluir refresh_token solo si está presente
        if "refresh_token" in tokens and tokens["refresh_token"]:
            update_data["refresh_token"] = tokens["refresh_token"]
            update_data["refresh_token_valid"] = True
        
        # Actualizar el registro
        response = supabase.table("google_ads_config").update(update_data).eq("id", record_id).execute()
        
        print("✅ Tokens actualizados correctamente en Supabase.")
        return True
        
    except Exception as e:
        print(f"❌ Error al actualizar tokens en Supabase: {e}")
        return False

def flujo_renovacion_token():
    """Ejecuta el flujo completo de renovación de token."""
    print("\n🚀 Iniciando flujo de renovación de token...\n")
    
    # Obtener configuración desde Supabase
    if not obtener_configuracion_supabase():
        print("❌ No se pudo obtener la configuración necesaria. Abortando.")
        return False
    
    # Iniciar servidor local para recibir redirección
    httpd = iniciar_servidor_local()
    
    try:
        # Generar URL de autorización
        auth_url = generar_url_autorizacion()
        print(f"\n🌐 Abriendo navegador para autorización...\n")
        print(f"URL: {auth_url}\n")
        
        # Abrir navegador
        webbrowser.open(auth_url)
        
        # Esperar a que se reciba el código
        print("⏳ Esperando autorización en el navegador...")
        timeout = 300  # 5 minutos
        start_time = time.time()
        
        while AUTH_CODE is None:
            time.sleep(1)
            
            # Verificar timeout
            if time.time() - start_time > timeout:
                print("❌ Tiempo de espera agotado. No se recibió el código.")
                return False
        
        print("\n🎯 Código de autorización recibido.")
        
        # Intercambiar código por tokens
        tokens = intercambiar_codigo_por_token(AUTH_CODE)
        
        if not tokens:
            print("❌ No se pudieron obtener los tokens. Abortando.")
            return False
        
        # Actualizar tokens en Supabase
        if not actualizar_token_en_supabase(tokens):
            print("❌ No se pudieron actualizar los tokens en Supabase. Abortando.")
            return False
        
        print("\n✅ Renovación de token completada exitosamente.")
        return True
        
    finally:
        # Siempre cerrar el servidor al finalizar
        time.sleep(1)  # Esperar un momento para asegurar respuesta HTTP
        cerrar_servidor(httpd)

def main():
    """Función principal del script."""
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Herramienta de renovación de token de Google Ads")
    parser.add_argument("--renew-token", action="store_true", help="Inicia el flujo de renovación de token")
    args = parser.parse_args()
    
    print("\n🔑 RENOVACIÓN DE TOKEN DE GOOGLE ADS 🔑\n")
    print("="*80 + "\n")
    
    # Verificar argumentos
    if args.renew_token:
        # Ejecutar flujo de renovación
        resultado = flujo_renovacion_token()
        
        if resultado:
            print("\n🎉 El proceso de renovación de token ha finalizado correctamente.")
            print("   Ya puedes utilizar la API de Google Ads nuevamente.")
            print("\n   Para verificar, ejecuta:")
            print("   python diagnostico_token_google_ads.py")
        else:
            print("\n❌ El proceso de renovación de token ha fallado.")
            print("   Revisa los errores anteriores e intenta nuevamente.")
        
        print("\n" + "="*80 + "\n")
        return 0 if resultado else 1
    
    else:
        # Mostrar instrucciones si no se especifican argumentos
        print("📝 Instrucciones:")
        print("   Para renovar el token, ejecuta:")
        print("   python renovar_token_google_ads.py --renew-token")
        print("\n   Para verificar el estado del token actual, ejecuta:")
        print("   python diagnostico_token_google_ads.py")
        print("\n" + "="*80 + "\n")
        return 0

if __name__ == "__main__":
    sys.exit(main())
