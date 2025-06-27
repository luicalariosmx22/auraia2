#!/usr/bin/env python3
"""
Generador de mensajes de bienvenida personalizados para diferentes tipos de negocio
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

# Plantillas de mensajes por tipo de negocio
PLANTILLAS_BIENVENIDA = {
    "agencia_marketing": {
        "titulo": "🚀 Agencia de Marketing Digital",
        "mensaje": """¡Hola! 👋 Soy {nombre_bot}, tu asistente virtual de {nombre_empresa}.

🎯 Especialistas en:
• Marketing Digital y Publicidad Online
• Automatización con Inteligencia Artificial  
• Gestión de Redes Sociales
• SEO y Google Ads

¿Cómo puedo ayudarte a hacer crecer tu negocio hoy? 📈""",
        "variables": ["nombre_bot", "nombre_empresa"]
    },
    
    "ecommerce": {
        "titulo": "🛍️ Tienda Online",
        "mensaje": """¡Bienvenido/a! 🛒 Soy {nombre_bot} de {nombre_empresa}.

✨ Estoy aquí para ayudarte con:
• Información de productos y catálogo
• Estado de pedidos y envíos
• Ofertas y descuentos especiales
• Resolver cualquier duda

¿Qué estás buscando hoy? 🔍""",
        "variables": ["nombre_bot", "nombre_empresa"]
    },
    
    "servicios_profesionales": {
        "titulo": "💼 Servicios Profesionales",
        "mensaje": """¡Hola! 👨‍💼 Soy {nombre_bot}, asistente virtual de {nombre_empresa}.

🔧 Te puedo ayudar con:
• Información sobre nuestros servicios
• Agendar citas y consultas
• Precios y paquetes disponibles
• Contacto con nuestros especialistas

¿En qué podemos ayudarte? 📞""",
        "variables": ["nombre_bot", "nombre_empresa"]
    },
    
    "restaurante": {
        "titulo": "🍽️ Restaurante",
        "mensaje": """¡Bienvenido/a! 🍽️ Soy {nombre_bot} de {nombre_empresa}.

😋 Estoy aquí para:
• Mostrar nuestro menú y especialidades
• Tomar reservaciones
• Información de horarios y ubicación
• Pedidos para delivery

¿Qué se te antoja hoy? 🥘""",
        "variables": ["nombre_bot", "nombre_empresa"]
    },
    
    "educacion": {
        "titulo": "📚 Centro Educativo",
        "mensaje": """¡Hola! 📚 Soy {nombre_bot}, tu asistente educativo de {nombre_empresa}.

🎓 Te puedo ayudar con:
• Información de cursos y programas
• Proceso de inscripciones
• Horarios y modalidades
• Becas y financiamiento

¿Qué quieres aprender hoy? 🧠""",
        "variables": ["nombre_bot", "nombre_empresa"]
    },
    
    "salud": {
        "titulo": "🏥 Servicios de Salud",
        "mensaje": """¡Hola! 👩‍⚕️ Soy {nombre_bot} de {nombre_empresa}.

💊 Estoy para ayudarte con:
• Agendar citas médicas
• Información de especialidades
• Horarios de atención
• Servicios y estudios disponibles

¿Cómo puedo ayudarte con tu salud? 🩺""",
        "variables": ["nombre_bot", "nombre_empresa"]
    },
    
    "tecnologia": {
        "titulo": "💻 Empresa de Tecnología",
        "mensaje": """¡Hola! 💻 Soy {nombre_bot}, asistente de {nombre_empresa}.

⚡ Te ayudo con:
• Información de productos y servicios tech
• Soporte técnico inicial
• Cotizaciones y demos
• Contacto con nuestros ingenieros

