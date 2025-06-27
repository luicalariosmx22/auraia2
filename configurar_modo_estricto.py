#!/usr/bin/env python3
"""
Script simple para verificar configuración y cambiar a modo estricto
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

print("🚀 Configurando modo estricto para Nora")

# Mostrar configuración actual
print("\n📋 Configuración actual:")
response = supabase.table("configuracion_bot").select("nombre_nora, modo_respuesta, mensaje_fuera_tema").execute()

for config in response.data:
    nombre = config.get("nombre_nora", "N/A")
    modo = config.get("modo_respuesta", "No configurado")
    print(f"🤖 {nombre}: {modo}")

# Cambiar 'aura' a modo estricto
print("\n🔧 Configurando 'aura' en modo estricto...")
update_response = supabase.table("configuracion_bot").update({
    "modo_respuesta": "estricto",
    "mensaje_fuera_tema": "🚫 Lo siento, solo puedo ayudarte con consultas sobre nuestros servicios de IA y marketing digital. Un agente humano te contactará pronto para resolver tu consulta general."
}).eq("nombre_nora", "aura").execute()

if update_response.data:
    print("✅ Configuración actualizada exitosamente")
    
    # Verificar cambio
    verify_response = supabase.table("configuracion_bot").select("nombre_nora, modo_respuesta, mensaje_fuera_tema").eq("nombre_nora", "aura").execute()
    
    if verify_response.data:
        config = verify_response.data[0]
        print(f"    ➤ Modo: {config.get('modo_respuesta')}")
        print(f"    ➤ Mensaje: {config.get('mensaje_fuera_tema')[:60]}...")
else:
    print("❌ No se pudo actualizar la configuración")

print("\n✅ Configuración completada")
print("💡 Ahora puedes probar preguntando algo como '¿Cómo hacer un huevo con jamón?' desde el chat")
print("    Nora debería responder con el mensaje personalizado en lugar de contestar la pregunta")
