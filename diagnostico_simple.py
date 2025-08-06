#!/usr/bin/env python3
"""
Script simple para diagnosticar el estado actual
"""
import sys
import os

print("🔍 DIAGNÓSTICO WEBHOOKS")
print("=" * 30)

# Verificar path
print(f"📁 Working directory: {os.getcwd()}")
print(f"🐍 Python path: {sys.executable}")

# Intentar importar supabase
try:
    sys.path.append('.')
    # Agregar ruta específica al path
    sys.path.append(os.path.join(os.getcwd(), 'clientes', 'aura'))
    from utils.supabase_client import supabase
    print("✅ Supabase importado correctamente")
    
    # Verificar conexión básica
    result = supabase.table('logs_webhooks_meta').select('*').limit(1).execute()
    
    if result.data:
        print(f"✅ Tabla accesible - {len(result.data)} registros encontrados")
        campos = list(result.data[0].keys())
        print(f"📋 Campos: {campos}")
        
        # Verificar campos específicos
        campos_necesarios = ['procesado', 'procesado_en']
        for campo in campos_necesarios:
            if campo in campos:
                print(f"✅ {campo}: EXISTE")
            else:
                print(f"❌ {campo}: NO EXISTE")
    else:
        print("⚠️ Tabla sin datos - no se pueden verificar campos")
        
except ImportError as e:
    print(f"❌ Error de importación: {e}")
except Exception as e:
    print(f"❌ Error general: {e}")

print("\n🎯 SIGUIENTE PASO:")
if 'procesado' not in locals() or 'procesado_en' not in locals():
    print("📝 Necesitas agregar campos manualmente en Supabase:")
    print("   1. Abre el panel de Supabase")
    print("   2. Ve a Table Editor > logs_webhooks_meta")
    print("   3. Agrega: procesado (boolean, default false)")
    print("   4. Agrega: procesado_en (timestamptz, nullable)")
else:
    print("✅ Tabla lista - puedes ejecutar los tests")
