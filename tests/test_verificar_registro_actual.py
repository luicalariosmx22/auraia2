#!/usr/bin/env python3
"""
🚀 TEST ULTRA EFICIENTE: Verificar registro de blueprints separados
"""

import os
from supabase.client import create_client

# 🔗 Conexión directa
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY") 
supabase = create_client(url, key)

print("🔍 Verificando estado actual del registro...")

# 1. Ver módulos disponibles
modulos = supabase.table('modulos_disponibles').select('nombre, descripcion, ruta').execute()

print("\n📋 Módulos registrados:")
for mod in modulos.data:
    print(f"  • {mod['nombre']}: {mod['ruta']}")

# 2. Ver configuración de aura
config = supabase.table('configuracion_bot').select('modulos').eq('nombre_nora', 'aura').execute()

if config.data:
    modulos_activos = config.data[0].get('modulos', {})
    print(f"\n✅ Módulos activos para aura: {list(modulos_activos.keys())}")

print("\n🎯 ¡Verificación completa!")
