#!/usr/bin/env python3
"""
🔍 VERIFICAR SCHEMA: Columnas reales de facebook_paginas
"""

import os
from supabase.client import create_client

# 🔗 Conexión directa a Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# 📊 Verificar estructura real de la tabla
result = supabase.table('facebook_paginas').select('*').eq('page_id', '782681001814242').limit(1).execute()

if result.data:
    columnas = list(result.data[0].keys())
    print("📋 Columnas disponibles en facebook_paginas:")
    for col in sorted(columnas):
        print(f"  • {col}")
        
    # 🔍 Verificar columnas específicas
    registro = result.data[0]
    print(f"\n📄 Estado actual página 782681001814242:")
    print(f"  • webhook_activo: {registro.get('webhook_activo', 'NO EXISTE')}")
    print(f"  • estado_webhook: {registro.get('estado_webhook', 'NO EXISTE')}")  
    print(f"  • access_token: {'PRESENTE' if registro.get('access_token') else 'NULL'}")
else:
    print("⚠️ No se encontró la página 782681001814242")