¿Qué solución tecnológica necesitas? 🔧""",
        "variables": ["nombre_bot", "nombre_empresa"]
    }
}

def mostrar_plantillas():
    """Muestra todas las plantillas disponibles"""
    print("📋 Plantillas de bienvenida disponibles:\n")
    
    for i, (clave, plantilla) in enumerate(PLANTILLAS_BIENVENIDA.items(), 1):
        print(f"{i}. {plantilla['titulo']}")
    
    print("\n" + "="*50)

def generar_mensaje_personalizado():
    """Permite al usuario generar un mensaje personalizado"""
    print("🎨 Generador de mensaje de bienvenida personalizado\n")
    
    mostrar_plantillas()
    
    try:
        seleccion = int(input("Selecciona una plantilla (1-{}): ".format(len(PLANTILLAS_BIENVENIDA))))
        
        if 1 <= seleccion <= len(PLANTILLAS_BIENVENIDA):
            plantilla_key = list(PLANTILLAS_BIENVENIDA.keys())[seleccion - 1]
            plantilla = PLANTILLAS_BIENVENIDA[plantilla_key]
            
            print(f"\n📝 Seleccionaste: {plantilla['titulo']}")
            print("\nAhora necesito algunos datos para personalizar el mensaje:\n")
            
            variables = {}
            for variable in plantilla['variables']:
                if variable == "nombre_bot":
                    valor = input(f"💬 Nombre del bot/asistente (ej: Nora): ").strip()
                elif variable == "nombre_empresa":
                    valor = input(f"🏢 Nombre de tu empresa: ").strip()
                else:
                    valor = input(f"📝 {variable}: ").strip()
                
                if not valor:
                    print(f"⚠️ El campo {variable} no puede estar vacío")
                    return None
                    
                variables[variable] = valor
            
            # Generar mensaje personalizado
            mensaje_final = plantilla['mensaje'].format(**variables)
            
            print("\n" + "="*60)
            print("✨ TU MENSAJE DE BIENVENIDA PERSONALIZADO:")
            print("="*60)
            print(mensaje_final)
            print("="*60)
            
            return mensaje_final
            
        else:
            print("❌ Selección inválida")
            return None
            
    except ValueError:
        print("❌ Por favor ingresa un número válido")
        return None

def guardar_mensaje_en_bd(mensaje, nombre_nora="aura"):
    """Guarda el mensaje generado en la base de datos"""
    print(f"\n💾 ¿Quieres guardar este mensaje para {nombre_nora}? (s/n): ", end="")
    respuesta = input().lower().strip()
    
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            response = supabase.table("configuracion_bot").update({
                "bienvenida": mensaje
            }).eq("nombre_nora", nombre_nora).execute()
            
            if response.data:
                print(f"✅ Mensaje guardado correctamente para {nombre_nora}")
                return True
            else:
                print("❌ No se pudo guardar el mensaje")
                return False
                
        except Exception as e:
            print(f"❌ Error al guardar: {e}")
            return False
    else:
        print("📋 Mensaje no guardado. Puedes copiarlo manualmente desde arriba.")
        return False

def crear_mensaje_desde_cero():
    """Permite crear un mensaje completamente personalizado"""
    print("✏️ Crear mensaje desde cero\n")
    
    print("📝 Consejos para un buen mensaje de bienvenida:")
    print("• Saluda de forma amigable")
    print("• Presenta a tu bot y empresa")
    print("• Menciona los servicios principales") 
    print("• Termina con una pregunta abierta")
    print("• Usa emojis para hacerlo más atractivo")
    print("• Mantén un tono profesional pero cercano\n")
    
    nombre_bot = input("💬 Nombre del bot: ").strip()
    nombre_empresa = input("🏢 Nombre de la empresa: ").strip()
    
    print(f"\n📝 Escribe tu mensaje personalizado:")
    print("(Puedes usar {nombre_bot} y {nombre_empresa} como variables)")
    print("Escribe línea por línea, presiona Enter dos veces para terminar:\n")
    
    lineas = []
    linea_vacia = False
    
    while True:
        linea = input()
        if linea == "":
            if linea_vacia:
                break
            linea_vacia = True
        else:
            linea_vacia = False
            lineas.append(linea)
    
    mensaje_personalizado = "\n".join(lineas)
    
    # Reemplazar variables
    mensaje_final = mensaje_personalizado.replace("{nombre_bot}", nombre_bot).replace("{nombre_empresa}", nombre_empresa)
    
    print("\n" + "="*60)
    print("✨ TU MENSAJE PERSONALIZADO:")
    print("="*60)
    print(mensaje_final)
    print("="*60)
    
    return mensaje_final

if __name__ == "__main__":
    print("🎯 Generador de Mensajes de Bienvenida para Nora\n")
    
    while True:
        print("¿Qué quieres hacer?")
        print("1. 📋 Usar plantilla predefinida")
        print("2. ✏️ Crear mensaje desde cero")
        print("3. 👀 Ver configuración actual")
        print("4. 🚪 Salir")
        
        opcion = input("\nSelecciona una opción (1-4): ").strip()
        
        if opcion == "1":
            mensaje = generar_mensaje_personalizado()
            if mensaje:
                guardar_mensaje_en_bd(mensaje)
        
        elif opcion == "2":
            mensaje = crear_mensaje_desde_cero()
            if mensaje:
                guardar_mensaje_en_bd(mensaje)
        
        elif opcion == "3":
            try:
                response = supabase.table("configuracion_bot").select("nombre_nora, bienvenida").execute()
                print("\n📋 Configuración actual:")
                for config in response.data:
                    nombre = config.get("nombre_nora", "N/A")
                    bienvenida = config.get("bienvenida", "No configurado")
                    print(f"\n🤖 {nombre}:")
                    if bienvenida and bienvenida != "No configurado":
                        print(f"    {bienvenida[:100]}...")
                    else:
                        print("    ❌ Sin mensaje configurado")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif opcion == "4":
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción inválida")
        
        print("\n" + "="*60 + "\n")
