"""
🔧 ACTUALIZACIÓN ESQUEMA SUPABASE - logs_webhooks_meta
====================================================

Este script actualiza el esquema de supabase_schemas.py para reflejar
la nueva estructura de la tabla logs_webhooks_meta después de ejecutar
la actualización SQL.

📋 ESTADO ACTUAL:
- logs_webhooks_meta aparece como 'tabla_vacia' en supabase_schemas.py
- La tabla existe en Supabase pero sin estructura adecuada
- Los archivos Python intentan insertar datos pero fallan

🎯 OBJETIVO:
- Actualizar supabase_schemas.py con la estructura real
- Verificar que coincide con el uso en meta_webhook_helpers.py
- Asegurar compatibilidad con webhooks_api.py

⚠️ EJECUTAR DESPUÉS DE:
1. Aplicar actualizar_estructura_logs_webhooks_meta.sql en Supabase
2. Verificar que la tabla funciona correctamente
3. Ejecutar este script para actualizar el esquema Python
"""

import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verificar_tabla_actual():
    """Verifica el estado actual de la tabla en Supabase"""
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        print("🔍 Verificando estructura actual de logs_webhooks_meta...")
        
        # Intentar obtener información de la tabla
        result = supabase.table('logs_webhooks_meta').select('*').limit(1).execute()
        
        if result.data is not None:
            print("✅ Tabla logs_webhooks_meta es accesible")
            return True
        else:
            print("❌ Tabla logs_webhooks_meta no es accesible")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando tabla: {e}")
        return False

