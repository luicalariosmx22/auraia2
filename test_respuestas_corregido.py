"""
Script de demostración del Sistema de Respuestas Inteligentes - VERSIÓN CORREGIDA
Simula datos reales y muestra cómo Nora lee el CONTENIDO de los bloques con etiquetas específicas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Mock de Supabase para la demostración
class MockSupabase:
    def __init__(self):
        self.mock_data = [
            {
                'id': 'curso_ia_1',
                'contenido': 'Nuestro Curso de Inteligencia Artificial tiene una duración de 6 semanas presenciales. Incluye teoría y práctica con proyectos reales.',
                'etiquetas': ['Curso Inteligencia Artificial', 'Presencial', 'Duración'],
                'prioridad': True
            },
            {
                'id': 'curso_ia_2', 
                'contenido': 'El costo del Curso de Inteligencia Artificial es de $15,000 MXN. Incluye materiales, certificación y acceso a la plataforma por 1 año.',
                'etiquetas': ['Curso Inteligencia Artificial', 'Precio', 'Certificación'],
                'prioridad': True
            },
            {
                'id': 'curso_ia_3',
                'contenido': 'Las clases se imparten en nuestras instalaciones en Av. Revolución #1234, Col. Centro, Guadalajara. Horarios: Lunes a Viernes 6:00-9:00 PM.',
                'etiquetas': ['Curso Inteligencia Artificial', 'Ubicación', 'Horarios'],
                'prioridad': False
            },
            {
                'id': 'curso_marketing_1',
                'contenido': 'Curso de Marketing Digital: 4 semanas intensivas. Aprende estrategias de redes sociales, Google Ads y email marketing.',
                'etiquetas': ['Marketing Digital', 'Curso', 'Estrategias'],
                'prioridad': False
            },
            {
                'id': 'curso_marketing_2',
                'contenido': 'Precio del Curso de Marketing Digital: $8,500 MXN. Incluye acceso a herramientas premium y proyecto final.',
                'etiquetas': ['Marketing Digital', 'Precio', 'Herramientas'],
                'prioridad': False
            }
        ]
    
    def table(self, table_name):
        return self
    
    def select(self, fields):
        return self
    
    def eq(self, field, value):
        return self
    
    def execute(self):
        class MockResponse:
            def __init__(self, data):
                self.data = data
        return MockResponse(self.mock_data)

# Usar mock en lugar de Supabase real
import clientes.aura.utils.respuestas_inteligentes as ri_module
ri_module.supabase = MockSupabase()

from clientes.aura.utils.respuestas_inteligentes import SistemaRespuestasInteligentes

def probar_sistema_mejorado():
    print("🎯 DEMOSTRACIÓN: Sistema de Respuestas Inteligentes CORREGIDO")
    print("=" * 70)
    print("📋 Datos simulados:")
    print("   • Curso de IA: duración, precio, ubicación (etiquetas internas)")
    print("   • Curso de Marketing: duración, precio (etiquetas internas)")
    print("   • Nora lee el CONTENIDO de los bloques, no muestra las etiquetas")
    print()
    
    sistema = SistemaRespuestasInteligentes("aura")
    
    # Casos de prueba
    casos_prueba = [
        "¿Cuánto cuesta un curso?",
        "¿Cuánto cuesta el curso de inteligencia artificial?", 
        "¿Qué cursos tienen disponibles?",
        "¿Dónde está ubicado el curso de IA?",
        "¿Cuál es la duración del curso de inteligencia artificial?",
        "¿Cuánto cuesta el curso de marketing?",
        "Información sobre inteligencia artificial"
    ]
    
    for i, pregunta in enumerate(casos_prueba, 1):
        print(f"🔍 CASO {i}: '{pregunta}'")
        print("-" * 50)
        
        # Procesar pregunta
        respuesta = sistema.procesar_pregunta(pregunta)
        
        if respuesta:
            print("✅ RESPUESTA INTELIGENTE:")
            print(respuesta)
        else:
            print("⚪ Procesaría con IA normal")
        
        print()
        print("=" * 70)
        print()

if __name__ == "__main__":
    probar_sistema_mejorado()
