#!/usr/bin/env python3
# clientes/aura/scripts/mostrar_contexto_bd.py

"""
Script para mostrar el contexto actual de la base de datos.
Úsalo antes de hacer preguntas a GitHub Copilot sobre BD.

Uso: python clientes/aura/scripts/mostrar_contexto_bd.py
"""

import sys
from pathlib import Path

# Agregar ruta para importaciones
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

try:
    from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
    from clientes.aura.utils.quick_schemas import tablas, columnas, info
    
    print("🗄️ CONTEXTO ACTUAL DE BASE DE DATOS SUPABASE")
    print("=" * 60)
    
    # Información general
    todas_tablas = tablas()
    print(f"📊 Total de tablas: {len(todas_tablas)}")
    print(f"📅 Última actualización: Automática cada 24h")
    
    # Tablas con más columnas (más importantes)
    print("\n📋 TABLAS PRINCIPALES (con datos):")
    print("-" * 40)
    
    tablas_con_datos = {}
    for tabla in todas_tablas:
        cols = columnas(tabla)
        if len(cols) > 1:  # Más de 1 columna = tiene estructura real
            tablas_con_datos[tabla] = len(cols)
    
    # Ordenar por número de columnas
    for tabla, num_cols in sorted(tablas_con_datos.items(), key=lambda x: x[1], reverse=True):
        print(f"  {tabla:<30} | {num_cols:>3} columnas")
    
    # Mostrar columnas de las 3 tablas más importantes
    print("\n🔍 COLUMNAS DE TABLAS MÁS USADAS:")
    print("-" * 40)
    
    tablas_importantes = ['contactos', 'clientes', 'meta_ads_cuentas']
    for tabla in tablas_importantes:
        if tabla in todas_tablas:
            cols = columnas(tabla)[:10]  # Primeras 10 columnas
            print(f"\n📋 {tabla}:")
            for i, col in enumerate(cols, 1):
                print(f"   {i:2}. {col}")
            if len(columnas(tabla)) > 10:
                print(f"   ... y {len(columnas(tabla)) - 10} más")
    
    # Tablas vacías
    tablas_vacias = [t for t in todas_tablas if len(columnas(t)) <= 1]
    if tablas_vacias:
        print(f"\n📦 TABLAS VACÍAS ({len(tablas_vacias)}):")
        print("-" * 40)
        for tabla in tablas_vacias:
            print(f"  - {tabla}")
    
    # Comando para actualizar
    print(f"\n🔄 ACTUALIZAR ESQUEMAS:")
    print("-" * 40)
    print("python clientes/aura/scripts/generar_supabase_schema.py")
    
    # Código para copiar en conversaciones
    print(f"\n📋 CÓDIGO PARA COPIAR EN CONVERSACIONES:")
    print("-" * 40)
    print("# Contexto BD para GitHub Copilot")
    print("from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS")
    print("from clientes.aura.utils.quick_schemas import existe, columnas")
    print("")
    print("# Tablas principales disponibles:")
    principales = list(sorted(tablas_con_datos.items(), key=lambda x: x[1], reverse=True)[:5])
    for tabla, num_cols in principales:
        print(f"# - {tabla} ({num_cols} columnas)")
    
    print("\n" + "=" * 60)
    print("✅ Contexto generado. Copia la info relevante en tu conversación.")
    
except ImportError as e:
    print(f"❌ Error: No se pudieron cargar los esquemas.")
    print(f"🔧 Solución: Ejecuta primero 'python clientes/aura/scripts/generar_supabase_schema.py'")
    print(f"📝 Detalle: {e}")

except Exception as e:
    print(f"❌ Error inesperado: {e}")
