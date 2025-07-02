#!/usr/bin/env python3
"""
✅ Script para agregar columnas de ubicación a la tabla cursos
👉 Ejecuta las consultas SQL necesarias para añadir direccion y google_maps_link
"""

import os
import sys
from supabase import create_client, Client

def main():
    try:
        # Configurar Supabase
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_ANON_KEY')
        
        if not url or not key:
            print("❌ Error: Variables SUPABASE_URL y SUPABASE_ANON_KEY no configuradas")
            return False
            
        supabase: Client = create_client(url, key)
        
        print("🔄 Agregando columnas de ubicación a la tabla cursos...")
        
        # SQL para agregar las columnas
        sql_statements = [
            "ALTER TABLE cursos ADD COLUMN IF NOT EXISTS direccion TEXT DEFAULT '';",
            "ALTER TABLE cursos ADD COLUMN IF NOT EXISTS google_maps_link TEXT DEFAULT '';",
        ]
        
        # Ejecutar cada statement
        for sql in sql_statements:
            try:
                result = supabase.rpc('exec_sql', {'sql': sql}).execute()
                print(f"✅ Ejecutado: {sql}")
            except Exception as e:
                print(f"⚠️  Error ejecutando: {sql}")
                print(f"   Detalle: {e}")
                # Continuar con el siguiente statement
        
        # Verificar que las columnas existen
        print("\n🔍 Verificando columnas...")
        try:
            # Intentar hacer una consulta que incluya las nuevas columnas
            test_query = supabase.table('cursos').select('id, direccion, google_maps_link').limit(1).execute()
            print("✅ Columnas 'direccion' y 'google_maps_link' agregadas exitosamente")
            return True
        except Exception as e:
            print(f"❌ Error verificando columnas: {e}")
            print("\n📋 Ejecuta manualmente en Supabase SQL Editor:")
            print("ALTER TABLE cursos ADD COLUMN IF NOT EXISTS direccion TEXT DEFAULT '';")
            print("ALTER TABLE cursos ADD COLUMN IF NOT EXISTS google_maps_link TEXT DEFAULT '';")
            return False
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 ¡Migración completada! Ahora puedes editar cursos con ubicación.")
    else:
        print("\n⚠️  La migración falló. Revisa los mensajes de error.")
    sys.exit(0 if success else 1)
