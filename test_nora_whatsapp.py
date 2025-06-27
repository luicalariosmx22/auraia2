#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTER DE NORA - WhatsApp Response Test
Simula un mensaje de WhatsApp para verificar que Nora responda correctamente
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clientes.aura.handlers.process_message import procesar_mensaje
from clientes.aura.handlers.handle_ai import manejar_respuesta_ai, obtener_configuracion_nora
from clientes.aura.utils.chat.buscar_conocimiento import obtener_base_conocimiento

def test_configuracion_nora():
    """Test 1: Verificar que se puede obtener la configuración de Nora"""
    print("=" * 60)
    print("🧪 TEST 1: Configuración de Nora")
    print("=" * 60)
    
    try:
        nombre_nora = "aura"
        personalidad, instrucciones, modo_respuesta, mensaje_fuera_tema = obtener_configuracion_nora(nombre_nora)
        
        print(f"✅ Configuración obtenida para '{nombre_nora}':")
        print(f"   📝 Personalidad: {personalidad[:100]}...")
        print(f"   📋 Instrucciones: {instrucciones[:100]}...")
        print(f"   ⚙️ Modo respuesta: {modo_respuesta}")
        print(f"   🚫 Mensaje fuera tema: {mensaje_fuera_tema[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

def test_base_conocimiento():
    """Test 2: Verificar que se puede obtener la base de conocimiento"""
    print("\n" + "=" * 60)
    print("🧪 TEST 2: Base de Conocimiento")
    print("=" * 60)
    
    try:
        nombre_nora = "aura"
        base_conocimiento = obtener_base_conocimiento(nombre_nora)
        
        print(f"✅ Base de conocimiento obtenida:")
        print(f"   📚 Total de bloques: {len(base_conocimiento)}")
        
        if base_conocimiento:
            print(f"   📄 Primer bloque: {base_conocimiento[0].get('contenido', 'Sin contenido')[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Error en base de conocimiento: {e}")
        return False

def test_ia_directa():
    """Test 3: Probar la IA directamente"""
    print("\n" + "=" * 60)
    print("🧪 TEST 3: Respuesta de IA Directa")
    print("=" * 60)
    
    try:
        mensaje_test = "Hola, ¿qué servicios ofrecen?"
        nombre_nora = "aura"
        
        print(f"💬 Mensaje de prueba: '{mensaje_test}'")
        print(f"🤖 Nombre Nora: '{nombre_nora}'")
        
        respuesta, historial = manejar_respuesta_ai(
            mensaje_usuario=mensaje_test,
            nombre_nora=nombre_nora
        )
        
        print(f"✅ Respuesta generada:")
        print(f"   📝 Respuesta: {respuesta}")
        print(f"   📚 Historial: {len(historial)} mensajes")
        
        return True, respuesta
    except Exception as e:
        print(f"❌ Error en IA directa: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_proceso_completo():
    """Test 4: Simular el proceso completo de WhatsApp"""
    print("\n" + "=" * 60)
    print("🧪 TEST 4: Proceso Completo WhatsApp")
    print("=" * 60)
    
    try:
        # Simular datos de WhatsApp
        datos_whatsapp = {
            "From": "whatsapp:+5215512345678",  # Número del usuario
            "To": "whatsapp:+5215593372311",    # Número de Nora (debe estar en la BD)
            "Body": "Hola, necesito información sobre sus servicios",
            "ProfileName": "Usuario Test",
            "ProfilePicUrl": None
        }
        
        print(f"📱 Simulando mensaje de WhatsApp:")
        print(f"   👤 De: {datos_whatsapp['From']}")
        print(f"   🤖 Para: {datos_whatsapp['To']}")
        print(f"   💬 Mensaje: {datos_whatsapp['Body']}")
        
        # Procesar el mensaje
        respuesta = procesar_mensaje(datos_whatsapp)
        
        print(f"✅ Proceso completado:")
        print(f"   📝 Respuesta final: {respuesta}")
        
        return True
    except Exception as e:
        print(f"❌ Error en proceso completo: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_verificar_bd():
    """Test 5: Verificar que los datos estén en la base de datos"""
    print("\n" + "=" * 60)
    print("🧪 TEST 5: Verificación de Base de Datos")
    print("=" * 60)
    
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        # Verificar configuración_bot
        response = supabase.table("configuracion_bot").select("*").eq("nombre_nora", "aura").execute()
        
        if response.data:
            config = response.data[0]
            print(f"✅ Configuración encontrada:")
            print(f"   🤖 Nombre: {config.get('nombre_nora')}")
            print(f"   📞 Número: {config.get('numero_nora')}")
            print(f"   ✅ IA Activa: {config.get('ia_activa', 'No definido')}")
            print(f"   ⚙️ Modo: {config.get('modo_respuesta', 'No definido')}")
        else:
            print("❌ No se encontró configuración para 'aura'")
            return False
        
        # Verificar conocimiento_nora
        response_conocimiento = supabase.table("conocimiento_nora").select("*").eq("nombre_nora", "aura").eq("activo", True).execute()
        
        print(f"📚 Bloques de conocimiento activos: {len(response_conocimiento.data)}")
        
        return True
    except Exception as e:
        print(f"❌ Error verificando BD: {e}")
        return False

def ejecutar_todos_los_tests():
    """Ejecutar todos los tests en secuencia"""
    print("🚀 INICIANDO TESTS DE NORA - WhatsApp Response")
    print("=" * 80)
    
    tests_pasados = 0
    total_tests = 5
    
    # Test 1: Configuración
    if test_configuracion_nora():
        tests_pasados += 1
    
    # Test 2: Base de conocimiento
    if test_base_conocimiento():
        tests_pasados += 1
    
    # Test 3: Verificar BD
    if test_verificar_bd():
        tests_pasados += 1
    
    # Test 4: IA directa
    exito_ia, respuesta = test_ia_directa()
    if exito_ia:
        tests_pasados += 1
    
    # Test 5: Proceso completo
    if test_proceso_completo():
        tests_pasados += 1
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE TESTS")
    print("=" * 80)
    print(f"✅ Tests pasados: {tests_pasados}/{total_tests}")
    
    if tests_pasados == total_tests:
        print("🎉 ¡TODOS LOS TESTS PASARON! Nora debería responder correctamente en WhatsApp.")
    else:
        print(f"⚠️ {total_tests - tests_pasados} tests fallaron. Revisa los errores arriba.")
    
    print("=" * 80)

if __name__ == "__main__":
    ejecutar_todos_los_tests()
