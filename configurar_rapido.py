#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificación rápida y configuración de ejemplo para Google Ads API
Este script:
1. Verifica que la tabla google_ads_config existe
2. Inserta una configuración de ejemplo si no hay registros
3. Muestra los pasos siguientes para completar la integración
"""

import os
import sys
import json
import traceback
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

# Configuración de ejemplo
CONFIG_EJEMPLO = {
    "client_id": "ejemplo-client-id.apps.googleusercontent.com",
    "client_secret": "GOCSPX-ejemplo-client-secret",
    "developer_token": "ejemplo-developer-token",
    "login_customer_id": "1234567890",
    "developer_token_valid": True,
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat()
}

def verificar_tabla():
    """Verifica si la tabla existe y contiene registros"""
    print("\n🔍 Verificando tabla google_ads_config...\n")
    
    try:
        # Intentar seleccionar registros
        response = supabase.table("google_ads_config").select("id").execute()
        
        if response.data:
            print(f"✅ La tabla existe y contiene {len(response.data)} registros.")
            return True
        else:
            print("✅ La tabla existe pero no contiene registros.")
            return False
    
    except Exception as e:
        error_str = str(e).lower()
        
        if "does not exist" in error_str or "42p01" in error_str:
            print("❌ La tabla no existe.")
            return None
        else:
            print(f"❌ Error verificando la tabla: {e}")
            return None

def insertar_configuracion_ejemplo():
    """Inserta una configuración de ejemplo en la tabla"""
    print("\n📝 Insertando configuración de ejemplo...\n")
    
    try:
        # Insertar datos
        response = supabase.table("google_ads_config").insert(CONFIG_EJEMPLO).execute()
        
        if response.data:
            print("✅ Configuración de ejemplo insertada correctamente.")
            return True
        else:
            print("❌ Error al insertar la configuración de ejemplo.")
            return False
    
    except Exception as e:
        print(f"❌ Error al insertar la configuración: {e}")
        return False

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

def mostrar_instrucciones():
    """Muestra instrucciones para continuar con la integración"""
    print("\n📋 INSTRUCCIONES PARA CONTINUAR\n")
    
    print("""
1. Ahora que la tabla está creada y contiene una configuración de ejemplo,
   debes actualizar estos datos con tus credenciales reales de Google Ads API.

2. Para obtener estas credenciales necesitarás:
   - Un proyecto en Google Cloud Platform con OAuth configurado
   - Un Developer Token de Google Ads
   - Una cuenta de Google Ads con acceso de administrador

3. Una vez que tengas estas credenciales, puedes:
   a) Actualizar manualmente la tabla en Supabase, o
   b) Ejecutar: python configurar_google_ads.py

4. Después de actualizar las credenciales, obtén un token de acceso con:
   python renovar_token_google_ads.py --renew-token

5. Finalmente, verifica que todo funciona correctamente con:
   python diagnostico_token_google_ads.py
""")

def main():
    """Función principal"""
    print("\n🚀 VERIFICACIÓN RÁPIDA Y CONFIGURACIÓN GOOGLE ADS\n")
    print("="*80 + "\n")
    
    try:
        # Verificar si la tabla existe y tiene registros
        resultado = verificar_tabla()
        
        if resultado is None:
            print("\n❌ No se pudo verificar la tabla. Por favor, crea la tabla manualmente.")
            print("Usa el script SQL: scripts/crear_tabla_google_ads_config.sql")
            return 1
        elif resultado is False:
            # Tabla existe pero sin registros
            print("\nℹ️ La tabla existe pero no contiene registros.")
            respuesta = input_seguro("¿Deseas insertar una configuración de ejemplo? (s/n): ")
            
            if respuesta.lower() == 's':
                insertar_configuracion_ejemplo()
        else:
            # Tabla existe con registros
            print("\nℹ️ La tabla ya contiene registros de configuración.")
        
        # Mostrar instrucciones
        mostrar_instrucciones()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
