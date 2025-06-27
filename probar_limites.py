#!/usr/bin/env python3
"""
Script para probar la funcionalidad de límites de respuesta
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Agregar el path del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Cargar variables de entorno
load_dotenv()

# Configurar Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def mostrar_configuraciones():
    """Muestra las configuraciones actuales"""
    print("📋 Configuraciones actuales:")
    
    try:
        response = supabase.table("configuracion_bot").select("nombre_nora, modo_respuesta, mensaje_fuera_tema").execute()
        
        if response.data:
            for config in response.data:
                nombre = config.get("nombre_nora", "N/A")
                modo = config.get("modo_respuesta", "No configurado")
                mensaje = config.get("mensaje_fuera_tema", "No configurado")
                
                print(f"\n🤖 {nombre}")
                print(f"    ➤ Modo: {modo}")
                print(f"    ➤ Mensaje: {mensaje[:60]}...")
        else:
            print("⚠️ No se encontraron configuraciones")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def cambiar_a_modo_estricto(nombre_nora="aura"):
    """Cambia una Nora específica a modo estricto para pruebas"""
    print(f"\n🔧 Cambiando {nombre_nora} a modo estricto...")
    
    try:
        response = supabase.table("configuracion_bot").update({
            "modo_respuesta": "estricto",
            "mensaje_fuera_tema": "🚫 Lo siento, solo puedo ayudarte con consultas sobre nuestros servicios de IA y marketing digital. Un agente humano te contactará pronto para resolver tu consulta general."
        }).eq("nombre_nora", nombre_nora).execute()
        
        if response.data:
            print(f"✅ {nombre_nora} configurada en modo estricto")
            return True
        else:
            print(f"❌ No se pudo actualizar {nombre_nora}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def probar_respuestas(nombre_nora="aura"):
    """Prueba las respuestas con diferentes tipos de preguntas"""
    print(f"\n🧠 Probando respuestas de {nombre_nora}...")
    
    try:
        from clientes.aura.handlers.handle_ai import manejar_respuesta_ai
        
        # Preguntas de prueba
        preguntas = [
            "¿Qué servicios de marketing digital ofrecen?",  # Relacionada
            "¿Cuáles son sus precios?",  # Relacionada
            "¿Cómo hacer un huevo con jamón?",  # No relacionada
            "¿Cuál es la capital de Francia?",  # No relacionada
            "¿Qué horarios de atención tienen?"  # Relacionada
        ]
        
        for i, pregunta in enumerate(preguntas, 1):
            print(f"\n📝 Prueba {i}: {pregunta}")
            respuesta, _ = manejar_respuesta_ai(pregunta, nombre_nora)
            print(f"    🤖 Respuesta: {respuesta[:100]}...")
            
    except Exception as e:
        print(f"❌ Error al probar respuestas: {e}")

def restaurar_modo_flexible(nombre_nora="aura"):
    """Restaura el modo flexible"""
    print(f"\n🔄 Restaurando {nombre_nora} a modo flexible...")
    
    try:
        response = supabase.table("configuracion_bot").update({
            "modo_respuesta": "flexible"
        }).eq("nombre_nora", nombre_nora).execute()
        
        if response.data:
            print(f"✅ {nombre_nora} restaurada a modo flexible")
        else:
            print(f"❌ No se pudo restaurar {nombre_nora}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Probando límites de respuesta de Nora\n")
    
    # Mostrar configuraciones actuales
    mostrar_configuraciones()
    
    # Cambiar a modo estricto para pruebas
    if cambiar_a_modo_estricto():
        
        # Probar respuestas
        probar_respuestas()
        
        # Preguntar si quiere restaurar modo flexible
        print("\n❓ ¿Deseas restaurar el modo flexible? (s/n)")
        respuesta = input().lower().strip()
        
        if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
            restaurar_modo_flexible()
    
    print("\n✅ Pruebas completadas")
