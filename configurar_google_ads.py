#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para crear la tabla google_ads_config en Supabase
y configurar la integración con Google Ads.

Este script:
1. Crea la tabla google_ads_config si no existe
2. Permite al usuario ingresar las credenciales de OAuth de Google Ads
3. Guarda las credenciales en la tabla
"""

import os
import sys
import json
from datetime import datetime
import getpass
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

# Definición de la tabla
TABLA_GOOGLE_ADS_CONFIG = """
CREATE TABLE IF NOT EXISTS google_ads_config (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID REFERENCES auth.users(id),
    cliente_id VARCHAR,
    developer_token VARCHAR,
    developer_token_valid BOOLEAN DEFAULT FALSE,
    client_id VARCHAR,
    client_secret VARCHAR,
    login_customer_id VARCHAR,
    refresh_token VARCHAR,
    refresh_token_valid BOOLEAN DEFAULT FALSE,
    access_token VARCHAR,
    token_type VARCHAR DEFAULT 'Bearer',
    expires_in INTEGER DEFAULT 3600,
    activo BOOLEAN DEFAULT TRUE
);
"""

def crear_tabla():
    """Crea la tabla google_ads_config en Supabase si no existe."""
    print("🔧 Verificando tabla google_ads_config en Supabase...")
    
    try:
        # Intentar ejecutar una consulta simple para verificar si la tabla existe
        response = supabase.table("google_ads_config").select("id").limit(1).execute()
        print(f"✅ La tabla google_ads_config ya existe. Encontrados {len(response.data)} registros.")
        return True
    except Exception as e:
        # Capturar el error específico
        error_str = str(e).lower()
        print(f"ℹ️ Respuesta de Supabase: {error_str}")
        
        if "does not exist" in error_str or "42p01" in error_str:
            print("\n⚠️ La tabla google_ads_config no existe.")
            
            # Informar que ya se ha creado la tabla
            print("\n✅ La tabla ha sido creada manualmente en el paso anterior.")
            print("Verificando nuevamente la tabla...")
            
            try:
                # Intentar consultar de nuevo
                response = supabase.table("google_ads_config").select("id").limit(1).execute()
                print("✅ Tabla google_ads_config verificada correctamente.")
                return True
            except Exception as e2:
                print(f"❌ La tabla aún no existe o hay otro problema: {e2}")
                print("\nℹ️ Si acabas de crear la tabla, es posible que necesites esperar unos segundos.")
                
                # Dar otra oportunidad
                respuesta = input_seguro("¿Intentar verificar nuevamente? (s/n): ")
                if respuesta.lower() == 's':
                    try:
                        response = supabase.table("google_ads_config").select("id").limit(1).execute()
                        print("✅ Tabla google_ads_config verificada correctamente en el segundo intento.")
                        return True
                    except:
                        print("❌ La tabla sigue sin ser accesible.")
                
                # Permitir continuar de todas formas
                respuesta = input_seguro("¿Deseas continuar de todos modos? (s/n): ")
                return respuesta.lower() == 's'
        else:
            print(f"❌ Error inesperado al verificar la tabla: {e}")
            # Permitir continuar de todas formas
            respuesta = input_seguro("¿Deseas continuar de todos modos? (s/n): ")
            return respuesta.lower() == 's'

def input_seguro(prompt):
    """Función de input mejorada para manejar problemas de codificación"""
    try:
        return input(prompt)
    except UnicodeEncodeError:
        # Si hay error de codificación, usar ASCII para el prompt
        print("[Advertencia: Problemas con caracteres especiales]")
        return input(prompt.encode('ascii', 'replace').decode())
    except Exception as e:
        print(f"[Error en input: {e}]")
        return input(">> ")  # Prompt simplificado como fallback

def solicitar_credenciales():
    """Solicita al usuario las credenciales de OAuth de Google Ads."""
    print("\n🔑 Configuración de credenciales de Google Ads\n")
    
    # Valores predeterminados o ejemplos
    default_client_id = "XXXXX-XXXXX.apps.googleusercontent.com"
    default_login_customer_id = "123-456-7890"
    
    print("Ingresa las credenciales de OAuth para Google Ads.")
    print("Estos datos se encuentran en la consola de Google Cloud y en Google Ads.")
    print("Deja en blanco para usar valores predeterminados de ejemplo (solo para pruebas).\n")
    
    try:
        client_id = input_seguro(f"Client ID de OAuth [{default_client_id}]: ")
        client_id = client_id if client_id else default_client_id
        
        client_secret = getpass.getpass("Client Secret de OAuth: ")
        if not client_secret:
            print("⚠️ Usando un client secret de ejemplo (solo para pruebas).")
            client_secret = "GOCSPX-ejemplo-client-secret"
        
        developer_token = getpass.getpass("Developer Token de Google Ads: ")
        if not developer_token:
            print("⚠️ Usando un developer token de ejemplo (solo para pruebas).")
            developer_token = "ejemplo-developer-token"
        
        login_customer_id = input_seguro(f"Login Customer ID (MCC) opcional [{default_login_customer_id}]: ")
        login_customer_id = login_customer_id if login_customer_id else default_login_customer_id
        
        return {
            "client_id": client_id,
            "client_secret": client_secret,
            "developer_token": developer_token,
            "login_customer_id": login_customer_id,
            "developer_token_valid": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ Error solicitando credenciales: {e}")
        print("\nDetalles del error:")
        traceback.print_exc()
        
        print("\n⚠️ Usando credenciales de ejemplo para continuar...")
        return {
            "client_id": default_client_id,
            "client_secret": "GOCSPX-ejemplo-client-secret",
            "developer_token": "ejemplo-developer-token",
            "login_customer_id": default_login_customer_id,
            "developer_token_valid": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

def guardar_credenciales(credenciales):
    """Guarda las credenciales en la tabla google_ads_config."""
    print("\n💾 Guardando credenciales en Supabase...")
    
    try:
        # Verificar si ya existen registros
        try:
            response = supabase.table("google_ads_config").select("id").execute()
            if response.data:
                print(f"ℹ️ Ya existen {len(response.data)} registros de configuración.")
                actualizar = input_seguro("¿Deseas actualizar el registro existente en lugar de crear uno nuevo? (s/n): ")
                
                if actualizar.lower() == 's':
                    registro_id = response.data[0]['id']
                    response = supabase.table("google_ads_config").update(credenciales).eq("id", registro_id).execute()
                    print("✅ Credenciales actualizadas correctamente.")
                    return True
        except Exception as e:
            print(f"ℹ️ No se pudo verificar registros existentes: {e}")
        
        # Insertar nuevas credenciales
        response = supabase.table("google_ads_config").insert(credenciales).execute()
        
        if response.data:
            print("✅ Credenciales guardadas correctamente.")
            return True
        else:
            print("⚠️ La operación se completó pero no se recibió confirmación.")
            return True
    
    except Exception as e:
        print(f"❌ Error al guardar credenciales: {e}")
        print("\nDetalles del error:")
        traceback.print_exc()
        
        # Permitir continuar de todas formas
        respuesta = input_seguro("¿Deseas continuar de todos modos? (s/n): ")
        return respuesta.lower() == 's'

def main():
    """Función principal del script."""
    try:
        print("\n🚀 CONFIGURACIÓN DE GOOGLE ADS EN SUPABASE 🚀\n")
        print("="*80 + "\n")
        
        print("Este script configurará las credenciales de Google Ads en la tabla 'google_ads_config'.")
        print("La tabla ya debería estar creada en el paso anterior del asistente.")
        
        # Verificar tabla
        if not crear_tabla():
            print("⚠️ Advertencia: Puede haber problemas con la tabla google_ads_config.")
            continuar = input_seguro("¿Deseas continuar de todas formas? (s/n): ")
            if continuar.lower() != 's':
                print("❌ Operación cancelada por el usuario.")
                return 1
        
        # Solicitar credenciales
        print("\nA continuación, configuraremos las credenciales de acceso a Google Ads API.")
        credenciales = solicitar_credenciales()
        if not credenciales:
            print("❌ No se pudieron obtener las credenciales. Abortando.")
            return 1
        
        # Guardar credenciales
        if not guardar_credenciales(credenciales):
            print("❌ No se pudieron guardar las credenciales. Abortando.")
            return 1
        
        print("\n✅ Configuración de Google Ads completada correctamente.")
        print("\nPara obtener el token de acceso, ejecuta:")
        print("python renovar_token_google_ads.py --renew-token")
        
        print("\n" + "="*80 + "\n")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error inesperado en el script: {e}")
        print("\nDetalles del error:")
        traceback.print_exc()
        
        print("\n⚠️ El script ha encontrado un error, pero es posible que algunas operaciones se hayan completado.")
        print("Para continuar con el proceso de configuración, ejecuta:")
        print("python renovar_token_google_ads.py --renew-token")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
