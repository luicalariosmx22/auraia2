#!/usr/bin/env python3
"""
🧪 Prueba del Sistema de Formularios Conversacionales
Prueba la creación de tareas paso a paso
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clientes.aura.utils.detector_intenciones import detector_intenciones
from clientes.aura.utils.formulario_conversacional import crear_formulario_tarea, tiene_formulario_activo, obtener_formulario_activo
from clientes.aura.utils.supabase_client import supabase

def simular_usuario_cliente():
    """Simula datos de un usuario cliente"""
    return {
        "tipo": "usuario_cliente",
        "nombre": "Test User",
        "empresa_id": "test-empresa-id",
        "telefono": "+1234567890",
        "rol": "empleado",
        "nombre_nora": "aura"
    }

def simular_usuario_admin():
    """Simula datos de un usuario admin"""
    return {
        "tipo": "admin",
        "nombre": "Admin User",
        "telefono": "+0987654321",
        "rol": "admin",
        "nombre_nora": "aura",
        "admin_total": True
    }

def test_deteccion_intenciones():
    """Prueba la detección de intenciones"""
    print("🧪 PRUEBA: Detección de Intenciones")
    print("=" * 50)
    
    usuario_test = simular_usuario_cliente()
    
    mensajes_crear_tarea = [
        "Quiero crear una nueva tarea",
        "Crear tarea para revisar el reporte",
        "Nueva tarea: Llamar a cliente",
        "Necesito registrar una tarea urgente",
        "Agregar tarea",
        "Tarea nueva para mañana"
    ]
    
    mensajes_normales = [
        "Hola, ¿cómo estás?",
        "¿Cuál es el estado del proyecto?",
        "Necesito ayuda con algo",
        "Gracias por la información"
    ]
    
    print("\n📝 Mensajes que DEBEN detectar creación de tarea:")
    for mensaje in mensajes_crear_tarea:
        es_crear = detector_intenciones.es_mensaje_crear_tarea(mensaje, usuario_test)
        contexto = detector_intenciones.extraer_contexto_tarea(mensaje)
        status = "✅" if es_crear else "❌"
        print(f"  {status} '{mensaje}' -> {es_crear}")
        if contexto:
            print(f"      Contexto: {contexto}")
    
    print("\n💬 Mensajes que NO deben detectar creación de tarea:")
    for mensaje in mensajes_normales:
        es_crear = detector_intenciones.es_mensaje_crear_tarea(mensaje, usuario_test)
        status = "✅" if not es_crear else "❌"
        print(f"  {status} '{mensaje}' -> {es_crear}")

def test_formulario_completo():
    """Prueba el flujo completo del formulario"""
    print("\n🧪 PRUEBA: Formulario Completo")
    print("=" * 50)
    
    telefono_test = "+1234567890"
    usuario_test = simular_usuario_admin()
    
    # Limpiar estado previo si existe
    from clientes.aura.utils.gestor_estados import gestor_estados
    gestor_estados.limpiar_estado(telefono_test)
    
    # Crear formulario
    print("\n1️⃣ Creando formulario...")
    formulario = crear_formulario_tarea(usuario_test)
    primera_pregunta = formulario.iniciar_formulario(telefono_test)
    print(f"Primera pregunta: {primera_pregunta}")
    
    # Simular respuestas paso a paso
    respuestas_simuladas = [
        "Revisar el reporte mensual",
        "Revisar todos los datos del mes anterior y generar el reporte ejecutivo",
        "Empresa Test",
        "Juan Pérez",
        "Alta",
        "mañana"
    ]
    
    print(f"\n2️⃣ Simulando respuestas paso a paso...")
    for i, respuesta in enumerate(respuestas_simuladas):
        print(f"\n--- Paso {i+1} ---")
        print(f"Respuesta usuario: '{respuesta}'")
        
        if tiene_formulario_activo(telefono_test):
            formulario_activo = obtener_formulario_activo(telefono_test)
            siguiente_pregunta = formulario_activo.procesar_respuesta(telefono_test, respuesta)
            print(f"Siguiente pregunta: {siguiente_pregunta}")
            
            if not tiene_formulario_activo(telefono_test):
                print("🎉 ¡Formulario completado!")
                break
        else:
            print("❌ No hay formulario activo")
            break

def test_contexto_extracto():
    """Prueba la extracción de contexto de mensajes"""
    print("\n🧪 PRUEBA: Extracción de Contexto")
    print("=" * 50)
    
    mensajes_con_contexto = [
        'Crear tarea "Revisar contratos urgente"',
        "Nueva tarea para Juan: revisar el reporte",
        "Tarea urgente para mañana: llamar cliente",
        "Necesito recordar que hay que actualizar la web",
        "Agregar tarea prioridad alta para la próxima semana"
    ]
    
    for mensaje in mensajes_con_contexto:
        contexto = detector_intenciones.extraer_contexto_tarea(mensaje)
        print(f"\n📝 Mensaje: '{mensaje}'")
        print(f"   Contexto extraído: {contexto}")
        
        # Generar mensaje de bienvenida
        bienvenida = detector_intenciones.generar_mensaje_bienvenida_tarea(contexto)
        print(f"   Bienvenida generada:\n{bienvenida}")

def test_validadores():
    """Prueba los validadores del formulario"""
    print("\n🧪 PRUEBA: Validadores")
    print("=" * 50)
    
    from clientes.aura.utils.formulario_conversacional import validar_fecha
    
    fechas_validas = [
        "hoy", "mañana", "15/12/2024", "2024-12-15", 
        "la próxima semana", "25/12"
    ]
    
    fechas_invalidas = [
        "ayer imposible", "32/15/2024", "fecha mala", "xyz"
    ]
    
    print("\n📅 Fechas válidas:")
    for fecha in fechas_validas:
        es_valida = validar_fecha(fecha, {})
        status = "✅" if es_valida else "❌"
        print(f"  {status} '{fecha}'")
    
    print("\n📅 Fechas inválidas:")
    for fecha in fechas_invalidas:
        es_valida = validar_fecha(fecha, {})
        status = "✅" if not es_valida else "❌"
        print(f"  {status} '{fecha}'")

def main():
    """Ejecuta todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE FORMULARIOS CONVERSACIONALES")
    print("=" * 70)
    
    try:
        test_deteccion_intenciones()
        test_contexto_extracto()
        test_validadores()
        test_formulario_completo()
        
        print("\n🎉 TODAS LAS PRUEBAS COMPLETADAS")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
