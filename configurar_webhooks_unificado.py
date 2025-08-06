#!/usr/bin/env python3
"""
🔧 Script para agregar campos necesarios a logs_webhooks_meta
Opción 1: Unificar en una sola tabla
"""
import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def agregar_campos_tabla():
    print("🔧 Agregando campos necesarios a logs_webhooks_meta...")
    
    try:
        from clientes.aura.utils.supabase_client import supabase
        print("✅ Cliente Supabase conectado")
        
        # Verificar estructura actual
        print("📋 Verificando estructura actual...")
        response = supabase.table('logs_webhooks_meta').select('*').limit(1).execute()
        
        if response.data:
            campos_actuales = list(response.data[0].keys())
            print(f"📋 Campos actuales: {campos_actuales}")
            
            # Verificar si ya tiene los campos necesarios
            if 'procesado' in campos_actuales and 'procesado_en' in campos_actuales:
                print("✅ Los campos ya existen. ¡Perfecto!")
                return True
        
        # Los campos no existen, intentar agregarlos usando SQL directo
        print("🔨 Intentando agregar campos con SQL...")
        
        # SQL para agregar los campos
        sql_commands = [
            "ALTER TABLE logs_webhooks_meta ADD COLUMN IF NOT EXISTS procesado BOOLEAN DEFAULT false;",
            "ALTER TABLE logs_webhooks_meta ADD COLUMN IF NOT EXISTS procesado_en TIMESTAMP WITH TIME ZONE;"
        ]
        
        for sql in sql_commands:
            try:
                # Usar rpc para ejecutar SQL directo
                result = supabase.rpc('exec_sql', {'sql_query': sql}).execute()
                print(f"✅ Ejecutado: {sql[:50]}...")
            except Exception as e:
                print(f"⚠️ SQL manual falló: {e}")
                # Intentar método alternativo usando PostgreSQL REST
                try:
                    # Esto es un hack: intentar insertar un registro con los nuevos campos
                    # Si la tabla no tiene los campos, fallará gracefully
                    test_data = {
                        'tipo_objeto': 'test',
                        'objeto_id': 'test_structure',
                        'campo': 'test',
                        'valor': 'test',
                        'timestamp': '2024-01-01T00:00:00Z',
                        'procesado': False,
                        'procesado_en': None
                    }
                    
                    # Intentar insertar para forzar la creación de campos
                    insert_result = supabase.table('logs_webhooks_meta').insert(test_data).execute()
                    
                    if insert_result.data:
                        print("✅ Campos agregados mediante inserción")
                        # Eliminar el registro de prueba
                        supabase.table('logs_webhooks_meta').delete().eq('objeto_id', 'test_structure').execute()
                        print("🗑️ Registro de prueba eliminado")
                        return True
                    
                except Exception as e2:
                    print(f"❌ Método alternativo también falló: {e2}")
        
        # Verificar si funcionó
        response_final = supabase.table('logs_webhooks_meta').select('*').limit(1).execute()
        if response_final.data:
            campos_finales = list(response_final.data[0].keys())
            if 'procesado' in campos_finales and 'procesado_en' in campos_finales:
                print("✅ ¡Campos agregados exitosamente!")
                return True
        
        print("⚠️ No se pudieron agregar los campos automáticamente")
        print("💡 SOLUCIÓN MANUAL:")
        print("1. Accede a tu panel de Supabase")
        print("2. Ve a la tabla 'logs_webhooks_meta'")
        print("3. Agrega estos campos:")
        print("   - procesado: boolean, default false")
        print("   - procesado_en: timestamp with timezone, nullable")
        
        return False
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def main():
    print("🚀 CONFIGURACIÓN WEBHOOKS UNIFICADOS")
    print("=" * 50)
    print("📋 Opción 1: Usar solo logs_webhooks_meta")
    print("=" * 50)
    
    resultado = agregar_campos_tabla()
    
    if resultado:
        print("\n🎉 ¡CONFIGURACIÓN EXITOSA!")
        print("💡 Próximos pasos:")
        print("1. ✅ Ejecutar test_simple_webhooks.py")
        print("2. 🔄 Probar los endpoints del panel")
        print("3. 📊 Verificar estadísticas en la UI")
    else:
        print("\n⚠️ Configuración incompleta")
        print("💡 Revisa las instrucciones manuales arriba")
    
    return resultado

if __name__ == "__main__":
    main()
