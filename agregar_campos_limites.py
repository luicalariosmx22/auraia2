#!/usr/bin/env python3
"""
Script para agregar campos de límites de respuesta a la tabla configuracion_bot
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables de entorno
load_dotenv()

# Configurar Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def agregar_campos_bd():
    """Agrega los campos necesarios para límites de respuesta"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Variables de entorno SUPABASE_URL o SUPABASE_KEY no encontradas")
        return False

    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("🔧 Agregando campos a configuracion_bot...")
        
        # Primero verificar la estructura actual
        response = supabase.table("configuracion_bot").select("*").limit(1).execute()
        
        if not response.data:
            print("⚠️ No hay datos en configuracion_bot para verificar")
            return False
            
        config_actual = response.data[0]
        campos_existentes = list(config_actual.keys())
        
        print(f"📋 Campos actuales: {campos_existentes}")
        
        # Verificar si ya existen los campos
        tiene_modo = 'modo_respuesta' in campos_existentes
        tiene_mensaje = 'mensaje_fuera_tema' in campos_existentes
        
        if tiene_modo and tiene_mensaje:
            print("✅ Los campos ya existen en la tabla")
            return True
        
        # Si no existen, intentar agregarlos usando UPDATE con upsert
        print("🔄 Agregando campos faltantes...")
        
        # Obtener todas las configuraciones
        all_configs = supabase.table("configuracion_bot").select("*").execute()
        
        for config in all_configs.data:
            nombre_nora = config.get("nombre_nora")
            updates = {}
            
            if not tiene_modo:
                updates["modo_respuesta"] = "flexible"
                
            if not tiene_mensaje:
                updates["mensaje_fuera_tema"] = "Lo siento, no tengo información sobre ese tema. Te conectaré con un humano para ayudarte mejor."
            
            if updates:
                print(f"    ➤ Actualizando {nombre_nora}")
                supabase.table("configuracion_bot").update(updates).eq("nombre_nora", nombre_nora).execute()
        
        print("✅ Campos agregados correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al agregar campos: {e}")
        return False

def verificar_resultado():
    """Verifica que los campos se agregaron correctamente"""
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        response = supabase.table("configuracion_bot").select("nombre_nora, modo_respuesta, mensaje_fuera_tema").execute()
        
        if response.data:
            print("\n📋 Configuraciones actualizadas:")
            for config in response.data:
                nombre = config.get("nombre_nora", "N/A")
                modo = config.get("modo_respuesta", "No configurado")
                mensaje = config.get("mensaje_fuera_tema", "No configurado")
                
                print(f"\n🤖 {nombre}")
                print(f"    ➤ Modo: {modo}")
                print(f"    ➤ Mensaje: {mensaje[:50]}...")
                
        return True
        
    except Exception as e:
        print(f"❌ Error al verificar resultado: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Agregando campos de límites de respuesta\n")
    
    if agregar_campos_bd():
        verificar_resultado()
        print("\n✅ Proceso completado exitosamente")
    else:
        print("\n❌ No se pudieron agregar los campos")
