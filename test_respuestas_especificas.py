#!/usr/bin/env python3
"""
Script de prueba mejorado para el sistema de respuestas inteligentes
Simula casos específicos como "¿Cuánto cuesta el curso de marketing?"
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def simular_base_conocimiento():
    """Simula datos reales de la base de conocimiento"""
    return [
        {
            'id': 'curso_ia_1',
            'contenido': 'Nuestro Curso de Inteligencia Artificial tiene una duración de 6 semanas presenciales. Incluye teoría y práctica con proyectos reales.\nEl costo del Curso de Inteligencia Artificial es de $15,000 MXN. Incluye materiales, certificación y acceso a la plataforma por 1 año.\nLas clases se imparten en nuestras instalaciones en Av. Revolución #1234, Col. Centro, Guadalajara. Horarios: Lunes a Viernes 6:00-9:00 PM.',
            'etiquetas': ['Curso Inteligencia Artificial', 'presencial', 'IA'],
            'prioridad': True
        },
        {
            'id': 'curso_marketing_1',
            'contenido': 'Curso de Marketing Digital: 4 semanas intensivas. Aprende estrategias de redes sociales, Google Ads y email marketing.\nPrecio del Curso de Marketing Digital: $8,500 MXN. Incluye acceso a herramientas premium y proyecto final.\nUbicación: Mismo centro de capacitación en Av. Revolución #1234. Horarios flexibles: Martes y Jueves 7:00-10:00 PM.',
            'etiquetas': ['Curso Marketing Digital', 'redes sociales', 'publicidad'],
            'prioridad': False
        },
        {
            'id': 'info_general',
            'contenido': 'Ofrecemos cursos especializados en tecnología e innovación. Todos nuestros programas incluyen certificación oficial.',
            'etiquetas': ['cursos', 'capacitación', 'certificación'],
            'prioridad': False
        }
    ]

def probar_caso_especifico(sistema, pregunta, descripcion):
    """Prueba un caso específico y muestra el resultado"""
    print(f"\n🔍 CASO: '{pregunta}'")
    print("-" * 50)
    
    # Simular la función obtener_conocimiento_completo
    original_obtener = sistema.obtener_conocimiento_completo
    sistema.obtener_conocimiento_completo = simular_base_conocimiento
    
    try:
        respuesta = sistema.procesar_pregunta(pregunta)
        
        if respuesta:
            print(f"✅ RESPUESTA INTELIGENTE:")
            print(respuesta)
        else:
            print("⚪ Sin respuesta específica - IA normal procesaría")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        # Restaurar función original
        sistema.obtener_conocimiento_completo = original_obtener
    
    print("=" * 70)

def main():
    """Función principal de pruebas"""
    try:
        # Importar el sistema
        from clientes.aura.utils.respuestas_inteligentes import SistemaRespuestasInteligentes
        
        print("🎯 PROBANDO SISTEMA DE RESPUESTAS ESPECÍFICAS")
        print("=" * 70)
        
        # Inicializar sistema
        sistema = SistemaRespuestasInteligentes("aura")
        
        # Casos de prueba específicos
        casos_prueba = [
            ("¿Cuánto cuesta el curso de marketing?", "Debe responder SOLO el precio del curso de marketing"),
            ("¿Cuánto cuesta el curso de inteligencia artificial?", "Debe responder SOLO el precio del curso de IA"),
            ("¿Dónde está el curso de marketing?", "Debe responder SOLO la ubicación del curso de marketing"),
            ("¿Qué horarios tiene el curso de IA?", "Debe responder SOLO los horarios del curso de IA"),
            ("¿Cuánto cuestan los cursos?", "Debe listar precios de todos los cursos disponibles"),
            ("Información sobre marketing digital", "Debe dar información completa del curso de marketing"),
            ("¿Cuánto cuesta un curso?", "Debe preguntar cuál curso o listar opciones"),
            ("¿Dónde están ubicados?", "Debe dar información de ubicación general"),
        ]
        
        for pregunta, descripcion in casos_prueba:
            probar_caso_especifico(sistema, pregunta, descripcion)
        
        print("\n🎉 PRUEBAS COMPLETADAS")
        print("✅ El sistema ahora debería responder específicamente a lo que pregunta el usuario")
        print("📋 Las respuestas deben ser EXACTAS y no incluir información extra no solicitada")
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de estar en el directorio correcto del proyecto")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()
