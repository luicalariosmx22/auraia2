#!/usr/bin/env python3
"""
Script para probar el mensaje de bienvenida de Nora
"""

import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta

# Cargar variables de entorno
load_dotenv()

# Configurar Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def configurar_mensaje_bienvenida():
    """Configura un mensaje de bienvenida para pruebas"""
    print("🎯 Configurando mensaje de bienvenida para Nora...")
    
    mensaje_ejemplo = """¡Hola! 👋 Soy Nora, tu asistente virtual de AuraAI.

🤖 Estoy aquí para ayudarte con:
• Información sobre nuestros servicios de IA
• Marketing digital y automatización  
• Responder dudas sobre nuestros productos
• Conectarte con nuestro equipo humano

¿En qué puedo ayudarte hoy? 😊"""

    try:
        response = supabase.table("configuracion_bot").update({
            "bienvenida": mensaje_ejemplo
        }).eq("nombre_nora", "aura").execute()
        
        if response.data:
            print("✅ Mensaje de bienvenida configurado correctamente")
            print(f"📝 Mensaje: {mensaje_ejemplo[:60]}...")
            return True
        else:
            print("❌ No se pudo configurar el mensaje")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def mostrar_configuracion_actual():
    """Muestra la configuración actual"""
    print("\n📋 Configuración actual:")
    
    try:
        response = supabase.table("configuracion_bot").select("nombre_nora, bienvenida").execute()
        
        for config in response.data:
            nombre = config.get("nombre_nora", "N/A")
            bienvenida = config.get("bienvenida", "No configurado")
            
            print(f"\n🤖 {nombre}")
            if bienvenida and bienvenida != "No configurado":
                print(f"    ✅ Bienvenida: {bienvenida[:80]}...")
            else:
                print(f"    ❌ Sin mensaje de bienvenida")
                
    except Exception as e:
        print(f"❌ Error: {e}")

def simular_nuevo_contacto():
    """Simula cómo se comportaría con un nuevo contacto"""
    print("\n🧪 Simulando nuevo contacto...")
    
    numero_test = "+521234567890"
    nombre_nora = "aura"
    
    # Verificar si existe historial
    historial = supabase.table("historial_conversaciones") \
        .select("id, created_at") \
        .eq("telefono", numero_test) \
        .eq("nombre_nora", nombre_nora) \
        .order("created_at", desc=True) \
        .limit(1) \
        .execute().data
    
    if not historial:
        print("✅ Es nuevo contacto - se enviará bienvenida")
    else:
        # Verificar días de inactividad
        try:
            ultima_interaccion = datetime.fromisoformat(historial[0]["created_at"].replace('Z', '+00:00'))
            ahora = datetime.now().astimezone()
            dias_inactivo = (ahora - ultima_interaccion).days
            
            if dias_inactivo >= 7:
                print(f"✅ Usuario inactivo por {dias_inactivo} días - se enviará bienvenida")
            else:
                print(f"⚠️ Usuario activo (última interacción hace {dias_inactivo} días) - no se enviará bienvenida")
        except Exception as e:
            print(f"❌ Error calculando inactividad: {e}")

def limpiar_historial_test():
    """Limpia el historial de prueba"""
    print("\n🧹 Limpiando historial de prueba...")
    
    numero_test = "+521234567890"
    
    try:
        # Eliminar historial de prueba
        supabase.table("historial_conversaciones").delete().eq("telefono", numero_test).execute()
        print("✅ Historial de prueba eliminado")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Probando mensaje de bienvenida\n")
    
    # Mostrar configuración actual
    mostrar_configuracion_actual()
    
    # Configurar mensaje de ejemplo si no existe
    print("\n" + "="*50)
    configurar_mensaje_bienvenida()
    
    # Simular comportamiento con nuevo contacto
    print("\n" + "="*50)
    simular_nuevo_contacto()
    
    # Preguntar si quiere limpiar historial de prueba
    print("\n" + "="*50)
    respuesta = input("¿Quieres limpiar el historial de prueba? (s/n): ").lower().strip()
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        limpiar_historial_test()
    
    print("\n✅ Prueba completada")
    print("💡 Ahora puedes enviar un mensaje desde WhatsApp al número de prueba para verificar la bienvenida")
