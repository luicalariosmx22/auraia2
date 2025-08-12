#!/usr/bin/env python3
"""
🚀 TEST ULTRA EFICIENTE: Actualizar registro sin cargar Flask
"""

import os
from supabase.client import create_client

# 🔗 Conexión directa a Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

print("🔄 Actualizando registro de blueprints...")

# 1. Verificar si redes_sociales ya existe
result = supabase.table('modulos_disponibles').select('*').eq('nombre', 'redes_sociales').execute()

if not result.data:
    # Crear registro para redes_sociales si no existe
    nuevo_modulo = {
        'nombre': 'redes_sociales',
        'descripcion': 'Gestión de redes sociales - Módulo principal optimizado',
        'icono': '🌐',
        'ruta': 'panel_cliente_redes_sociales.panel_cliente_redes_sociales_bp'
    }
    
    insert_result = supabase.table('modulos_disponibles').insert(nuevo_modulo).execute()
    print(f"✅ Módulo redes_sociales creado: {insert_result.data}")
else:
    # Actualizar ruta al módulo optimizado
    update_result = supabase.table('modulos_disponibles').update({
        'ruta': 'panel_cliente_redes_sociales.panel_cliente_redes_sociales_bp',
        'descripcion': 'Gestión de redes sociales - Módulo principal optimizado'
    }).eq('nombre', 'redes_sociales').execute()
    print(f"✅ Módulo redes_sociales actualizado: {update_result.data}")

print("🎉 Registro actualizado exitosamente!")
