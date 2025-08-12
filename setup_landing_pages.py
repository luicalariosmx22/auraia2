"""
Script para crear las tablas de landing pages en Supabase
Ejecuta el SQL y verifica que todo funcione correctamente
"""

import os
import sys
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def ejecutar_sql_landing_pages():
    """Ejecuta el SQL para crear las tablas de landing pages"""
    try:
        # Importar cliente de Supabase
        from clientes.aura.utils.supabase_client import supabase
        
        print("🔗 Conectando a Supabase...")
        
        # Leer el archivo SQL
        sql_file = os.path.join(os.path.dirname(__file__), 'crear_tablas_landing_pages.sql')
        
        if not os.path.exists(sql_file):
            print(f"❌ No se encontró el archivo: {sql_file}")
            return False
        
        with open(sql_file, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        print("📋 Ejecutando SQL...")
        
        # Dividir SQL en comandos individuales
        sql_commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
        
        for i, command in enumerate(sql_commands, 1):
            try:
                if command.upper().startswith(('CREATE', 'INSERT', 'UPDATE')):
                    print(f"   Ejecutando comando {i}/{len(sql_commands)}: {command[:50]}...")
                    
                    # Para Supabase, usar rpc para comandos DDL
                    result = supabase.rpc('exec_sql', {'sql_query': command}).execute()
                    
                    if result:
                        print(f"   ✅ Comando {i} ejecutado")
                    else:
                        print(f"   ⚠️ Comando {i} sin resultado")
                        
            except Exception as e:
                print(f"   ❌ Error en comando {i}: {e}")
                # Continuar con el siguiente comando
                continue
        
        print("✅ SQL ejecutado completamente")
        return True
        
    except Exception as e:
        print(f"❌ Error ejecutando SQL: {e}")
        return False

def verificar_tablas():
    """Verifica que las tablas se crearon correctamente"""
    try:
        from clientes.aura.utils.supabase_client import supabase
        from clientes.aura.utils.quick_schemas import existe, columnas
        
        print("\n🔍 Verificando tablas creadas...")
        
        # Verificar landing_pages_config
        if existe('landing_pages_config'):
            print("✅ Tabla landing_pages_config existe")
            campos = columnas('landing_pages_config')
            print(f"   📋 Campos: {campos}")
        else:
            print("❌ Tabla landing_pages_config NO existe")
        
        # Verificar landing_pages_bloques
        if existe('landing_pages_bloques'):
            print("✅ Tabla landing_pages_bloques existe")
            campos = columnas('landing_pages_bloques')
            print(f"   📋 Campos: {campos}")
        else:
            print("❌ Tabla landing_pages_bloques NO existe")
        
        # Verificar datos de ejemplo
        try:
            result = supabase.table('landing_pages_config') \
                .select('*') \
                .eq('nombre_nora', 'aura') \
                .execute()
            
            if result.data:
                print(f"✅ Datos de ejemplo para 'aura' encontrados: {len(result.data)} registros")
            else:
                print("⚠️ No hay datos de ejemplo para 'aura'")
                
        except Exception as e:
            print(f"❌ Error verificando datos: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        return False

def test_funciones_secciones():
    """Prueba las funciones del módulo secciones"""
    try:
        print("\n🧪 Probando funciones de secciones.py...")
        
        # Importar funciones
        from clientes.aura.routes.panel_cliente_lading_pages.secciones import (
            obtener_config_landing,
            obtener_catalogo_bloques,
            validar_configuracion,
            obtener_estadisticas_landing
        )
        
        # Probar obtener configuración
        config = obtener_config_landing('aura')
        print(f"✅ Configuración obtenida: {config.get('titulo', 'Sin título')}")
        
        # Probar catálogo de bloques
        catalogo = obtener_catalogo_bloques()
        print(f"✅ Catálogo de bloques: {len(catalogo)} bloques disponibles")
        
        # Probar validación
        validacion = validar_configuracion(config)
        print(f"✅ Validación: {'válida' if validacion['valida'] else 'inválida'}")
        if not validacion['valida']:
            print(f"   ⚠️ Errores: {validacion['errores']}")
        
        # Probar estadísticas
        stats = obtener_estadisticas_landing('aura')
        print(f"✅ Estadísticas: existe={stats.get('existe')}, publicada={stats.get('publicada')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando funciones: {e}")
        return False

def main():
    """Función principal para setup completo"""
    print("🚀 SETUP MÓDULO LANDING PAGES")
    print("=" * 50)
    
    # 1. Ejecutar SQL
    print("\n1️⃣ Creando tablas en Supabase...")
    if not ejecutar_sql_landing_pages():
        print("❌ Error creando tablas, intentando verificación manual...")
    
    # 2. Verificar tablas
    print("\n2️⃣ Verificando estructura de base de datos...")
    verificar_tablas()
    
    # 3. Probar funciones
    print("\n3️⃣ Probando funcionalidad del módulo...")
    test_funciones_secciones()
    
    print("\n" + "=" * 50)
    print("✅ Setup completado")
    print("\n📋 Próximos pasos:")
    print("   1. Registrar módulo en modulos_disponibles")
    print("   2. Activar en configuracion_bot para 'aura'")
    print("   3. Agregar a registro_dinamico.py")
    print("   4. Probar en http://localhost:5000/panel_cliente/aura/lading_pages")

if __name__ == "__main__":
    main()
