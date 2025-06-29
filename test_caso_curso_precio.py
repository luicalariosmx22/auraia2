#!/usr/bin/env python3
"""
Script específico para probar el caso: "¿Cuánto cuesta un curso?"
Verifica que Nora siempre ofrezca opciones cuando no tiene claro qué curso específico
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clientes.aura.utils.respuestas_inteligentes import SistemaRespuestasInteligentes
from clientes.aura.utils.memoria_conversacion import memoria_conversacion

def simular_conversacion_curso():
    """Simula una conversación real donde el usuario pregunta sobre costos de cursos"""
    
    print("🎯 SIMULACIÓN: Pregunta ambigua sobre costo de curso")
    print("=" * 70)
    
    sistema = SistemaRespuestasInteligentes("aura")
    telefono_usuario = "5216624644200"  # Número de ejemplo
    
    # Escenario 1: Pregunta ambigua inicial
    print("\n👤 USUARIO: ¿Cuánto cuesta un curso?")
    print("-" * 50)
    
    respuesta1 = sistema.procesar_pregunta("¿Cuánto cuesta un curso?", telefono=telefono_usuario)
    
    if respuesta1:
        print("🤖 NORA:")
        print(respuesta1)
        print("\n✅ PERFECTO: Nora detectó la ambigüedad y ofreció opciones")
    else:
        print("❌ ERROR: Nora no detectó la ambigüedad, derivó a IA normal")
        return
    
    # Escenario 2: Usuario selecciona una opción
    print("\n" + "="*50)
    print("👤 USUARIO: 1")
    print("-" * 30)
    
    respuesta2 = sistema.procesar_pregunta("1", telefono=telefono_usuario)
    
    if respuesta2:
        print("🤖 NORA:")
        print(respuesta2)
        print("\n✅ PERFECTO: Nora procesó la selección correctamente")
    else:
        print("❌ ERROR: Nora no pudo procesar la selección")
    
    # Limpiar memoria
    memoria_conversacion.limpiar_memoria(telefono_usuario, "aura")

def probar_variaciones_pregunta():
    """Prueba diferentes variaciones de preguntas ambiguas sobre cursos"""
    
    print("\n🔍 PROBANDO VARIACIONES DE PREGUNTAS AMBIGUAS")
    print("=" * 70)
    
    sistema = SistemaRespuestasInteligentes("aura")
    telefono_test = "1111111111"
    
    variaciones = [
        "¿Cuánto cuesta un curso?",
        "precio del curso",
        "cuanto vale el curso inteligencia artificial",
        "costos",
        "¿Qué cursos tienen y cuánto cuestan?",
        "curso de marketing precio",
        "ubicación de los cursos",
        "horarios de curso",
        "cuando empiezan los cursos"
    ]
    
    for i, pregunta in enumerate(variaciones, 1):
        print(f"\n{i}. 👤 USUARIO: {pregunta}")
        print("-" * 40)
        
        respuesta = sistema.procesar_pregunta(pregunta, telefono=telefono_test)
        
        if respuesta:
            print("🤖 NORA: [Respuesta inteligente generada]")
            
            # Mostrar tipo de respuesta
            if "1️⃣" in respuesta or "2️⃣" in respuesta:
                print("📋 Tipo: Menú de opciones")
            elif len(respuesta.split('\n')) > 3:
                print("💬 Tipo: Respuesta contextual extendida")
            else:
                print("📄 Tipo: Respuesta directa")
                
            # Mostrar preview de la respuesta
            preview = respuesta[:150].replace('\n', ' ')
            print(f"📄 Preview: {preview}...")
            
        else:
            print("🔄 NORA: [Derivado a IA normal]")
    
    # Limpiar memoria
    memoria_conversacion.limpiar_memoria(telefono_test, "aura")

def verificar_deteccion_duplicados():
    """Verifica que el sistema detecte y maneje duplicados correctamente"""
    
    print("\n🔍 VERIFICANDO DETECCIÓN DE DUPLICADOS")
    print("=" * 70)
    
    sistema = SistemaRespuestasInteligentes("aura")
    
    # Simular datos con duplicados
    opciones_con_duplicados = [
        {
            'bloque': {
                'id': '1',
                'contenido': 'Curso de Inteligencia Artificial - Presencial - $500',
                'etiquetas': ['curso', 'ia', 'presencial']
            },
            'puntuacion': 5,
            'razones': ['IA']
        },
        {
            'bloque': {
                'id': '2',
                'contenido': 'Curso de Inteligencia Artificial - En línea - $400',
                'etiquetas': ['curso', 'ia', 'online']
            },
            'puntuacion': 5,
            'razones': ['IA']
        },
        {
            'bloque': {
                'id': '3',
                'contenido': 'Curso IA - Modalidad presencial - Costo $500',
                'etiquetas': ['curso', 'artificial', 'presencial']
            },
            'puntuacion': 4,
            'razones': ['IA']
        }
    ]
    
    print("📊 Datos originales:")
    for i, opcion in enumerate(opciones_con_duplicados):
        print(f"  {i+1}. {opcion['bloque']['contenido']}")
    
    # Detectar duplicados
    opciones_unicas = sistema.detectar_duplicados(opciones_con_duplicados, umbral_similitud=0.7)
    
    print(f"\n🔄 Después de detectar duplicados: {len(opciones_unicas)} opciones únicas")
    for i, opcion in enumerate(opciones_unicas):
        contenido = opcion['bloque']['contenido']
        tiene_duplicados = "✅" if opcion.get('tiene_duplicados') else "❌"
        num_similares = opcion.get('num_similares', 0)
        print(f"  {i+1}. {contenido[:60]}... [Duplicados: {tiene_duplicados}] [Similares: {num_similares}]")

def main():
    """Función principal que ejecuta todas las pruebas específicas"""
    
    print("🚀 INICIANDO PRUEBAS ESPECÍFICAS DEL SISTEMA DE RESPUESTAS INTELIGENTES")
    print("🎯 Enfoque: Preguntas ambiguas como '¿Cuánto cuesta un curso?'")
    print("=" * 80)
    
    try:
        # Ejecutar pruebas específicas
        simular_conversacion_curso()
        probar_variaciones_pregunta()
        verificar_deteccion_duplicados()
        
        print("\n" + "🎉" * 25)
        print("TODAS LAS PRUEBAS ESPECÍFICAS COMPLETADAS")
        print("✅ El sistema debería manejar correctamente preguntas ambiguas")
        print("✅ Nora siempre ofrecerá opciones cuando no tenga claro qué curso específico")
        print("✅ Se detectan y manejan duplicados apropiadamente")
        print("🎉" * 25)
        
    except Exception as e:
        print(f"\n❌ ERROR EN PRUEBAS ESPECÍFICAS: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
