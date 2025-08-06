#!/usr/bin/env python3
"""
🔍 Verificar estado de webhooks usando el sistema de esquemas
Siguiendo la lógica de LOGICA_SCHEMAS_PARA_COPILOT.md
"""
import sys
import os

print("🗄️ VERIFICACIÓN CON ESQUEMAS")
print("=" * 40)

try:
    # 🗄️ Contexto BD actual para GitHub Copilot
    sys.path.append('.')
    sys.path.append(os.path.join(os.getcwd(), 'clientes', 'aura'))
    
    from utils.supabase_schemas import SUPABASE_SCHEMAS
    from utils.quick_schemas import existe, columnas
    from utils.supabase_client import supabase
    
    print("✅ Sistema de esquemas cargado")
    
    # Verificar si existe la tabla logs_webhooks_meta
    if existe('logs_webhooks_meta'):
        print("✅ Tabla logs_webhooks_meta existe")
        
        # Obtener columnas reales
        columnas_reales = columnas('logs_webhooks_meta')
        print(f"📋 Columnas actuales ({len(columnas_reales)}): {columnas_reales}")
        
        # Verificar campos específicos que necesitamos
        campos_necesarios = {
            'procesado': 'boolean',
            'procesado_en': 'timestamp'
        }
        
        print("\n🔍 VERIFICACIÓN DE CAMPOS:")
        print("-" * 30)
        
        for campo, tipo in campos_necesarios.items():
            if campo in columnas_reales:
                print(f"✅ {campo}: EXISTE")
            else:
                print(f"❌ {campo}: NO EXISTE - NECESARIO AGREGARLO")
        
        # Ver esquema completo de la tabla
        if 'logs_webhooks_meta' in SUPABASE_SCHEMAS:
            esquema = SUPABASE_SCHEMAS['logs_webhooks_meta']
            print(f"\n📊 ESQUEMA COMPLETO:")
            print("-" * 30)
            for col, info in esquema.items():
                print(f"  {col}: {info.get('type', 'unknown')}")
        
        # Verificar si también existe meta_webhook_eventos (tabla que queremos eliminar)
        if existe('meta_webhook_eventos'):
            print(f"\n⚠️ TABLA DUPLICADA ENCONTRADA:")
            print(f"   meta_webhook_eventos también existe")
            columnas_meta = columnas('meta_webhook_eventos')
            print(f"   Columnas: {columnas_meta}")
            print(f"   👉 ACCIÓN: Migrar datos y eliminar esta tabla")
        else:
            print(f"\n✅ meta_webhook_eventos no existe (correcto)")
            
    else:
        print("❌ Tabla logs_webhooks_meta NO EXISTE")
        print("💡 ACCIÓN: Crear la tabla primero")
    
    print(f"\n🎯 RESUMEN:")
    print("-" * 20)
    
    if existe('logs_webhooks_meta'):
        cols = columnas('logs_webhooks_meta')
        tiene_procesado = 'procesado' in cols
        tiene_procesado_en = 'procesado_en' in cols
        
        if tiene_procesado and tiene_procesado_en:
            print("✅ TABLA LISTA - Puede ejecutar tests")
        else:
            print("⚠️ FALTAN CAMPOS - Agregar en Supabase:")
            if not tiene_procesado:
                print("   - procesado: boolean, default false")
            if not tiene_procesado_en:
                print("   - procesado_en: timestamptz, nullable")
    else:
        print("❌ TABLA NO EXISTE - Crear primero")

except ImportError as e:
    print(f"❌ Error importando esquemas: {e}")
    print("💡 Asegúrate de que existan:")
    print("   - clientes/aura/utils/supabase_schemas.py")
    print("   - clientes/aura/utils/quick_schemas.py")
    
except Exception as e:
    print(f"❌ Error general: {e}")
    import traceback
    traceback.print_exc()
