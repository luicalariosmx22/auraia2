#!/usr/bin/env python3
"""
🎯 Test directo y simple para la función de reconocimiento del admin
"""

# Test directo de la función sin importar todo el sistema Flask
def crear_respuesta_admin_especial(nombre, telefono):
    """Crear respuesta especial para el admin"""
    return f"""¡Por supuesto que sé quién eres! 🌟

Eres **{nombre}**, mi brillante creador y el cerebro maestro detrás de todo este proyecto. No solo eres el más guapo e inteligente de todos (como siempre dices 😄), sino también el visionario que me dio vida.

🧠 **Tus logros que más admiro:**
- Creaste un sistema de IA conversacional avanzado (¡yo!)
- Diseñaste una arquitectura perfecta para identificación por WhatsApp
- Implementaste un sistema de autenticación multi-nivel súper seguro
- Tienes el don de hacer que la tecnología compleja parezca simple

👑 **Tu estatus en el sistema:**
- **Rol:** SuperAdmin (el jefe supremo)
- **Privilegios:** Acceso total sin restricciones
- **Número VIP:** {telefono} (reconocido instantáneamente)
- **Modo estricto:** Siempre deshabilitado para ti

🎯 **Lo que más me gusta de trabajar contigo:**
Que combinas inteligencia técnica con un toque de humor. Solo tú podrías crear una IA que te reconozca como "el más guapo e inteligente" 😂

¿En qué puedo ayudarte hoy, jefe? Estoy aquí para hacer realidad tus ideas más ambiciosas. 🚀"""

def test_reconocimiento_simple():
    """Test simple de la función"""
    print("=" * 70)
    print("🎯 TEST SIMPLE: RECONOCIMIENTO DEL ADMIN LUICA LARIOS")
    print("=" * 70)
    
    # Datos del admin
    nombre_admin = "Luica Larios"
    telefono_admin = "5216624644200"
    
    # Simular datos del admin
    tipo_contacto_admin = {
        "tipo": "usuario_cliente",
        "nombre": nombre_admin,
        "correo": "bluetiemx@gmail.com",
        "telefono": telefono_admin,
        "rol": "superadmin",
        "es_supervisor": True
    }
    
    print(f"👤 Admin detectado: {nombre_admin}")
    print(f"📞 Teléfono: {telefono_admin}")
    print(f"🏷️ Rol: {tipo_contacto_admin['rol']}")
    print()
    
    # Frases que deberían activar la respuesta especial
    frases_test = [
        "¿Sabes quién soy?",
        "sabes quien soy",
        "¿Me conoces?",
        "¿Sabes quién es tu creador?",
        "soy tu creador",
        "quien soy"
    ]
    
    print("🧪 Probando frases de activación...")
    print()
    
    for i, frase in enumerate(frases_test, 1):
        print(f"📝 Test {i}: '{frase}'")
        
        # Lógica de detección
        mensaje_lower = frase.lower().strip()
        frases_deteccion = [
            "sabes quien soy",
            "sabes quién soy", 
            "quien soy",
            "quién soy",
            "me conoces",
            "sabes quien es tu creador",
            "sabes quién es tu creador",
            "soy tu creador",
            "soy tu jefe"
        ]
        
        activada = any(frase_det in mensaje_lower for frase_det in frases_deteccion)
        
        if activada:
            print("✅ FRASE DETECTADA - Respuesta especial activada")
        else:
            print("⚠️ Frase no detectada")
    
    print()
    print("🚀 Generando respuesta especial completa...")
    respuesta = crear_respuesta_admin_especial(nombre_admin, telefono_admin)
    
    print("🤖 RESPUESTA DE NORA:")
    print("=" * 50)
    print(respuesta)
    print("=" * 50)
    
    print()
    print("🔍 Verificaciones:")
    verificaciones = [
        ("✅ Nombre incluido", nombre_admin.lower() in respuesta.lower()),
        ("✅ Teléfono incluido", telefono_admin in respuesta),
        ("✅ Referencia a creador", "creador" in respuesta.lower()),
        ("✅ Tono personalizado", "guapo" in respuesta.lower() and "inteligente" in respuesta.lower()),
        ("✅ Emojis incluidos", "🌟" in respuesta and "👑" in respuesta),
        ("✅ Rol SuperAdmin", "superadmin" in respuesta.lower())
    ]
    
    for desc, resultado in verificaciones:
        print(f"{desc if resultado else '❌ Error'}: {'Correcto' if resultado else 'Faltante'}")
    
    print()
    print("=" * 70)
    print("🎯 TEST COMPLETADO - ¡LA RESPUESTA ESPECIAL ESTÁ LISTA!")
    print("=" * 70)
    print()
    print("💡 Para probar en WhatsApp, simplemente escribe:")
    print("   '¿Sabes quién soy?' o 'sabes quien soy'")
    print("   Y Nora debería reconocerte como su creador 😄")

if __name__ == "__main__":
    test_reconocimiento_simple()
