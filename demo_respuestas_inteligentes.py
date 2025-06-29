#!/usr/bin/env python3
"""
🎯 DEMOSTRACIÓN COMPLETA DEL SISTEMA DE RESPUESTAS INTELIGENTES
Este script demuestra exactamente cómo Nora maneja preguntas ambiguas como:
"¿cuánto cuesta un curso?" y siempre ofrece opciones al usuario.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clientes.aura.utils.respuestas_inteligentes import SistemaRespuestasInteligentes
from clientes.aura.utils.memoria_conversacion import memoria_conversacion

def demostrar_conversacion_completa():
    """Demuestra una conversación completa desde pregunta ambigua hasta respuesta específica"""
    
    print("=" * 80)
    print("🎯 DEMOSTRACIÓN: Conversación Inteligente con Nora")
    print("=" * 80)
    
    # Simular datos de usuario
    telefono_usuario = "+5216624644200"  # Tu número
    nombre_nora = "aura"
    
    # Inicializar sistema
    sistema = SistemaRespuestasInteligentes(nombre_nora)
    
    # === ESCENARIO 1: Pregunta ambigua inicial ===
    print("\n👤 USUARIO: '¿Cuánto cuesta un curso?'")
    print("-" * 50)
    
    mensaje1 = "¿Cuánto cuesta un curso?"
    
    # Limpiar memoria previa (nueva conversación)
    memoria_conversacion.limpiar_memoria(telefono_usuario, nombre_nora)
    
    # Procesar pregunta
    opciones_previas = memoria_conversacion.obtener_opciones(telefono_usuario, nombre_nora)
    respuesta1 = sistema.procesar_pregunta(mensaje1, opciones_previas)
    
    if respuesta1:
        print("🤖 NORA:")
        print(respuesta1)
        
        # Si es menú, guardar opciones en memoria
        if "1️⃣" in respuesta1:
            analisis = sistema.analizar_pregunta(mensaje1)
            opciones = sistema.buscar_opciones_relacionadas(analisis)
            opciones_unicas = sistema.detectar_duplicados(opciones)
            
            if opciones_unicas:
                resultado_memoria = memoria_conversacion.guardar_opciones(telefono_usuario, nombre_nora, opciones_unicas)
                print(f"\n💾 Memoria: Guardadas {len(opciones_unicas)} opciones ({'✅' if resultado_memoria else '❌'})")
    else:
        print("🤖 NORA: [Respuesta procesada por IA normal]")
    
    # === ESCENARIO 2: Usuario selecciona opción ===
    print("\n\n👤 USUARIO: '1'")
    print("-" * 50)
    
    mensaje2 = "1"
    
    # Obtener opciones de memoria
    opciones_previas = memoria_conversacion.obtener_opciones(telefono_usuario, nombre_nora)
    print(f"🧠 Memoria: {'✅ Recuperadas opciones' if opciones_previas else '❌ Sin opciones'}")
    
    # Procesar selección
    respuesta2 = sistema.procesar_pregunta(mensaje2, opciones_previas)
    
    if respuesta2:
        print("🤖 NORA:")
        print(respuesta2)
        
        # Limpiar memoria después de respuesta específica
        memoria_conversacion.limpiar_memoria(telefono_usuario, nombre_nora)
        print("\n🧹 Memoria: Limpiada después de respuesta específica")
    else:
        print("🤖 NORA: [Respuesta procesada por IA normal]")
    
    # === ESCENARIO 3: Nueva pregunta ambigua diferente ===
    print("\n\n👤 USUARIO: '¿Dónde son los cursos?'")
    print("-" * 50)
    
    mensaje3 = "¿Dónde son los cursos?"
    
    # Procesar nueva pregunta
    opciones_previas = memoria_conversacion.obtener_opciones(telefono_usuario, nombre_nora)  # Debería ser None
    respuesta3 = sistema.procesar_pregunta(mensaje3, opciones_previas)
    
    if respuesta3:
        print("🤖 NORA:")
        print(respuesta3)
    else:
        print("🤖 NORA: [Respuesta procesada por IA normal - no requiere opciones]")
    
    print("\n" + "=" * 80)
    print("✅ DEMOSTRACIÓN COMPLETADA")
    print("=" * 80)
    
    return True

def demostrar_casos_especificos():
    """Demuestra casos específicos de detección de ambigüedad"""
    
    print("\n🧪 CASOS DE PRUEBA ESPECÍFICOS")
    print("=" * 50)
    
    sistema = SistemaRespuestasInteligentes("aura")
    
    casos_prueba = [
        "¿Cuánto cuesta un curso?",
        "¿Cuánto cuesta el curso de IA?",
        "¿Dónde dan los cursos?",
        "¿Qué cursos tienen?",
        "Precio del curso inteligencia artificial",
        "¿Cuándo empieza el curso?",
        "Hola, buenos días",
        "¿Cómo están?",
        "Me interesa el marketing digital",
        "¿Tienen cursos presenciales?"
    ]
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n{i:2d}. 👤 '{caso}'")
        
        # Analizar pregunta
        analisis = sistema.analizar_pregunta(caso)
        respuesta = sistema.procesar_pregunta(caso, None)
        
        # Mostrar análisis
        flags = []
        if analisis['es_pregunta_precio']: flags.append("💰PRECIO")
        if analisis['es_pregunta_curso']: flags.append("📚CURSO")
        if analisis['es_pregunta_ubicacion']: flags.append("📍UBICACIÓN")
        if analisis['es_pregunta_horario']: flags.append("🕒HORARIO")
        if analisis['es_pregunta_ia']: flags.append("🤖IA")
        if analisis['es_pregunta_marketing']: flags.append("📈MARKETING")
        
        print(f"    🎯 Detección: {' + '.join(flags) if flags else 'GENERAL'}")
        
        if respuesta:
            print(f"    🤖 Respuesta: {'MENÚ DE OPCIONES' if '1️⃣' in respuesta else 'CLARIFICACIÓN'}")
        else:
            print(f"    🤖 Respuesta: IA NORMAL")
    
    print("\n✅ CASOS DE PRUEBA COMPLETADOS")

def verificar_configuracion():
    """Verifica que la configuración del sistema esté correcta"""
    
    print("\n🔧 VERIFICACIÓN DE CONFIGURACIÓN")
    print("=" * 40)
    
    try:
        # Verificar imports
        from clientes.aura.utils.supabase_client import supabase
        print("✅ Supabase client disponible")
        
        # Verificar tabla de conocimiento
        response = supabase.table("conocimiento_nora").select("count", count="exact").execute()
        print(f"✅ Base de conocimiento: {response.count} bloques")
        
        # Verificar memoria (opcional)
        try:
            memoria_conversacion.limpiar_memoria_expirada()
            print("✅ Sistema de memoria funcionando")
        except Exception as e:
            print(f"⚠️ Sistema de memoria (opcional): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO DEMOSTRACIÓN DEL SISTEMA DE RESPUESTAS INTELIGENTES")
    print("Este sistema hace que Nora SIEMPRE ofrezca opciones cuando hay ambigüedad\n")
    
    # Verificar configuración
    if not verificar_configuracion():
        print("❌ Configuración incorrecta, abortando...")
        sys.exit(1)
    
    # Ejecutar demostraciones
    try:
        demostrar_conversacion_completa()
        demostrar_casos_especificos()
        
        print("\n🎉 DEMOSTRACIÓN EXITOSA")
        print("📝 RESUMEN:")
        print("   • Nora detecta preguntas ambiguas automáticamente")
        print("   • Siempre ofrece opciones cuando no puede responder específicamente")
        print("   • Maneja memoria de conversación para seguimiento de menús")
        print("   • Funciona tanto en WhatsApp como en el panel web")
        
    except Exception as e:
        print(f"❌ Error durante demostración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
