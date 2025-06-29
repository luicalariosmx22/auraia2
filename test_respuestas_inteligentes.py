#!/usr/bin/env python3
"""
Script de pruebas para el Sistema de Respuestas Inteligentes
Simula diferentes tipos de preguntas y verifica que el sistema responda apropiadamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clientes.aura.utils.respuestas_inteligentes import SistemaRespuestasInteligentes
from clientes.aura.utils.memoria_conversacion import memoria_conversacion

def test_respuestas_inteligentes():
    """Prueba el sistema de respuestas inteligentes con diferentes tipos de preguntas"""
    
    print("🧪 INICIANDO PRUEBAS DEL SISTEMA DE RESPUESTAS INTELIGENTES")
    print("=" * 70)
    
    sistema = SistemaRespuestasInteligentes("aura")
    telefono_test = "1234567890"
    
    # Casos de prueba
    casos_prueba = [
        {
            "nombre": "Pregunta ambigua sobre precio de curso",
            "mensaje": "¿Cuánto cuesta un curso?",
            "esperado": "menu_opciones"
        },
        {
            "nombre": "Pregunta específica sobre IA",
            "mensaje": "curso inteligencia artificial",
            "esperado": "busqueda_especifica"
        },
        {
            "nombre": "Pregunta muy específica (no debería usar sistema inteligente)",
            "mensaje": "¿Cómo están hoy? Me gustaría saber sobre el clima",
            "esperado": "ia_normal"
        },
        {
            "nombre": "Pregunta sobre ubicación",
            "mensaje": "¿Dónde están ubicados?",
            "esperado": "respuesta_contextual"
        },
        {
            "nombre": "Pregunta sobre costos sin especificar",
            "mensaje": "precios",
            "esperado": "menu_opciones"
        }
    ]
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n🧪 CASO {i}: {caso['nombre']}")
        print(f"📝 Mensaje: '{caso['mensaje']}'")
        print("-" * 50)
        
        try:
            respuesta = sistema.procesar_pregunta(caso['mensaje'], telefono=telefono_test)
            
            if respuesta is None:
                print("🔄 Sistema derivó a IA normal (respuesta None)")
                resultado = "ia_normal"
            elif "1️⃣" in respuesta or "2️⃣" in respuesta:
                print("📋 Sistema generó menú de opciones")
                resultado = "menu_opciones"
            elif len(respuesta) > 100:
                print("💬 Sistema generó respuesta contextual")
                resultado = "respuesta_contextual"
            else:
                print("🔍 Sistema generó búsqueda específica")
                resultado = "busqueda_especifica"
            
            print(f"🎯 Resultado: {resultado}")
            print(f"✅ Esperado: {caso['esperado']}")
            
            if resultado == caso['esperado']:
                print("✅ CASO PASÓ")
            else:
                print("❌ CASO FALLÓ")
            
            if respuesta:
                print(f"📄 Respuesta generada:")
                print(respuesta[:200] + "..." if len(respuesta) > 200 else respuesta)
                
        except Exception as e:
            print(f"❌ ERROR EN CASO: {e}")
    
    print("\n" + "=" * 70)
    print("🧪 PRUEBAS COMPLETADAS")

def test_memoria_conversacion():
    """Prueba el sistema de memoria de conversación"""
    
    print("\n🧠 INICIANDO PRUEBAS DE MEMORIA DE CONVERSACIÓN")
    print("=" * 70)
    
    telefono_test = "9876543210"
    nombre_nora_test = "aura"
    
    # Datos de prueba
    opciones_test = [
        {
            'bloque': {
                'id': 'test1',
                'contenido': 'Curso de IA - $500',
                'etiquetas': ['curso', 'ia']
            },
            'puntuacion': 5,
            'razones': ['Información de IA']
        },
        {
            'bloque': {
                'id': 'test2',
                'contenido': 'Curso de Marketing - $300',
                'etiquetas': ['curso', 'marketing']
            },
            'puntuacion': 3,
            'razones': ['Información de cursos']
        }
    ]
    
    try:
        # Limpiar memoria previa
        print("🧹 Limpiando memoria previa...")
        memoria_conversacion.limpiar_memoria(telefono_test, nombre_nora_test)
        
        # Guardar opciones
        print("💾 Guardando opciones en memoria...")
        exito_guardar = memoria_conversacion.guardar_opciones(telefono_test, nombre_nora_test, opciones_test)
        print(f"✅ Guardado exitoso: {exito_guardar}")
        
        # Recuperar opciones
        print("🔍 Recuperando opciones de memoria...")
        opciones_recuperadas = memoria_conversacion.obtener_opciones(telefono_test, nombre_nora_test)
        
        if opciones_recuperadas:
            print(f"✅ Opciones recuperadas: {len(opciones_recuperadas)} elementos")
            for i, opcion in enumerate(opciones_recuperadas, 1):
                print(f"  {i}. {opcion['bloque']['contenido'][:50]}...")
        else:
            print("❌ No se pudieron recuperar opciones")
        
        # Probar selección de menú
        print("\n🎯 Probando selección de menú...")
        sistema = SistemaRespuestasInteligentes(nombre_nora_test)
        
        # Simular selección "1"
        respuesta_seleccion = sistema.procesar_seleccion_menu("1", opciones_recuperadas or opciones_test)
        if respuesta_seleccion:
            print("✅ Selección procesada correctamente")
            print(f"📄 Respuesta: {respuesta_seleccion[:100]}...")
        else:
            print("❌ No se pudo procesar la selección")
        
        # Limpiar memoria final
        print("\n🧹 Limpiando memoria final...")
        memoria_conversacion.limpiar_memoria(telefono_test, nombre_nora_test)
        
    except Exception as e:
        print(f"❌ ERROR EN PRUEBA DE MEMORIA: {e}")
        import traceback
        traceback.print_exc()
    
    print("🧠 PRUEBAS DE MEMORIA COMPLETADAS")

def test_integracion_completa():
    """Prueba la integración completa simulando una conversación real"""
    
    print("\n🔄 INICIANDO PRUEBA DE INTEGRACIÓN COMPLETA")
    print("=" * 70)
    
    sistema = SistemaRespuestasInteligentes("aura")
    telefono_test = "5551234567"
    
    # Simular conversación completa
    conversacion = [
        "¿Cuánto cuesta un curso?",  # Debería generar menú
        "1",                         # Selección del menú
        "¿Hay descuentos?",         # Pregunta de seguimiento
    ]
    
    for i, mensaje in enumerate(conversacion, 1):
        print(f"\n👤 USUARIO (mensaje {i}): {mensaje}")
        print("-" * 30)
        
        try:
            respuesta = sistema.procesar_pregunta(mensaje, telefono=telefono_test)
            
            if respuesta:
                print(f"🤖 NORA: {respuesta}")
            else:
                print("🤖 NORA: [Derivado a IA normal]")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    # Limpiar al final
    memoria_conversacion.limpiar_memoria(telefono_test, "aura")
    print("\n🔄 INTEGRACIÓN COMPLETA FINALIZADA")

if __name__ == "__main__":
    try:
        # Ejecutar todas las pruebas
        test_respuestas_inteligentes()
        test_memoria_conversacion()
        test_integracion_completa()
        
        print("\n" + "🎉" * 20)
        print("TODAS LAS PRUEBAS COMPLETADAS")
        print("🎉" * 20)
        
    except Exception as e:
        print(f"\n❌ ERROR GENERAL EN PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
