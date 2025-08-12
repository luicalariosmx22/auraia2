#!/usr/bin/env python3
"""
🔧 CORREGIR: Actualizar ruta del módulo redes_sociales
"""

import os
from supabase.client import create_client

# 🔗 Conexión directa
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY") 
supabase = create_client(url, key)

print("🔧 Corrigiendo ruta del módulo redes_sociales...")

# Actualizar la ruta correcta
result = supabase.table('modulos_disponibles').update({
    'ruta': 'panel_cliente_redes_sociales.panel_cliente_redes_sociales_bp',
    'descripcion': 'Gestión de redes sociales - Módulo principal optimizado'
}).eq('nombre', 'redes_sociales').execute()

print(f"✅ Ruta corregida: {result.data}")

# Verificar que no exista facebook_detalle duplicado
detalle_check = supabase.table('modulos_disponibles').select('*').eq('nombre', 'facebook_detalle').execute()

if detalle_check.data:
    print("⚠️ facebook_detalle ya existe - eliminando duplicado...")
    supabase.table('modulos_disponibles').delete().eq('nombre', 'facebook_detalle').execute()
    print("✅ Duplicado eliminado")
else:
    print("✅ No hay duplicados de facebook_detalle")

print("\n🎯 Corrección completada! El módulo debería funcionar correctamente ahora.")
