#!/usr/bin/env python3
"""
Script para verificar la estructura usando consultas directas a Supabase
"""

from clientes.aura.utils.supabase_client import supabase

def verificar_estructura_directa():
    """Verifica la estructura usando consultas SELECT directas"""
    print("🔍 VERIFICANDO ESTRUCTURA DE TABLAS AGENDA")
    print("=" * 50)
    
    # Verificar si agenda_eventos existe y obtener algunas filas
    try:
        result = supabase.table('agenda_eventos').select('*').limit(1).execute()
        print("✅ Tabla agenda_eventos existe")
        
        if result.data:
            print("📊 Ejemplo de datos en agenda_eventos:")
            evento = result.data[0]
            print("📋 Columnas encontradas:")
            for campo in evento.keys():
                print(f"  • {campo}: {type(evento[campo]).__name__}")
        else:
            print("📋 Tabla agenda_eventos existe pero está vacía")
            
    except Exception as e:
        print(f"❌ Error con agenda_eventos: {e}")
        
        # Si la tabla no existe, intentar crearla
        if "does not exist" in str(e) or "relation" in str(e):
            print("🔨 La tabla agenda_eventos no existe, necesita ser creada")
    
    # Verificar si google_calendar_sync existe
    try:
        result = supabase.table('google_calendar_sync').select('*').limit(1).execute()
        print("\n✅ Tabla google_calendar_sync existe")
        
        if result.data:
            print("📊 Ejemplo de datos en google_calendar_sync:")
            sync = result.data[0]
            print("📋 Columnas encontradas:")
            for campo in sync.keys():
                print(f"  • {campo}: {type(sync[campo]).__name__}")
        else:
            print("📋 Tabla google_calendar_sync existe pero está vacía")
            
    except Exception as e:
        print(f"❌ Error con google_calendar_sync: {e}")
        
        if "does not exist" in str(e) or "relation" in str(e):
            print("🔨 La tabla google_calendar_sync no existe, necesita ser creada")

if __name__ == "__main__":
    verificar_estructura_directa()
