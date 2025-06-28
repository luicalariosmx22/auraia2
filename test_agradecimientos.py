#!/usr/bin/env python3
"""
🧪 Test de Detección de Agradecimientos
Verifica que Nora detecte correctamente los agradecimientos después de mostrar tareas
"""

from clientes.aura.utils.consultor_tareas import ConsultorTareas

def test_deteccion_agradecimientos():
    """Test de detección de agradecimientos"""
    
    print("🧪 TEST DE DETECCIÓN DE AGRADECIMIENTOS")
    print("=" * 50)
    
    # Simular usuario cliente
    usuario_cliente = {
        "id": 123,
        "tipo": "cliente",
        "nombre": "Usuario Test",
        "telefono": "6629360887"
    }
    
    consultor = ConsultorTareas(usuario_cliente, "aura")
    
    # Mensajes de agradecimiento
    mensajes_agradecimiento = [
        "gracias",
        "muchas gracias",
        "perfecto",
        "excelente",
        "muy bien",
        "genial",
        "súper",
        "ok",
        "entendido",
        "Muchas gracias 😊",
        "¡Perfecto! Gracias",
        "Genial, muchas gracias",
        "Ok, entendido"
    ]
    
    # Mensajes que NO son agradecimiento
    mensajes_normales = [
        "¿cuáles son mis tareas?",
        "quiero ver las tareas de mi empresa",
        "hola",
        "necesito ayuda",
        "¿cómo estás?",
        "buenos días"
    ]
    
    print("1️⃣ TESTEAR DETECCIÓN DE AGRADECIMIENTOS:")
    for mensaje in mensajes_agradecimiento:
        es_agradecimiento = consultor.detectar_respuesta_agradecimiento(mensaje)
        resultado = "✅" if es_agradecimiento else "❌"
        print(f"   {resultado} '{mensaje}' → {es_agradecimiento}")
    
    print("\n2️⃣ TESTEAR MENSAJES NORMALES (NO DEBEN DETECTARSE):")
    for mensaje in mensajes_normales:
        es_agradecimiento = consultor.detectar_respuesta_agradecimiento(mensaje)
        resultado = "✅" if not es_agradecimiento else "❌"
        print(f"   {resultado} '{mensaje}' → {es_agradecimiento}")
    
    print("\n3️⃣ TESTEAR RESPUESTAS DE SEGUIMIENTO:")
    for i in range(5):
        respuesta = consultor.generar_respuesta_seguimiento("6629360887")
        print(f"   💬 Respuesta {i+1}: {respuesta}")

if __name__ == "__main__":
    test_deteccion_agradecimientos()
