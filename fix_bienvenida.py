#!/usr/bin/env python3
"""
Script alternativo para agregar columna 'bienvenida' usando método de inserción
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables de entorno
load_dotenv()

# Configurar Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def metodo_copia_tabla():
    """Método alternativo: copiar datos con nueva columna"""
    print("🔄 Método alternativo: recrear configuraciones con columna bienvenida")
    
    try:
        # 1. Obtener todas las configuraciones actuales
        response = supabase.table("configuracion_bot").select("*").execute()
        
        if not response.data:
            print("⚠️ No hay configuraciones para migrar")
            return False
        
        configuraciones = response.data
        print(f"📋 Encontradas {len(configuraciones)} configuraciones")
        
        # 2. Para cada configuración, agregar el campo bienvenida
        for config in configuraciones:
            nombre_nora = config.get("nombre_nora")
            print(f"    🔧 Procesando {nombre_nora}...")
            
            # Crear nueva configuración con todos los campos + bienvenida
            config_actualizada = config.copy()
            
            # Agregar campo bienvenida si no existe
            if 'bienvenida' not in config_actualizada:
                config_actualizada['bienvenida'] = f"¡Hola! 👋 Soy {nombre_nora.capitalize()}, tu asistente virtual. ¿En qué puedo ayudarte hoy?"
            
            # Eliminar configuración antigua
            delete_response = supabase.table("configuracion_bot").delete().eq("nombre_nora", nombre_nora).execute()
            
            # Insertar configuración actualizada
            insert_response = supabase.table("configuracion_bot").insert(config_actualizada).execute()
            
            if insert_response.data:
                print(f"        ✅ {nombre_nora} actualizada con columna bienvenida")
            else:
                print(f"        ❌ Error actualizando {nombre_nora}")
                # Restaurar configuración original si falló
                supabase.table("configuracion_bot").insert(config).execute()
        
        print("✅ Migración completada")
        return True
        
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        return False

def verificar_bienvenida():
    """Verifica que la columna bienvenida existe y funciona"""
    print("\n🔍 Verificando columna bienvenida...")
    
    try:
        # Intentar obtener datos incluyendo bienvenida
        response = supabase.table("configuracion_bot").select("nombre_nora, bienvenida").execute()
        
        if response.data:
            print("✅ Columna 'bienvenida' disponible")
            
            for config in response.data:
                nombre = config.get("nombre_nora", "N/A")
                bienvenida = config.get("bienvenida", "No configurado")
                print(f"    🤖 {nombre}: {bienvenida[:40]}...")
                
            return True
        else:
            print("⚠️ No se pudieron obtener configuraciones")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        if "bienvenida" in str(e):
            print("💡 La columna 'bienvenida' no existe en la tabla")
        return False

def solucion_rapida():
    """Solución rápida: agregar datos con bienvenida usando upsert"""
    print("\n⚡ Solución rápida: usar UPSERT para agregar campo")
    
    try:
        # Obtener configuraciones actuales
        response = supabase.table("configuracion_bot").select("*").execute()
        
        for config in response.data:
            nombre_nora = config.get("nombre_nora")
            
            # Preparar datos actualizados
            update_data = {
                "nombre_nora": nombre_nora,
                "bienvenida": f"¡Hola! 👋 Soy {nombre_nora.capitalize()}, tu asistente virtual. ¿En qué puedo ayudarte hoy?"
            }
            
            # Usar upsert para agregar el campo
            upsert_response = supabase.table("configuracion_bot") \
                .upsert(update_data, on_conflict="nombre_nora") \
                .execute()
            
            if upsert_response.data:
                print(f"    ✅ {nombre_nora} actualizada")
            else:
                print(f"    ❌ Error con {nombre_nora}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en solución rápida: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Script alternativo para agregar columna bienvenida\n")
    
    # Verificar estado actual
    if verificar_bienvenida():
        print("\n✅ La columna ya existe y funciona correctamente")
    else:
        print("\n🔄 Intentando diferentes métodos...\n")
        
        # Método 1: Solución rápida con upsert
        print("🚀 Método 1: Solución rápida")
        if solucion_rapida():
            if verificar_bienvenida():
                print("✅ Método 1 exitoso")
            else:
                print("❌ Método 1 falló")
                
                # Método 2: Copia de tabla
                print("\n🔄 Método 2: Migración completa")
                if metodo_copia_tabla():
                    verificar_bienvenida()
    
    print("\n📝 Si ningún método funciona, ejecuta manualmente en Supabase:")
    print("   ALTER TABLE configuracion_bot ADD COLUMN bienvenida TEXT;")
    print("\n🏁 Proceso completado")
