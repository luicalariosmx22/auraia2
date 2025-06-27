#!/usr/bin/env python3
"""
Script para agregar la columna 'bienvenida' a la tabla configuracion_bot
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables de entorno
load_dotenv()

# Configurar Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def verificar_estructura_actual():
    """Verifica la estructura actual de la tabla"""
    print("🔍 Verificando estructura actual de configuracion_bot...")
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Obtener una configuración para ver campos disponibles
        response = supabase.table("configuracion_bot").select("*").limit(1).execute()
        
        if response.data:
            config = response.data[0]
            campos_actuales = list(config.keys())
            
            print(f"📋 Campos actuales: {campos_actuales}")
            
            # Verificar si ya existe la columna bienvenida
            if 'bienvenida' in campos_actuales:
                print("✅ La columna 'bienvenida' ya existe")
                return True
            else:
                print("❌ La columna 'bienvenida' NO existe")
                return False
        else:
            print("⚠️ No hay datos en la tabla para verificar")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
        return False

def agregar_columna_bienvenida():
    """Agrega la columna bienvenida usando UPDATE para simular ALTER TABLE"""
    print("\n🔧 Intentando agregar columna 'bienvenida'...")
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Obtener todas las configuraciones
        response = supabase.table("configuracion_bot").select("*").execute()
        
        if not response.data:
            print("⚠️ No hay configuraciones para actualizar")
            return False
        
        # Intentar agregar el campo 'bienvenida' a cada configuración
        for config in response.data:
            nombre_nora = config.get("nombre_nora")
            
            # Si no tiene el campo, lo agregamos
            if 'bienvenida' not in config:
                print(f"    ➤ Agregando campo 'bienvenida' a {nombre_nora}")
                
                # Mensaje por defecto
                mensaje_default = f"¡Hola! 👋 Soy Nora, tu asistente virtual. ¿En qué puedo ayudarte hoy?"
                
                try:
                    update_response = supabase.table("configuracion_bot").update({
                        "bienvenida": mensaje_default
                    }).eq("nombre_nora", nombre_nora).execute()
                    
                    if update_response.data:
                        print(f"        ✅ Campo agregado correctamente")
                    else:
                        print(f"        ❌ Error al agregar campo")
                        
                except Exception as e:
                    print(f"        ❌ Error: {e}")
                    
        print("\n✅ Proceso de agregado de columna completado")
        return True
        
    except Exception as e:
        print(f"❌ Error agregando columna: {e}")
        return False

def verificar_resultado():
    """Verifica que la columna se agregó correctamente"""
    print("\n🔍 Verificando resultado...")
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Intentar seleccionar incluyendo la columna bienvenida
        response = supabase.table("configuracion_bot").select("nombre_nora, bienvenida").execute()
        
        if response.data:
            print("✅ La columna 'bienvenida' ahora existe")
            
            for config in response.data:
                nombre = config.get("nombre_nora", "N/A")
                bienvenida = config.get("bienvenida", "No configurado")
                print(f"    🤖 {nombre}: {bienvenida[:50]}...")
                
            return True
        else:
            print("⚠️ No se pudieron obtener los datos")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando resultado: {e}")
        return False

def crear_script_sql():
    """Crea un script SQL para ejecutar manualmente si es necesario"""
    print("\n📝 Creando script SQL para ejecución manual...")
    
    script_sql = """
-- Script para agregar columna 'bienvenida' a configuracion_bot

-- Opción 1: Usar ALTER TABLE (si tienes permisos de administrador)
ALTER TABLE configuracion_bot 
ADD COLUMN IF NOT EXISTS bienvenida TEXT DEFAULT '¡Hola! 👋 Soy Nora, tu asistente virtual. ¿En qué puedo ayudarte hoy?';

-- Opción 2: Actualizar registros existentes si la columna ya existe pero está vacía
UPDATE configuracion_bot 
SET bienvenida = '¡Hola! 👋 Soy Nora, tu asistente virtual. ¿En qué puedo ayudarte hoy?'
WHERE bienvenida IS NULL OR bienvenida = '';

-- Verificar resultado
SELECT nombre_nora, bienvenida FROM configuracion_bot;
"""
    
    with open("agregar_columna_bienvenida.sql", "w", encoding="utf-8") as f:
        f.write(script_sql)
    
    print("✅ Script SQL creado: agregar_columna_bienvenida.sql")

if __name__ == "__main__":
    print("🚀 Agregando columna 'bienvenida' a configuracion_bot\n")
    
    # Verificar estructura actual
    existe = verificar_estructura_actual()
    
    if not existe:
        # Intentar agregar la columna
        if agregar_columna_bienvenida():
            # Verificar que se agregó correctamente
            verificar_resultado()
        else:
            print("\n⚠️ No se pudo agregar la columna automáticamente")
            crear_script_sql()
            print("\n💡 Opciones:")
            print("1. Ejecutar el script SQL manualmente en tu panel de Supabase")
            print("2. Contactar al administrador de la base de datos")
    else:
        print("\n✅ La columna ya existe, no es necesario hacer nada")
    
    print("\n🏁 Proceso completado")
