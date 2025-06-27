#!/usr/bin/env python3
"""
Script simple para verificar la estructura de configuracion_bot
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables de entorno
load_dotenv()

# Configurar Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Variables de entorno SUPABASE_URL o SUPABASE_KEY no encontradas")
    exit(1)

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("🔍 Verificando tabla configuracion_bot...")
    
    # Obtener todas las configuraciones
    response = supabase.table("configuracion_bot").select("*").execute()
    
    if response.data:
        print(f"✅ Encontradas {len(response.data)} configuraciones")
        config = response.data[0]
        print(f"📋 Campos disponibles: {list(config.keys())}")
        print(f"🤖 Primera configuración: {config.get('nombre_nora', 'N/A')}")
        
        # Verificar si existen los campos necesarios
        tiene_modo = 'modo_respuesta' in config
        tiene_mensaje = 'mensaje_fuera_tema' in config
        
        print(f"✅ Campo 'modo_respuesta': {'Sí' if tiene_modo else 'No'}")
        print(f"✅ Campo 'mensaje_fuera_tema': {'Sí' if tiene_mensaje else 'No'}")
        
        if not tiene_modo or not tiene_mensaje:
            print("\n⚠️ Campos faltantes detectados")
            print("💡 Será necesario agregar estas columnas a la tabla")
    else:
        print("⚠️ No se encontraron configuraciones en la tabla")
        
except Exception as e:
    print(f"❌ Error: {e}")
