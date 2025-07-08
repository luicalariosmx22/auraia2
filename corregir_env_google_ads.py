#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corregir los problemas de parsing de los archivos .env y actualizar 
las credenciales de Google Ads en Supabase.

Este script:
1. Lee los archivos .env y .env.local con manejo especial para múltiples '='
2. Extrae las credenciales de Google Ads
3. Actualiza la tabla google_ads_config en Supabase
"""

import os
import sys
import json
import traceback
import re
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

try:
    from clientes.aura.utils.supabase_client import supabase
except ImportError as e:
    print(f"❌ Error importando dependencias: {e}")
    print("Asegúrate de estar en el directorio raíz del proyecto y que las dependencias estén instaladas.")
    sys.exit(1)

def leer_env_seguro(archivo):
    """
    Lee un archivo .env y maneja correctamente líneas con múltiples signos =
    Retorna un diccionario con las variables de entorno
    """
    variables = {}
    
    try:
        with open(archivo, 'r', encoding='utf-8', errors='replace') as f:
            contenido = f.read()
            
            # Dividir por líneas
            lineas = contenido.splitlines()
            
            # Procesar cada línea
            for i, linea in enumerate(lineas, 1):
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
                    
                    variables[clave] = valor
                    print(f"  ✓ Leída variable: {clave}")
                else:
                    print(f"  ⚠️ Línea {i} con formato incorrecto: {linea}")
        
        return variables
    except Exception as e:
        print(f"  ❌ Error leyendo archivo {archivo}: {e}")
        traceback.print_exc()
        return {}

def extraer_credenciales_google_ads():
    """
    Extrae las credenciales de Google Ads de los archivos .env y .env.local
    """
    credenciales = {
        "client_id": None,
        "client_secret": None,
        "developer_token": None,
        "refresh_token": None,
        "login_customer_id": None,
    }
    
    # Mapeo de nombres de variables en .env a nombres en nuestra estructura
    mapeo_variables = {
        "GOOGLE_CLIENT_ID": "client_id",
        "GOOGLE_CLIENT_SECRET": "client_secret",
        "GOOGLE_DEVELOPER_TOKEN": "developer_token",
        "GOOGLE_REFRESH_TOKEN": "refresh_token",
        "GOOGLE_LOGIN_CUSTOMER_ID": "login_customer_id",
        # Variables alternativas que también pueden contener estos valores
        "GOOGLE_ADS_CLIENT_ID": "client_id",
        "GOOGLE_ADS_CLIENT_SECRET": "client_secret",
        "GOOGLE_ADS_DEVELOPER_TOKEN": "developer_token",
        "GOOGLE_ADS_REFRESH_TOKEN": "refresh_token",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID": "login_customer_id",
    }
    
    archivos_env = [
        os.path.join(os.getcwd(), '.env'),
        os.path.join(os.getcwd(), '.env.local'),
        os.path.join(os.getcwd(), '.env.development'),
    ]
    
    # Leer archivos .env
    for archivo in archivos_env:
        if os.path.exists(archivo):
            print(f"\n📄 Leyendo archivo: {archivo}")
            variables = leer_env_seguro(archivo)
            
            # Extraer credenciales
            for var_env, var_credencial in mapeo_variables.items():
                if var_env in variables and variables[var_env] and not credenciales[var_credencial]:
                    credenciales[var_credencial] = variables[var_env]
                    print(f"  ✓ Encontrado {var_credencial} como {var_env}")
    
    return credenciales

def verificar_tabla_google_ads():
    """
    Verifica si la tabla google_ads_config existe y si tiene registros
    Retorna el ID del primer registro o None
    """
    try:
        response = supabase.table("google_ads_config").select("id").execute()
        
        if response.data:
            print(f"✅ La tabla google_ads_config existe y tiene {len(response.data)} registros")
            return response.data[0]["id"]
        else:
            print("✅ La tabla google_ads_config existe pero no tiene registros")
            return None
            
    except Exception as e:
        error_str = str(e).lower()
        
        if "does not exist" in error_str or "42p01" in error_str:
            print("❌ La tabla google_ads_config no existe")
            print("Por favor, crea la tabla primero usando el script crear_tabla_google_ads_config.sql")
            return None
        else:
            print(f"❌ Error al verificar la tabla: {e}")
            return None

def actualizar_credenciales_en_bd(id_registro, credenciales):
    """
    Actualiza las credenciales en la base de datos
    """
    # Preparar datos para la actualización
    datos_actualizacion = {
        "updated_at": datetime.now().isoformat(),
    }
    
    # Agregar solo las credenciales que existen
    for clave, valor in credenciales.items():
        if valor:
            datos_actualizacion[clave] = valor
    
    try:
        if id_registro:
            # Actualizar registro existente
            response = supabase.table("google_ads_config").update(
                datos_actualizacion
            ).eq("id", id_registro).execute()
            
            if response.data:
                print("✅ Credenciales actualizadas correctamente")
                return True
            else:
                print("❌ Error al actualizar credenciales")
                return False
        else:
            # Crear nuevo registro
            datos_actualizacion["created_at"] = datetime.now().isoformat()
            datos_actualizacion["activo"] = True
            
            response = supabase.table("google_ads_config").insert(
                datos_actualizacion
            ).execute()
            
            if response.data:
                print("✅ Credenciales insertadas correctamente")
                return True
            else:
                print("❌ Error al insertar credenciales")
                return False
                
    except Exception as e:
        print(f"❌ Error al actualizar/insertar en la base de datos: {e}")
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("\n🚀 CORRECCIÓN DE ARCHIVOS ENV Y ACTUALIZACIÓN DE CREDENCIALES\n")
    print("="*80 + "\n")
    
    try:
        # Extraer credenciales de archivos .env
        print("🔍 Extrayendo credenciales de Google Ads de archivos .env")
        credenciales = extraer_credenciales_google_ads()
        
        # Verificar si tenemos las credenciales mínimas
        print("\n📋 VERIFICACIÓN DE CREDENCIALES EXTRAÍDAS")
        credenciales_completas = True
        
        for clave, valor in credenciales.items():
            if valor:
                # Ocultar valores sensibles en la salida
                if "token" in clave or "secret" in clave:
                    valor_mostrado = valor[:4] + "*" * (len(valor) - 8) + valor[-4:] if len(valor) > 8 else "*" * len(valor)
                else:
                    valor_mostrado = valor
                print(f"✅ {clave}: {valor_mostrado}")
            else:
                print(f"❌ {clave}: No encontrado")
                credenciales_completas = False
        
        # Verificar tabla en base de datos
        print("\n🔍 Verificando tabla en Supabase")
        id_registro = verificar_tabla_google_ads()
        
        # Actualizar credenciales en base de datos
        if credenciales_completas or input("\n¿Actualizar credenciales en la base de datos de todos modos? (s/n): ").lower() == 's':
            print("\n📝 Actualizando credenciales en la base de datos")
            actualizar_credenciales_en_bd(id_registro, credenciales)
            
            print("\n✅ Proceso completado.")
            print("\nAhora puedes renovar el token de acceso ejecutando:")
            print("python renovar_token_google_ads.py")
        else:
            print("\n⚠️ No se actualizaron las credenciales en la base de datos.")
            print("Por favor, completa las credenciales en los archivos .env y vuelve a ejecutar este script.")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
