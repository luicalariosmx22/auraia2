#!/usr/bin/env python3
"""
Script para verificar qué páginas hay en la tabla facebook_paginas
"""

import os
from supabase.client import create_client, Client

def verificar_paginas_facebook():
    # Cargar variables de entorno
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Cambiado de SUPABASE_SERVICE_ROLE_KEY
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Variables de entorno de Supabase no encontradas")
        return
    
    # Crear cliente de Supabase
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        # 1. Verificar todas las páginas (activas e inactivas)
        print("🔍 Consultando TODAS las páginas de Facebook...")
        response_all = supabase.table('facebook_paginas').select('*').execute()
        all_pages = response_all.data if response_all.data else []
        
        print(f"📊 Total de páginas en la BD: {len(all_pages)}")
        
        # 2. Verificar solo páginas activas
        print("\n🔍 Consultando páginas ACTIVAS...")
        response_active = supabase.table('facebook_paginas').select('*').eq('activa', True).execute()
        active_pages = response_active.data if response_active.data else []
        
        print(f"📊 Páginas activas: {len(active_pages)}")
        
        # 3. Mostrar detalles de algunas páginas
        if all_pages:
            print("\n📋 Primeras 3 páginas encontradas:")
            for i, page in enumerate(all_pages[:3]):
                print(f"  {i+1}. {page.get('nombre_pagina', 'Sin nombre')} - Activa: {page.get('activa', False)} - Estado: {page.get('estado_webhook', 'No definido')}")
        else:
            print("\n❌ No se encontraron páginas en la tabla")
            
        # 4. Verificar estructura de la tabla
        print(f"\n🔧 Estructura de las páginas:")
        if all_pages:
            keys = list(all_pages[0].keys())
            print(f"  Campos disponibles: {keys}")
    
    except Exception as e:
        print(f"❌ Error al consultar páginas: {e}")

if __name__ == "__main__":
    verificar_paginas_facebook()
