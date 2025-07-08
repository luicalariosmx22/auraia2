#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para renovar el token de acceso (access_token) de Google Ads
utilizando el refresh_token almacenado en la base de datos.
"""

import os
import sys
import json
from datetime import datetime
import traceback
import requests

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
    """Carga variables de entorno desde archivos .env y .env.local"""
    try:
        # Lista de posibles archivos de entorno
        env_files = [
            os.path.join(os.getcwd(), '.env'),
            os.path.join(os.getcwd(), '.env.local'),
            os.path.join(os.getcwd(), '.env.development'),
            os.path.join(os.getcwd(), '.env.production')
        ]
        
        for env_path in env_files:
            if os.path.isfile(env_path):
                print(f"ℹ️ Leyendo archivo de entorno: {env_path}")
                with open(env_path, 'r', encoding='utf-8', errors='replace') as f:
                    for line in f:
                        # Ignorar comentarios y líneas vacías
                        if line.strip() and not line.strip().startswith('#'):
                            try:
                                # Dividir en clave y valor
                                parts = line.strip().split('=', 1)
                                if len(parts) == 2:
                                    key, value = parts
                                    # No sobrescribir si ya existe
                                    if key not in os.environ:
                                        # Eliminar comillas si existen
                                        value = value.strip('\'"')
                                        os.environ[key] = value
                                        print(f"  ✓ Variable cargada: {key}")
                            except Exception as e:
                                print(f"  ⚠️ Error al procesar línea en {env_path}: {e}")
        
        # Buscar también variables específicas de Google Ads en archivos de configuración
        possible_config_files = [
            os.path.join(os.getcwd(), 'config.json'),
            os.path.join(os.getcwd(), 'google_ads_config.json')
        ]
        
        for config_path in possible_config_files:
            if os.path.isfile(config_path):
                print(f"ℹ️ Leyendo archivo de configuración: {config_path}")
                try:
                    with open(config_path, 'r', encoding='utf-8', errors='replace') as f:
                        config = json.load(f)
                        for key, value in config.items():
                            if key not in os.environ and value:
                                os.environ[key] = str(value)
                                print(f"  ✓ Variable cargada desde config: {key}")
                except Exception as e:
                    print(f"  ⚠️ Error al leer archivo {config_path}: {e}")
                    
    except Exception as e:
        print(f"⚠️ Error al cargar variables de entorno: {e}")
        traceback.print_exc()

def obtener_config_google_ads():
    """Obtiene la configuración de Google Ads desde la base de datos"""
    print("\n🔍 Obteniendo configuración de Google Ads desde Supabase...\n")
    
    # Intentar obtener credenciales de Supabase
    cargar_variables_entorno()
    
    # Obtener URL y clave de Supabase del entorno
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ No se encontraron credenciales de Supabase en las variables de entorno.")
        print("Asegúrate de tener SUPABASE_URL y SUPABASE_KEY definidas en tu archivo .env")
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
        
        if response.status_code == 200:
            data = response.json()
            if data:
                config = data[0]
                print(f"✅ Configuración de Google Ads encontrada (ID: {config.get('id')[:8]}...)")
                return config
            else:
                print("❌ No se encontró ninguna configuración de Google Ads en la base de datos.")
                return None
        else:
            print(f"❌ Error al consultar la tabla: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Detalle del error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Respuesta: {response.text}")
            return None
    
    except Exception as e:
        print(f"❌ Error obteniendo configuración: {e}")
        traceback.print_exc()
        return None

def renovar_token_acceso(config):
    """Renueva el token de acceso utilizando el refresh_token"""
    print("\n🔄 Renovando token de acceso...\n")
    
    if not config:
        print("❌ No hay configuración disponible para renovar el token.")
        return False
    
    client_id = config.get('client_id')
    client_secret = config.get('client_secret')
    refresh_token = config.get('refresh_token')
    
    if not client_id or not client_secret or not refresh_token:
        print("❌ Faltan credenciales necesarias para renovar el token:")
        if not client_id: print("   - Client ID")
        if not client_secret: print("   - Client Secret")
        if not refresh_token: print("   - Refresh Token")
        return False
    
    print(f"ℹ️ Usando Client ID: {client_id[:15]}...")
    
    try:
        # Endpoint para renovar el token
        token_url = 'https://oauth2.googleapis.com/token'
        
        # Datos para la solicitud
        payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        # Realizar la solicitud para renovar el token
        response = requests.post(token_url, data=payload)
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Token de acceso renovado correctamente.")
            print(f"ℹ️ Nuevo token expira en: {token_data.get('expires_in', 3600)} segundos")
            
            # Actualizar la configuración en la base de datos
            return actualizar_token_en_bd(config['id'], token_data)
        else:
            print(f"❌ Error renovando el token: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Detalle del error: {json.dumps(error_data, indent=2)}")
                
                # Verificar errores específicos
                error = error_data.get('error')
                if error == 'invalid_grant':
                    print("\n❗ ERROR: El refresh_token no es válido o ha sido revocado.")
                    print("Esto significa que necesitas volver a autorizar la aplicación.")
                    print("Para solucionar esto:")
                    print("1. Ve a la consola de Google Cloud: https://console.cloud.google.com")
                    print("2. Selecciona tu proyecto")
                    print("3. Ve a 'APIs y Servicios' > 'Credenciales'")
                    print("4. Encuentra tu cliente OAuth y haz clic en 'Reset Secret'")
                    print("5. Actualiza el client_secret en la base de datos")
                    print("6. Ejecuta el flujo de autorización completo para obtener un nuevo refresh_token")
            except:
                print(f"Respuesta: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error en la solicitud para renovar el token: {e}")
        traceback.print_exc()
        return False

def actualizar_token_en_bd(config_id, token_data):
    """Actualiza el token en la base de datos"""
    print("\n💾 Actualizando token en la base de datos...\n")
    
    # Obtener URL y clave de Supabase del entorno
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ No se encontraron credenciales de Supabase.")
        return False
    
    try:
        # Configurar encabezados
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        # Datos a actualizar
        update_data = {
            'access_token': token_data.get('access_token'),
            'token_type': token_data.get('token_type', 'Bearer'),
            'expires_in': token_data.get('expires_in', 3600),
            'updated_at': datetime.now().isoformat(),
            'refresh_token_valid': True
        }
        
        # Actualizar en la base de datos
        endpoint = f"{supabase_url}/rest/v1/google_ads_config?id=eq.{config_id}"
        response = requests.patch(endpoint, headers=headers, json=update_data)
        
        if response.status_code in [200, 201, 204]:
            print("✅ Token actualizado correctamente en la base de datos.")
            return True
        else:
            print(f"❌ Error actualizando el token en la base de datos: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Detalle del error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Respuesta: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error en la actualización del token: {e}")
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("\n🚀 RENOVACIÓN DE TOKEN DE ACCESO GOOGLE ADS\n")
    print("="*80 + "\n")
    
    try:
        # Obtener configuración
        config = obtener_config_google_ads()
        
        if not config:
            print("\n❌ No se pudo obtener la configuración de Google Ads.")
            return 1
        
        # Renovar token
        if renovar_token_acceso(config):
            print("\n✅ Token de acceso renovado y actualizado correctamente.")
            print("\nAhora deberías poder utilizar la API de Google Ads sin problemas.")
            print("Intenta nuevamente la función que estaba fallando.")
        else:
            print("\n❌ No se pudo renovar el token de acceso.")
            print("Revisa los mensajes de error anteriores para entender el problema.")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
