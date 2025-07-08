#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para renovar el token de acceso de Google Ads usando el refresh_token 
almacenado en Supabase.

Este script:
1. Obtiene las credenciales de Google Ads desde Supabase
2. Utiliza el refresh_token para obtener un nuevo access_token
3. Actualiza la tabla google_ads_config con el nuevo access_token
"""

import os
import sys
import json
import traceback
import requests
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

def obtener_credenciales():
    """
    Obtiene las credenciales de Google Ads desde la base de datos
    """
    try:
        response = supabase.table("google_ads_config").select("*").limit(1).execute()
        
        if response.data:
            print("✅ Credenciales obtenidas correctamente de Supabase")
            return response.data[0]
        else:
            print("❌ No se encontraron credenciales en la base de datos")
            return None
    except Exception as e:
        print(f"❌ Error al obtener credenciales: {e}")
        traceback.print_exc()
        return None

def renovar_token_acceso(credenciales):
    """
    Renueva el token de acceso usando el refresh_token
    """
    # Verificar credenciales mínimas
    if not credenciales.get("client_id") or not credenciales.get("client_secret") or not credenciales.get("refresh_token"):
        print("❌ Faltan credenciales necesarias para renovar el token")
        print(f"   Client ID: {'✅' if credenciales.get('client_id') else '❌'}")
        print(f"   Client Secret: {'✅' if credenciales.get('client_secret') else '❌'}")
        print(f"   Refresh Token: {'✅' if credenciales.get('refresh_token') else '❌'}")
        return None
    
    print("\n🔄 Renovando token de acceso...")
    
    # Preparar solicitud
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": credenciales["client_id"],
        "client_secret": credenciales["client_secret"],
        "refresh_token": credenciales["refresh_token"],
        "grant_type": "refresh_token"
    }
    
    try:
        # Realizar solicitud
        response = requests.post(token_url, data=data)
        response_data = response.json()
        
        # Verificar respuesta
        if response.status_code == 200 and "access_token" in response_data:
            print("✅ Token de acceso renovado correctamente")
            return response_data
        else:
            print(f"❌ Error al renovar token: {response.status_code}")
            print(f"Respuesta: {json.dumps(response_data, indent=2)}")
            return None
    except Exception as e:
        print(f"❌ Error en la solicitud HTTP: {e}")
        traceback.print_exc()
        return None

def actualizar_token_en_bd(id_registro, token_data):
    """
    Actualiza el token de acceso en la base de datos
    """
    # Preparar datos para la actualización
    datos_actualizacion = {
        "access_token": token_data["access_token"],
        "token_type": token_data.get("token_type", "Bearer"),
        "expires_in": token_data.get("expires_in", 3600),
        "token_updated_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    
    try:
        # Actualizar registro
        response = supabase.table("google_ads_config").update(
            datos_actualizacion
        ).eq("id", id_registro).execute()
        
        if response.data:
            print("✅ Token actualizado correctamente en la base de datos")
            return True
        else:
            print("❌ Error al actualizar el token en la base de datos")
            return False
    except Exception as e:
        print(f"❌ Error al actualizar en la base de datos: {e}")
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("\n🚀 RENOVACIÓN DE TOKEN DE ACCESO DE GOOGLE ADS\n")
    print("="*80 + "\n")
    
    try:
        # Obtener credenciales de la base de datos
        print("🔍 Obteniendo credenciales desde Supabase...")
        credenciales = obtener_credenciales()
        
        if not credenciales:
            print("\n❌ No se pudieron obtener las credenciales necesarias.")
            print("Por favor, ejecuta primero:")
            print("python corregir_env_google_ads.py")
            return 1
        
        # Renovar token de acceso
        token_data = renovar_token_acceso(credenciales)
        
        if not token_data:
            print("\n❌ No se pudo renovar el token de acceso.")
            print("Verifica que el refresh_token sea válido y que las credenciales sean correctas.")
            return 1
        
        # Actualizar token en la base de datos
        actualizar_token_en_bd(credenciales["id"], token_data)
        
        print("\n✅ Proceso completado correctamente.")
        print("El token de acceso ha sido renovado y actualizado en la base de datos.")
        
        # Mostrar información del token
        token_mostrado = token_data["access_token"][:10] + "..." + token_data["access_token"][-10:]
        expiracion = token_data.get("expires_in", 3600)
        print(f"\nℹ️ Información del token:")
        print(f"Token: {token_mostrado}")
        print(f"Expira en: {expiracion} segundos ({expiracion / 60:.1f} minutos)")
        
        # Mostrar siguientes pasos
        print("\nℹ️ Siguientes pasos:")
        print("1. Verifica el funcionamiento con: python verificar_directo_google_ads.py")
        print("2. Actualiza las métricas con: python actualizar_y_verificar_google_ads.py")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