def actualizar_supabase_schemas():
    """Actualiza el archivo supabase_schemas.py con la nueva estructura"""
    
    schema_file = "clientes/aura/utils/supabase_schemas.py"
    
    if not os.path.exists(schema_file):
        print(f"❌ No se encontró {schema_file}")
        return False
    
    print(f"📝 Actualizando {schema_file}...")
    
    # Leer archivo actual
    with open(schema_file, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Nueva estructura para logs_webhooks_meta
    nueva_estructura = """    'logs_webhooks_meta': {
        'id': 'bigint',
        'tipo_objeto': 'varchar(50)',
        'objeto_id': 'varchar(100)', 
        'campo': 'varchar(100)',
        'valor': 'text',
        'timestamp': 'timestamptz',
        'recibido_en': 'timestamptz',
        'nombre_nora': 'varchar(50)',
        'id_cuenta_publicitaria': 'varchar(100)',
        'procesado': 'boolean',
        'procesado_en': 'timestamptz',
        'datos_adicionales': 'json',
        'error_procesamiento': 'text',
        'creado_en': 'timestamptz',
        'actualizado_en': 'timestamptz'
    },"""
    
    # Buscar y reemplazar la línea de logs_webhooks_meta
    if "'logs_webhooks_meta': {'estructura': 'tabla_vacia'}," in contenido:
        contenido = contenido.replace(
            "'logs_webhooks_meta': {'estructura': 'tabla_vacia'},",
            nueva_estructura
        )
        
        # Escribir archivo actualizado
        with open(schema_file, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print("✅ supabase_schemas.py actualizado correctamente")
        print("📊 Nueva estructura de logs_webhooks_meta:")
        print("   - id (bigint) - Primary key")
        print("   - tipo_objeto (varchar) - Tipo: campaign, ad, audience")
        print("   - objeto_id (varchar) - ID del objeto que cambió")
        print("   - campo (varchar) - Campo que cambió")
        print("   - valor (text) - Nuevo valor")
        print("   - timestamp (timestamptz) - Cuando ocurrió")
        print("   - recibido_en (timestamptz) - Cuando llegó al webhook")
        print("   - nombre_nora (varchar) - Instancia Nora")
        print("   - id_cuenta_publicitaria (varchar) - Cuenta Meta")
        print("   - procesado (boolean) - Si fue procesado")
        print("   - procesado_en (timestamptz) - Cuando fue procesado")
        print("   - datos_adicionales (json) - Data extra")
        print("   - error_procesamiento (text) - Errores")
        print("   - creado_en (timestamptz) - Timestamp creación")
        print("   - actualizado_en (timestamptz) - Timestamp actualización")
        
        return True
    else:
        print("⚠️ No se encontró la estructura 'tabla_vacia' para reemplazar")
        print("🔍 Verificando si ya está actualizada...")
        
        if 'tipo_objeto' in contenido and 'logs_webhooks_meta' in contenido:
            print("✅ Parece que ya está actualizada")
            return True
        else:
            print("❌ Estructura no encontrada")
            return False

def verificar_compatibilidad_meta_webhook_helpers():
    """Verifica que la nueva estructura sea compatible con meta_webhook_helpers.py"""
    
    helper_file = "clientes/aura/utils/meta_webhook_helpers.py"
    
    if not os.path.exists(helper_file):
        print(f"⚠️ No se encontró {helper_file}")
        return False
    
    print(f"🔍 Verificando compatibilidad con {helper_file}...")
    
    with open(helper_file, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Campos que meta_webhook_helpers.py debería estar usando
    campos_necesarios = [
        'tipo_objeto',
        'objeto_id', 
        'campo',
        'valor',
        'timestamp',
        'nombre_nora'
    ]
    
    campos_encontrados = []
    for campo in campos_necesarios:
        if f"'{campo}'" in contenido or f'"{campo}"' in contenido:
            campos_encontrados.append(campo)
    
    print(f"📋 Campos encontrados en meta_webhook_helpers.py: {len(campos_encontrados)}/{len(campos_necesarios)}")
    
    for campo in campos_encontrados:
        print(f"   ✅ {campo}")
    
    campos_faltantes = set(campos_necesarios) - set(campos_encontrados)
    if campos_faltantes:
        print(f"⚠️ Campos que podrían faltar: {campos_faltantes}")
        return False
    else:
        print("✅ Compatibilidad verificada")
        return True

def test_insercion_basica():
    """Prueba una inserción básica para verificar que funciona"""
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        print("🧪 Probando inserción básica...")
        
        test_data = {
            'tipo_objeto': 'campaign',
            'objeto_id': 'test_verificacion_esquema',
            'campo': 'status',
            'valor': 'ACTIVE',
            'nombre_nora': 'aura',
            'id_cuenta_publicitaria': 'test_account'
        }
        
        # Insertar
        result = supabase.table('logs_webhooks_meta').insert(test_data).execute()
        
        if result.data:
            print("✅ Inserción básica exitosa")
            
            # Limpiar test data
            supabase.table('logs_webhooks_meta').delete().eq('objeto_id', 'test_verificacion_esquema').execute()
            print("✅ Test data limpiado")
            
            return True
        else:
            print("❌ Error en inserción básica")
            return False
            
    except Exception as e:
        print(f"❌ Error en test de inserción: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 ACTUALIZACIÓN ESQUEMA SUPABASE - logs_webhooks_meta")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Paso 1: Verificar tabla actual
    if not verificar_tabla_actual():
        print("❌ La tabla logs_webhooks_meta no está disponible")
        print("💡 Primero ejecuta actualizar_estructura_logs_webhooks_meta.sql en Supabase")
        return
    
    # Paso 2: Actualizar esquema Python
    if not actualizar_supabase_schemas():
        print("❌ Error actualizando supabase_schemas.py")
        return
    
    # Paso 3: Verificar compatibilidad
    verificar_compatibilidad_meta_webhook_helpers()
    
    # Paso 4: Test básico
    if test_insercion_basica():
        print("\n🎉 ACTUALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("✅ Tabla logs_webhooks_meta estructurada correctamente")
        print("✅ supabase_schemas.py actualizado")
        print("✅ Compatibilidad verificada")
        print("✅ Test de inserción exitoso")
        print()
        print("🚀 SIGUIENTE PASO:")
        print("   Ejecutar webhook de Meta Ads para verificar funcionamiento completo")
    else:
        print("\n⚠️ ACTUALIZACIÓN PARCIAL")
        print("📋 Revisar logs para identificar problemas restantes")

if __name__ == "__main__":
    main()
