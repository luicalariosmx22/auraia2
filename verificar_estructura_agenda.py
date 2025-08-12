#!/usr/bin/env python3
"""
Script para verificar la estructura actual de las tablas de agenda
"""

from clientes.aura.utils.supabase_client import supabase

def verificar_estructura():
    """Verifica la estructura actual de las tablas"""
    print("🔍 VERIFICANDO ESTRUCTURA DE TABLAS AGENDA")
    print("=" * 50)
    
    # Verificar si agenda_eventos existe
    try:
        query_exists = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'agenda_eventos'
        );
        """
        result = supabase.rpc('execute_sql', {'query': query_exists}).execute()
        exists = result.data[0]['exists'] if result.data else False
        print(f"📋 Tabla agenda_eventos existe: {exists}")
        
        if exists:
            # Obtener estructura actual
            query_structure = """
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_name = 'agenda_eventos' 
            ORDER BY ordinal_position;
            """
            result = supabase.rpc('execute_sql', {'query': query_structure}).execute()
            
            print("\n📊 Estructura actual de agenda_eventos:")
            for col in result.data:
                print(f"  • {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
    except Exception as e:
        print(f"❌ Error verificando agenda_eventos: {e}")
    
    # Verificar si google_calendar_sync existe
    try:
        query_exists = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'google_calendar_sync'
        );
        """
        result = supabase.rpc('execute_sql', {'query': query_exists}).execute()
        exists = result.data[0]['exists'] if result.data else False
        print(f"\n📅 Tabla google_calendar_sync existe: {exists}")
        
        if exists:
            # Obtener estructura actual
            query_structure = """
            SELECT 
                column_name, 
                data_type, 
                is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'google_calendar_sync' 
            ORDER BY ordinal_position;
            """
            result = supabase.rpc('execute_sql', {'query': query_structure}).execute()
            
            print("\n📊 Estructura actual de google_calendar_sync:")
            for col in result.data:
                print(f"  • {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
                
    except Exception as e:
        print(f"❌ Error verificando google_calendar_sync: {e}")

if __name__ == "__main__":
    verificar_estructura()
