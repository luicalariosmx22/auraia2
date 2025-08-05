#!/usr/bin/env python3
"""
Script para crear las tablas de automatización de campañas en Supabase
"""
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from clientes.aura.utils.supabase_client import supabase

def ejecutar_sql_desde_archivo(archivo_sql):
    """
    Ejecuta un archivo SQL en Supabase
    """
    try:
        # Leer archivo SQL
        with open(archivo_sql, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print(f"📄 Ejecutando SQL desde: {archivo_sql}")
        
        # Dividir por declaraciones (por punto y coma)
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        print(f"🔧 Encontradas {len(statements)} declaraciones SQL")
        
        for i, statement in enumerate(statements, 1):
            try:
                if statement.upper().startswith(('CREATE', 'ALTER', 'INSERT', 'UPDATE', 'DELETE', 'COMMENT')):
                    print(f"   ⚡ Ejecutando declaración {i}/{len(statements)}")
                    
                    # Ejecutar usando la función RPC de Supabase para SQL raw
                    resultado = supabase.rpc('execute_sql', {'sql_query': statement}).execute()
                    
                    print(f"   ✅ Declaración {i} ejecutada exitosamente")
                else:
                    print(f"   ⏭️ Saltando declaración {i} (no es DDL/DML)")
                    
            except Exception as e:
                print(f"   ❌ Error en declaración {i}: {e}")
                # Continuar con la siguiente declaración
                continue
        
        print(f"✅ Archivo SQL {archivo_sql} procesado completamente")
        return True
        
    except Exception as e:
        print(f"❌ Error ejecutando archivo SQL {archivo_sql}: {e}")
        return False

def crear_tablas_automatizacion():
    """
    Crea las tablas necesarias para la automatización de campañas
    """
    print("🚀 Iniciando creación de tablas para automatización de campañas")
    
    # Ruta al archivo SQL
    sql_file = Path(__file__).parent / 'sql' / 'crear_tablas_automatizacion_campanas.sql'
    
    if not sql_file.exists():
        print(f"❌ Archivo SQL no encontrado: {sql_file}")
        return False
    
    return ejecutar_sql_desde_archivo(sql_file)

def verificar_tablas_creadas():
    """
    Verifica que las tablas se hayan creado correctamente
    """
    print("🔍 Verificando tablas creadas...")
    
    tablas_esperadas = [
        'meta_ads_automatizaciones',
        'meta_publicaciones_webhook', 
        'meta_anuncios_automatizados',
        'meta_paginas_webhook',
        'meta_plantillas_anuncios'
    ]
    
    tablas_verificadas = 0
    
    for tabla in tablas_esperadas:
        try:
            # Intentar hacer una consulta simple para verificar que la tabla existe
            resultado = supabase.table(tabla).select('*').limit(1).execute()
            print(f"   ✅ Tabla '{tabla}' verificada")
            tablas_verificadas += 1
        except Exception as e:
            print(f"   ❌ Error verificando tabla '{tabla}': {e}")
    
    print(f"📊 Verificación completada: {tablas_verificadas}/{len(tablas_esperadas)} tablas")
    return tablas_verificadas == len(tablas_esperadas)

def insertar_datos_ejemplo():
    """
    Inserta algunos datos de ejemplo para pruebas
    """
    print("💾 Insertando datos de ejemplo...")
    
    try:
        # Ejemplo de plantilla de anuncio
        plantilla_ejemplo = {
            'nombre_nora': 'nora_default',
            'nombre': 'Plantilla Promociones',
            'descripcion': 'Plantilla automática para promociones',
            'plantilla_json': {
                'headline': '🎉 Oferta Especial',
                'description': 'No te pierdas esta increíble oportunidad',
                'call_to_action': 'SHOP_NOW',
                'texto_personalizado': 'Aprovecha nuestras promociones exclusivas'
            },
            'activa': True
        }
        
        resultado = supabase.table('meta_plantillas_anuncios').insert(plantilla_ejemplo).execute()
        
        if resultado.data:
            print("   ✅ Plantilla de ejemplo insertada")
        else:
            print("   ⚠️ No se pudo insertar plantilla de ejemplo")
            
    except Exception as e:
        print(f"   ❌ Error insertando datos de ejemplo: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 CONFIGURACIÓN DE AUTOMATIZACIÓN DE CAMPAÑAS META ADS")
    print("=" * 60)
    
    # Paso 1: Crear tablas
    if crear_tablas_automatizacion():
        print("\n✅ Tablas creadas exitosamente")
        
        # Paso 2: Verificar tablas
        if verificar_tablas_creadas():
            print("\n✅ Todas las tablas verificadas correctamente")
            
            # Paso 3: Insertar datos de ejemplo
            insertar_datos_ejemplo()
            
            print("\n🎉 ¡Configuración completada exitosamente!")
            print("\n📋 Próximos pasos:")
            print("   1. Configurar webhook de Meta para eventos 'feed'")
            print("   2. Obtener Page Access Token para las páginas")
            print("   3. Crear primera automatización desde el panel")
            print("   4. Probar con publicación de prueba")
            
        else:
            print("\n❌ Error verificando tablas")
            sys.exit(1)
    else:
        print("\n❌ Error creando tablas")
        sys.exit(1)
    
    print("\n" + "=" * 60)
