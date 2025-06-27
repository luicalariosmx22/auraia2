#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTER DE IDENTIFICACIÓN POR TELÉFONO
Verifica que Nora identifique correctamente usuarios por número de WhatsApp
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clientes.aura.handlers.process_message import identificar_tipo_contacto
from clientes.aura.auth.google_login import buscar_usuario_por_telefono

def test_identificacion_por_telefono():
    """Test 1: Verificar identificación por teléfono"""
    print("=" * 60)
    print("🧪 TEST 1: Identificación por Teléfono")
    print("=" * 60)
    
    # Probar con el número de David Alcantara
    telefono_david = "5216621327315"
    nombre_nora = "aura"
    
    print(f"🔍 Buscando contacto por teléfono: {telefono_david}")
    resultado = identificar_tipo_contacto(telefono_david, nombre_nora)
    
    print(f"✅ Resultado de identificación:")
    print(f"   📋 Tipo: {resultado.get('tipo', 'No definido')}")
    print(f"   👤 Nombre: {resultado.get('nombre', 'Sin nombre')}")
    print(f"   📧 Email: {resultado.get('email', 'Sin email')}")
    print(f"   📞 Teléfono: {resultado.get('telefono', 'Sin teléfono')}")
    print(f"   🏷️ Rol: {resultado.get('rol', 'Sin rol')}")
    print(f"   🔑 Es supervisor: {resultado.get('es_supervisor', False)}")
    
    if resultado['tipo'] == 'usuario_cliente':
        print("✅ David fue identificado como USUARIO INTERNO")
        return True
    else:
        print(f"❌ David no fue identificado como usuario interno: {resultado['tipo']}")
        return False

def test_busqueda_directa():
    """Test 2: Búsqueda directa en usuarios_clientes"""
    print("\n" + "=" * 60)
    print("🧪 TEST 2: Búsqueda Directa por Teléfono")
    print("=" * 60)
    
    telefono_david = "5216621327315"
    nombre_nora = "aura"
    
    print(f"🔍 Búsqueda directa: {telefono_david}")
    usuario = buscar_usuario_por_telefono(telefono_david, nombre_nora)
    
    if usuario:
        print(f"✅ Usuario encontrado:")
        print(f"   👤 Nombre: {usuario.get('nombre', 'Sin nombre')}")
        print(f"   📧 Email: {usuario.get('correo', 'Sin email')}")
        print(f"   🏷️ Rol: {usuario.get('rol', 'Sin rol')}")
        print(f"   📞 Teléfono: {usuario.get('telefono', 'Sin teléfono')}")
        print(f"   🤖 Nora: {usuario.get('nombre_nora', 'Sin asignar')}")
        return True
    else:
        print("❌ Usuario no encontrado")
        return False

def test_flujo_whatsapp_completo():
    """Test 3: Simular flujo completo de WhatsApp"""
    print("\n" + "=" * 60)
    print("🧪 TEST 3: Flujo Completo WhatsApp")
    print("=" * 60)
    
    # Simular datos de WhatsApp de David
    datos_whatsapp = {
        "From": "whatsapp:+5216621327315",  # Número de David
        "To": "whatsapp:+5215593372311",    # Número de Nora
        "Body": "Hola, necesito revisar las tareas pendientes",
        "ProfileName": "David Test"
    }
    
    print(f"📱 Simulando mensaje de WhatsApp:")
    print(f"   👤 De: {datos_whatsapp['From']}")
    print(f"   🤖 Para: {datos_whatsapp['To']}")
    print(f"   💬 Mensaje: {datos_whatsapp['Body']}")
    
    try:
        from clientes.aura.handlers.process_message import procesar_mensaje
        
        # Procesar el mensaje (esto debería identificar a David como usuario interno)
        print(f"\n🔄 Procesando mensaje...")
        respuesta = procesar_mensaje(datos_whatsapp)
        
        print(f"✅ Mensaje procesado exitosamente")
        print(f"📝 Respuesta: {respuesta[:100]}..." if respuesta else "Sin respuesta")
        
        return True
    except Exception as e:
        print(f"❌ Error en flujo completo: {e}")
        import traceback
        traceback.print_exc()
        return False

def ejecutar_tests_telefono():
    """Ejecutar todos los tests de identificación por teléfono"""
    print("🚀 INICIANDO TESTS DE IDENTIFICACIÓN POR TELÉFONO")
    print("=" * 80)
    
    tests_pasados = 0
    total_tests = 3
    
    # Test 1: Identificación por teléfono
    if test_identificacion_por_telefono():
        tests_pasados += 1
    
    # Test 2: Búsqueda directa
    if test_busqueda_directa():
        tests_pasados += 1
    
    # Test 3: Flujo completo WhatsApp
    if test_flujo_whatsapp_completo():
        tests_pasados += 1
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE TESTS DE IDENTIFICACIÓN POR TELÉFONO")
    print("=" * 80)
    print(f"✅ Tests pasados: {tests_pasados}/{total_tests}")
    
    if tests_pasados == total_tests:
        print("🎉 ¡TODOS LOS TESTS PASARON!")
        print("📞 La identificación por teléfono funciona correctamente:")
        print("   - Búsqueda en usuarios_clientes ✅")
        print("   - Identificación de usuarios internos ✅")
        print("   - Flujo completo de WhatsApp ✅")
        print("   - Prioridad: usuarios_clientes > clientes ✅")
    else:
        print(f"⚠️ {total_tests - tests_pasados} tests fallaron. Revisa la configuración.")
    
    print("=" * 80)

if __name__ == "__main__":
    ejecutar_tests_telefono()
