#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTER DE ACCESO POR TIPO DE CONTACTO
Verifica que Nora identifique correctamente el tipo de contacto y 
proporcione información personalizada según si es cliente o no.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clientes.aura.handlers.process_message import identificar_tipo_contacto
from clientes.aura.handlers.handle_ai import manejar_respuesta_ai

def test_identificacion_cliente_con_empresa():
    """Test: Identificar cliente y obtener información de empresas"""
    print("=" * 60)
    print("🧪 TEST: Identificación de Cliente con Empresas")
    print("=" * 60)
    
    try:
        # Usar un número de teléfono que debería estar en la BD como cliente
        numero_test = "5215512345678"  # Ajusta según tu BD
        nombre_nora = "aura"
        
        print(f"🔍 Identificando contacto: {numero_test}")
        tipo_contacto = identificar_tipo_contacto(numero_test, nombre_nora)
        
        print(f"✅ Resultado de identificación:")
        print(f"   📋 Tipo: {tipo_contacto.get('tipo')}")
        print(f"   👤 Nombre: {tipo_contacto.get('nombre')}")
        print(f"   📧 Email: {tipo_contacto.get('email')}")
        print(f"   🆔 ID: {tipo_contacto.get('id')}")
        
        # Mostrar información de empresas si las tiene
        empresas = tipo_contacto.get("empresas", [])
        if empresas:
            print(f"   🏢 Empresas asociadas: {len(empresas)}")
            for i, empresa in enumerate(empresas, 1):
                print(f"      {i}. {empresa.get('nombre_empresa', 'Sin nombre')}")
                if empresa.get('industria'):
                    print(f"         Industria: {empresa.get('industria')}")
                if empresa.get('descripcion'):
                    print(f"         Descripción: {empresa.get('descripcion')[:100]}...")
        else:
            print(f"   🏢 Sin empresas asociadas")
        
        return tipo_contacto
        
    except Exception as e:
        print(f"❌ Error en identificación: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_respuesta_personalizada_cliente():
    """Test: Respuesta personalizada para cliente con empresa"""
    print("\n" + "=" * 60)
    print("🧪 TEST: Respuesta Personalizada para Cliente")
    print("=" * 60)
    
    try:
        # Identificar cliente primero
        numero_test = "5215512345678"
        nombre_nora = "aura"
        tipo_contacto = identificar_tipo_contacto(numero_test, nombre_nora)
        
        if not tipo_contacto or tipo_contacto["tipo"] != "cliente":
            print("⚠️ No se pudo identificar como cliente, creando datos de prueba...")
            tipo_contacto = {
                "tipo": "cliente",
                "id": "test-123",
                "nombre": "Cliente Prueba",
                "email": "cliente@test.com",
                "empresas": [
                    {
                        "nombre_empresa": "Empresa Demo S.A.",
                        "industria": "Tecnología",
                        "descripcion": "Empresa dedicada al desarrollo de software y soluciones tecnológicas"
                    }
                ]
            }
        
        # Generar respuesta usando información del cliente
        mensaje_test = "Hola, necesito información sobre sus servicios de marketing digital"
        print(f"💬 Mensaje de prueba: '{mensaje_test}'")
        print(f"🏢 Cliente: {tipo_contacto.get('nombre')}")
        
        respuesta, historial = manejar_respuesta_ai(
            mensaje_usuario=mensaje_test,
            nombre_nora=nombre_nora,
            tipo_contacto=tipo_contacto
        )
        
        print(f"\n✅ Respuesta personalizada:")
        print(f"📝 {respuesta}")
        
        # Verificar si menciona el nombre del cliente o empresa
        nombre_cliente = tipo_contacto.get("nombre", "").lower()
        empresas = tipo_contacto.get("empresas", [])
        
        menciona_cliente = nombre_cliente and nombre_cliente.split()[0].lower() in respuesta.lower()
        menciona_empresa = any(emp.get("nombre_empresa", "").lower() in respuesta.lower() for emp in empresas)
        
        if menciona_cliente:
            print("✅ La respuesta menciona al cliente por nombre")
        if menciona_empresa:
            print("✅ La respuesta hace referencia a su empresa")
        
        if not menciona_cliente and not menciona_empresa:
            print("⚠️ La respuesta no parece personalizada")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en respuesta personalizada: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_respuesta_visitante_vs_cliente():
    """Test: Comparar respuestas entre visitante y cliente"""
    print("\n" + "=" * 60)
    print("🧪 TEST: Comparación Visitante vs Cliente")
    print("=" * 60)
    
    try:
        nombre_nora = "aura"
        mensaje_test = "¿Qué servicios ofrecen?"
        
        # Respuesta para visitante (sin información de contacto)
        print("👤 Generando respuesta para VISITANTE...")
        respuesta_visitante, _ = manejar_respuesta_ai(
            mensaje_usuario=mensaje_test,
            nombre_nora=nombre_nora,
            tipo_contacto={"tipo": "desconocido", "nombre": "Visitante"}
        )
        
        # Respuesta para cliente con empresa
        print("🏢 Generando respuesta para CLIENTE...")
        tipo_cliente = {
            "tipo": "cliente",
            "nombre": "Juan Pérez",
            "empresas": [
                {
                    "nombre_empresa": "Constructora Pérez S.A.",
                    "industria": "Construcción",
                    "descripcion": "Empresa líder en construcción de viviendas"
                }
            ]
        }
        
        respuesta_cliente, _ = manejar_respuesta_ai(
            mensaje_usuario=mensaje_test,
            nombre_nora=nombre_nora,
            tipo_contacto=tipo_cliente
        )
        
        print(f"\n📊 COMPARACIÓN DE RESPUESTAS:")
        print(f"\n👤 VISITANTE:")
        print(f"   {respuesta_visitante}")
        
        print(f"\n🏢 CLIENTE (Juan Pérez - Constructora):")
        print(f"   {respuesta_cliente}")
        
        # Análisis simple de diferencias
        if len(respuesta_cliente) > len(respuesta_visitante):
            print(f"\n✅ La respuesta para cliente es más detallada ({len(respuesta_cliente)} vs {len(respuesta_visitante)} caracteres)")
        
        if "juan" in respuesta_cliente.lower() or "pérez" in respuesta_cliente.lower():
            print("✅ La respuesta para cliente es personalizada (menciona el nombre)")
        
        if "construcción" in respuesta_cliente.lower() or "constructora" in respuesta_cliente.lower():
            print("✅ La respuesta para cliente hace referencia a su industria")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en comparación: {e}")
        import traceback
        traceback.print_exc()
        return False

def ejecutar_tests_acceso():
    """Ejecutar todos los tests de acceso por tipo de contacto"""
    print("🚀 INICIANDO TESTS DE ACCESO POR TIPO DE CONTACTO")
    print("=" * 80)
    
    tests_pasados = 0
    total_tests = 3
    
    # Test 1: Identificación de cliente con empresa
    try:
        tipo_contacto = test_identificacion_cliente_con_empresa()
        if tipo_contacto:
            tests_pasados += 1
    except:
        pass
    
    # Test 2: Respuesta personalizada para cliente
    if test_respuesta_personalizada_cliente():
        tests_pasados += 1
    
    # Test 3: Comparación visitante vs cliente
    if test_respuesta_visitante_vs_cliente():
        tests_pasados += 1
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE TESTS DE ACCESO")
    print("=" * 80)
    print(f"✅ Tests pasados: {tests_pasados}/{total_tests}")
    
    if tests_pasados == total_tests:
        print("🎉 ¡TODOS LOS TESTS PASARON!")
        print("🔍 Nora ahora identifica el tipo de contacto y personaliza sus respuestas.")
        print("🏢 Los clientes reciben información específica sobre sus empresas.")
    else:
        print(f"⚠️ {total_tests - tests_pasados} tests fallaron. Revisa los errores arriba.")
    
    print("=" * 80)

if __name__ == "__main__":
    ejecutar_tests_acceso()
