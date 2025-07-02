#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script simplificado para configurar Google Ads en Supabase

Versión simplificada para evitar problemas de codificación en Windows
"""

import os
import sys
import json
from datetime import datetime
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

def configurar_credenciales_ejemplo():
    """Configura credenciales de ejemplo en la tabla google_ads_config"""
    print("\n🔑 Configurando credenciales de ejemplo para Google Ads\n")
    
    # Credenciales de ejemplo
    credenciales = {
        "client_id": "XXXXX-XXXXX.apps.googleusercontent.com",
        "client_secret": "GOCSPX-ejemplo-client-secret",
        "developer_token": "ejemplo-developer-token",
        "login_customer_id": "123-456-7890",
        "developer_token_valid": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    try:
        # Verificar si ya existen registros
        response = supabase.table("google_ads_config").select("*").execute()
        
        if response.data:
            print(f"ℹ️ Ya existen {len(response.data)} registros de configuración.")
            print("✅ No es necesario crear un registro de ejemplo.")
            return True
        
        # Insertar credenciales de ejemplo
        print("📝 Insertando credenciales de ejemplo...")
        response = supabase.table("google_ads_config").insert(credenciales).execute()
        
        if response.data:
            print("✅ Credenciales de ejemplo guardadas correctamente.")
            return True
        else:
            print("⚠️ La operación se completó pero no se recibió confirmación.")
            return True
    
    except Exception as e:
        print(f"❌ Error al configurar credenciales: {e}")
        print("\nDetalles del error:")
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("\n🚀 CONFIGURACIÓN SIMPLIFICADA DE GOOGLE ADS EN SUPABASE 🚀\n")
    print("="*80 + "\n")
    
    try:
        print("Este script verificará y configurará credenciales de ejemplo para Google Ads.")
        print("NOTA: Las credenciales de ejemplo NO son válidas y deben ser reemplazadas con tus propias credenciales.")
        
        # Configurar credenciales
        if not configurar_credenciales_ejemplo():
            print("❌ No se pudieron configurar las credenciales.")
            return 1
        
        print("\n✅ Configuración completada.")
        print("\nPróximos pasos:")
        print("1. Verifica las credenciales con: python verificar_google_ads_config.py")
        print("2. Actualiza las credenciales en Supabase con tus propios valores")
        print("3. Obtén un token de acceso con: python renovar_token_google_ads.py --renew-token")
        
        print("\n" + "="*80 + "\n")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error inesperado en el script: {e}")
        print("\nDetalles del error:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
