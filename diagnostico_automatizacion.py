#!/usr/bin/env python3
"""
Diagnóstico rápido de automatización Meta Ads
"""

import sys
sys.path.append('.')

from clientes.aura.utils.supabase_client import supabase

def diagnosticar_automatizacion():
    print("🔍 Diagnosticando automatización Meta Ads...")
    
    # Buscar la automatización
    result = supabase.table('automatizaciones').select('*').ilike('nombre', '%Meta Ads - Reportes Semanales%').execute()
    
    if not result.data:
        print("❌ No se encontró la automatización")
        return
    
    auto = result.data[0]
    print(f"\n📋 Automatización encontrada: {auto['nombre']}")
    print("🔍 Campos relevantes para ejecución:")
    print(f"   modulo_relacionado: '{auto.get('modulo_relacionado', 'NO DEFINIDO')}'")
    print(f"   funcion_objetivo: '{auto.get('funcion_objetivo', 'NO DEFINIDO')}'")
    print(f"   parametros_json: {auto.get('parametros_json', 'NO DEFINIDO')}")
    print(f"   activo: {auto.get('activo', 'NO DEFINIDO')}")
    
    # Verificar si los campos están vacíos o nulos
    if not auto.get('modulo_relacionado'):
        print("❌ modulo_relacionado está vacío o nulo")
    if not auto.get('funcion_objetivo'):
        print("❌ funcion_objetivo está vacío o nulo")
    
    print("\n📋 TODOS LOS CAMPOS:")
    for key, value in auto.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    diagnosticar_automatizacion()
