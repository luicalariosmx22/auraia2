#!/usr/bin/env python3
"""
Script para probar y verificar la implementación de límites de respuesta de Nora
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables de entorno
load_dotenv()

# Configurar Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def verificar_estructura_bd():
    """Verifica si las columnas necesarias existen en la tabla configuracion_bot"""
    print("🔍 Verificando estructura de la base de datos...")
    
    try:
        # Intentar obtener una configuración con los nuevos campos
        response = supabase.table("configuracion_bot").select("nombre_nora, modo_respuesta, mensaje_fuera_tema").limit(1).execute()
        
        if response.data:
            print("✅ Columnas 'modo_respuesta' y 'mensaje_fuera_tema' existen en la tabla")
            config = response.data[0]
            print(f"    ➤ Configuración encontrada: {config}")
            return True
        else:
            print("⚠️ No hay datos en configuracion_bot")
            return False
            
    except Exception as e:
        print(f"❌ Error al verificar estructura: {e}")
        print("💡 Posiblemente las columnas no existen aún")
        return False

def actualizar_configuracion_default():
    """Actualiza las configuraciones existentes con valores por defecto"""
    print("\n🔧 Actualizando configuraciones con valores por defecto...")
    
    try:
        # Obtener todas las configuraciones
        response = supabase.table("configuracion_bot").select("*").execute()
        
        if not response.data:
            print("⚠️ No hay configuraciones para actualizar")
            return
            
        for config in response.data:
            nombre_nora = config.get("nombre_nora")
            
            # Valores por defecto si no existen
            updates = {}
            
            if not config.get("modo_respuesta"):
                updates["modo_respuesta"] = "flexible"
                
            if not config.get("mensaje_fuera_tema"):
                updates["mensaje_fuera_tema"] = "Lo siento, no tengo información sobre ese tema. Te conectaré con un humano para ayudarte mejor."
            
            if updates:
                print(f"    ➤ Actualizando {nombre_nora}: {updates}")
                supabase.table("configuracion_bot").update(updates).eq("nombre_nora", nombre_nora).execute()
                
        print("✅ Configuraciones actualizadas correctamente")
        
    except Exception as e:
        print(f"❌ Error al actualizar configuraciones: {e}")

def probar_funcion_ia():
    """Prueba la nueva función de IA con modo estricto"""
    print("\n🧠 Probando función de IA...")
    
    try:
        # Importar la función actualizada
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from clientes.aura.handlers.handle_ai import manejar_respuesta_ai
        
        # Prueba 1: Pregunta relacionada con la empresa
        print("\n📝 Prueba 1 - Pregunta relacionada con la empresa:")
        respuesta1, _ = manejar_respuesta_ai("¿Qué servicios ofrecen?", "aura")
        print(f"    Respuesta: {respuesta1[:100]}...")
        
        # Prueba 2: Pregunta fuera del área (si está en modo estricto)
        print("\n📝 Prueba 2 - Pregunta general:")
        respuesta2, _ = manejar_respuesta_ai("¿Cuál es la capital de Francia?", "aura")
        print(f"    Respuesta: {respuesta2[:100]}...")
        
        print("✅ Función de IA funcionando correctamente")
        
    except Exception as e:
        print(f"❌ Error al probar función de IA: {e}")

def mostrar_configuracion_actual():
    """Muestra la configuración actual de todas las Noras"""
    print("\n📋 Configuración actual de Noras:")
    
    try:
        response = supabase.table("configuracion_bot").select("nombre_nora, modo_respuesta, mensaje_fuera_tema").execute()
        
        if response.data:
            for config in response.data:
                print(f"\n🤖 {config.get('nombre_nora', 'N/A')}")
                print(f"    ➤ Modo: {config.get('modo_respuesta', 'No configurado')}")
                print(f"    ➤ Mensaje: {config.get('mensaje_fuera_tema', 'No configurado')[:60]}...")
        else:
            print("⚠️ No se encontraron configuraciones")
            
    except Exception as e:
        print(f"❌ Error al obtener configuraciones: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando verificación de límites de respuesta de Nora\n")
    
    # Verificar estructura
    estructura_ok = verificar_estructura_bd()
    
    if estructura_ok:
        # Actualizar configuraciones por defecto
        actualizar_configuracion_default()
        
        # Mostrar configuración actual
        mostrar_configuracion_actual()
        
        # Probar función de IA
        probar_funcion_ia()
    else:
        print("\n❌ No se puede continuar sin la estructura correcta de la base de datos")
        print("💡 Asegúrate de que las columnas 'modo_respuesta' y 'mensaje_fuera_tema' existan en 'configuracion_bot'")
    
    print("\n✅ Verificación completada")
