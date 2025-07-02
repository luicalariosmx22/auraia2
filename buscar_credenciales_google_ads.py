#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para encontrar credenciales de Google Ads en todos los archivos de configuración posibles.
"""

import os
import sys
import json
import traceback
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

def buscar_credenciales():
    """Busca credenciales de Google Ads en todos los archivos de configuración posibles"""
    # Variables que buscamos
    credenciales_keys = {
        "GOOGLE_ADS_DEVELOPER_TOKEN": None,
        "GOOGLE_ADS_CLIENT_ID": None,
        "GOOGLE_ADS_CLIENT_SECRET": None,
        "GOOGLE_ADS_REFRESH_TOKEN": None,
        "GOOGLE_ADS_ACCESS_TOKEN": None,
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID": None,
        "developer_token": None,
        "client_id": None,
        "client_secret": None,
        "refresh_token": None,
        "access_token": None,
        "login_customer_id": None,
    }
    
    # Lista de posibles archivos de entorno
    env_files = [
        os.path.join(os.getcwd(), '.env'),
        os.path.join(os.getcwd(), '.env.local'),
        os.path.join(os.getcwd(), '.env.development'),
        os.path.join(os.getcwd(), '.env.production'),
        os.path.join(os.getcwd(), '.env.test')
    ]
    
    # Buscar en archivos .env
    print("\n🔍 Buscando credenciales en archivos .env...\n")
    for env_path in env_files:
        if os.path.isfile(env_path):
            print(f"ℹ️ Revisando archivo: {env_path}")
            try:
                with open(env_path, 'r', encoding='utf-8', errors='replace') as f:
                    for line in f:
                        # Ignorar comentarios y líneas vacías
                        if line.strip() and not line.strip().startswith('#'):
                            # Buscar patrones clave=valor
                            for key in credenciales_keys.keys():
                                pattern = fr'^{key}=(.+)$'
                                match = re.search(pattern, line.strip(), re.IGNORECASE)
                                if match:
                                    value = match.group(1).strip('\'"')
                                    if not credenciales_keys[key]:  # No sobrescribir
                                        credenciales_keys[key] = (value, env_path)
                                        print(f"  ✓ Encontrado {key} en {os.path.basename(env_path)}")
            except Exception as e:
                print(f"  ⚠️ Error al leer archivo {env_path}: {e}")
    
    # Posibles archivos de configuración JSON
    config_files = [
        os.path.join(os.getcwd(), 'config.json'),
        os.path.join(os.getcwd(), 'google_ads_config.json'),
        os.path.join(os.getcwd(), 'credentials.json'),
        os.path.join(os.getcwd(), 'settings.json')
    ]
    
    # Buscar en archivos de configuración JSON
    print("\n🔍 Buscando credenciales en archivos JSON...\n")
    for config_path in config_files:
        if os.path.isfile(config_path):
            print(f"ℹ️ Revisando archivo: {config_path}")
            try:
                with open(config_path, 'r', encoding='utf-8', errors='replace') as f:
                    config = json.load(f)
                    for key in credenciales_keys.keys():
                        if key in config and config[key]:
                            if not credenciales_keys[key]:  # No sobrescribir
                                credenciales_keys[key] = (config[key], config_path)
                                print(f"  ✓ Encontrado {key} en {os.path.basename(config_path)}")
            except Exception as e:
                print(f"  ⚠️ Error al leer archivo {config_path}: {e}")
    
    # Buscar en archivos Python
    print("\n🔍 Buscando credenciales en archivos Python específicos...\n")
    python_files = [
        os.path.join(os.getcwd(), 'google_ads_config.py'),
        os.path.join(os.getcwd(), 'config.py'),
        os.path.join(os.getcwd(), 'settings.py'),
        os.path.join(os.getcwd(), 'clientes', 'aura', 'services', 'google_ads_service.py'),
        os.path.join(os.getcwd(), 'clientes', 'aura', 'services', 'google_ads_service_fixed.py')
    ]
    
    for py_path in python_files:
        if os.path.isfile(py_path):
            print(f"ℹ️ Revisando archivo: {py_path}")
            try:
                with open(py_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    for key in credenciales_keys.keys():
                        # Buscar patrones como key = "valor" o key = 'valor'
                        patterns = [
                            fr'{key}\s*=\s*["\'](.+?)["\']',
                            fr'{key}\s*=\s*["\'](.+?)["\']',
                            fr'["\']?{key}["\']?\s*:\s*["\'](.+?)["\']'
                        ]
                        
                        for pattern in patterns:
                            match = re.search(pattern, content, re.IGNORECASE)
                            if match:
                                if not credenciales_keys[key]:  # No sobrescribir
                                    credenciales_keys[key] = (match.group(1), py_path)
                                    print(f"  ✓ Encontrado {key} en {os.path.basename(py_path)}")
                                break
            except Exception as e:
                print(f"  ⚠️ Error al leer archivo {py_path}: {e}")
    
    # Buscar en variables de entorno del sistema
    print("\n🔍 Verificando variables de entorno del sistema...\n")
    for key in credenciales_keys.keys():
        if key in os.environ and os.environ[key]:
            if not credenciales_keys[key]:  # No sobrescribir
                credenciales_keys[key] = (os.environ[key], "Variables de entorno")
                print(f"  ✓ Encontrado {key} en variables de entorno del sistema")
    
    return credenciales_keys

def main():
    """Función principal"""
    print("\n🚀 BÚSQUEDA DE CREDENCIALES DE GOOGLE ADS\n")
    print("="*80 + "\n")
    
    try:
        # Buscar credenciales
        credenciales = buscar_credenciales()
        
        # Mostrar resultados
        print("\n📋 RESUMEN DE CREDENCIALES ENCONTRADAS\n")
        
        for key, value in credenciales.items():
            if value:
                val, source = value
                masked_val = None
                
                # Ocultar valores sensibles
                if 'token' in key.lower() or 'secret' in key.lower():
                    if len(val) > 8:
                        masked_val = val[:4] + '*' * (len(val) - 8) + val[-4:]
                    else:
                        masked_val = '*' * len(val)
                else:
                    masked_val = val
                
                print(f"{key}: {masked_val} (fuente: {os.path.basename(source) if os.path.isfile(source) else source})")
            else:
                print(f"{key}: ❌ No encontrado")
        
        # Verificar si tenemos las credenciales mínimas necesarias
        print("\n🔍 VERIFICACIÓN DE CREDENCIALES MÍNIMAS\n")
        
        credenciales_minimas = [
            ("Client ID", credenciales["GOOGLE_ADS_CLIENT_ID"] or credenciales["client_id"]),
            ("Client Secret", credenciales["GOOGLE_ADS_CLIENT_SECRET"] or credenciales["client_secret"]),
            ("Developer Token", credenciales["GOOGLE_ADS_DEVELOPER_TOKEN"] or credenciales["developer_token"]),
            ("Refresh Token", credenciales["GOOGLE_ADS_REFRESH_TOKEN"] or credenciales["refresh_token"])
        ]
        
        todas_disponibles = True
        for nombre, valor in credenciales_minimas:
            if valor:
                print(f"✅ {nombre}: Disponible")
            else:
                print(f"❌ {nombre}: No encontrado")
                todas_disponibles = False
        
        if todas_disponibles:
            print("\n✅ Todas las credenciales mínimas están disponibles.")
            print("Puedes proceder con la renovación del token de acceso.")
        else:
            print("\n❌ Faltan algunas credenciales mínimas.")
            print("Necesitarás completar la configuración antes de poder usar la API de Google Ads.")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
