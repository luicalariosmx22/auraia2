#!/usr/bin/env python3
"""
Insertar registro de prueba para verificar estructura
"""
import sys
import os

print("🧪 PRUEBA DE INSERCIÓN")
print("=" * 30)

try:
    sys.path.append('.')
    sys.path.append(os.path.join(os.getcwd(), 'clientes', 'aura'))
    from utils.supabase_client import supabase
    print("✅ Supabase conectado")
    
    # Datos de prueba
    datos_prueba = {
        'tipo_objeto': 'test',
        'objeto_id': 'prueba_estructura_001',
        'campo': 'test_campo',
        'valor': 'test_valor',
        'timestamp': '2024-12-19T12:00:00Z'
        # NO incluimos procesado y procesado_en para ver si existen
    }
    
    print("📝 Insertando registro de prueba...")
    result = supabase.table('logs_webhooks_meta').insert(datos_prueba).execute()
    
    if result.data:
        print("✅ Inserción exitosa!")
        registro = result.data[0]
        print(f"📋 Campos en el registro: {list(registro.keys())}")
        
        # Verificar campos específicos
        if 'procesado' in registro:
            print(f"✅ procesado: {registro['procesado']}")
        else:
            print("❌ procesado: NO EXISTE")
            
        if 'procesado_en' in registro:
            print(f"✅ procesado_en: {registro['procesado_en']}")
        else:
            print("❌ procesado_en: NO EXISTE")
        
        # Limpiar - eliminar el registro de prueba
        print("🗑️ Limpiando registro de prueba...")
        supabase.table('logs_webhooks_meta').delete().eq('objeto_id', 'prueba_estructura_001').execute()
        print("✅ Limpieza completada")
        
    else:
        print("❌ Fallo en la inserción")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
