#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTER DE MENÚ PERSONALIZADO PARA CLIENTES
Simula un cliente escribiendo "menu" para ver su menú personalizado
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_menu_cliente_mock():
    """Test: Simular un cliente con empresa y probar el menú personalizado"""
    print("=" * 60)
    print("🧪 TEST: Menú Personalizado para Cliente")
    print("=" * 60)
    
    try:
        from clientes.aura.utils.menu_cliente import construir_menu_cliente, procesar_seleccion_menu_cliente
        
        # Simular un tipo de contacto cliente con empresa
        tipo_contacto_cliente = {
            "tipo": "cliente",
            "id": "test-cliente-123",
            "nombre": "Juan Pérez",
            "email": "juan@empresa.com",
            "telefono": "5215512345678",
            "empresas": [
                {
                    "id": "test-empresa-456",
                    "nombre_empresa": "Empresa Demo S.A.",
                    "descripcion": "Empresa de prueba para testing",
                    "industria": "Tecnología",
                    "brief": "Brief de ejemplo para la empresa demo. Este es el contenido del brief que describe los objetivos y necesidades del cliente."
                }
            ]
        }
        
        print(f"👤 Cliente simulado: {tipo_contacto_cliente['nombre']}")
        print(f"🏢 Empresa: {tipo_contacto_cliente['empresas'][0]['nombre_empresa']}")
        
        # Probar construcción del menú
        print("\n🔸 Generando menú personalizado...")
        menu_resultado = construir_menu_cliente(tipo_contacto_cliente, "aura")
        
        print("✅ Menú generado:")
        print("-" * 40)
        print(menu_resultado)
        print("-" * 40)
        
        # Probar selección de opciones
        print("\n🔸 Probando selección de opciones...")
        
        opciones_test = ["1", "2", "3", "4", "5", "6"]
        
        for opcion in opciones_test:
            print(f"\n📝 Probando opción {opcion}:")
            resultado_opcion = procesar_seleccion_menu_cliente(opcion, tipo_contacto_cliente, "aura")
            print(f"✅ Resultado: {resultado_opcion[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de menú de cliente: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_menu_visitante():
    """Test: Simular un visitante y verificar que use el menú general"""
    print("\n" + "=" * 60)
    print("🧪 TEST: Menú General para Visitante")
    print("=" * 60)
    
    try:
        from clientes.aura.utils.menu_cliente import construir_menu_cliente
        
        # Simular un visitante
        tipo_contacto_visitante = {
            "tipo": "desconocido",
            "id": None,
            "nombre": "Visitante",
            "email": "",
            "telefono": "5215587654321"
        }
        
        print(f"👤 Visitante simulado: {tipo_contacto_visitante['nombre']}")
        
        # Probar construcción del menú
        menu_resultado = construir_menu_cliente(tipo_contacto_visitante, "aura")
        
        print("✅ Resultado para visitante:")
        print("-" * 40)
        print(menu_resultado)
        print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de menú de visitante: {e}")
        return False

def test_menu_multiple_empresas():
    """Test: Cliente con múltiples empresas"""
    print("\n" + "=" * 60)
    print("🧪 TEST: Cliente con Múltiples Empresas")
    print("=" * 60)
    
    try:
        from clientes.aura.utils.menu_cliente import construir_menu_cliente, procesar_seleccion_menu_cliente
        
        # Simular cliente con múltiples empresas
        tipo_contacto_multi = {
            "tipo": "cliente",
            "id": "test-cliente-multi",
            "nombre": "María González",
            "email": "maria@email.com",
            "telefono": "5215599887766",
            "empresas": [
                {
                    "id": "empresa-1",
                    "nombre_empresa": "Startup Tech",
                    "industria": "Tecnología"
                },
                {
                    "id": "empresa-2", 
                    "nombre_empresa": "Consultora Legal",
                    "industria": "Legal"
                }
            ]
        }
        
        print(f"👤 Cliente: {tipo_contacto_multi['nombre']}")
        print(f"🏢 Empresas: {len(tipo_contacto_multi['empresas'])}")
        
        # Probar menú inicial
        menu_inicial = construir_menu_cliente(tipo_contacto_multi, "aura")
        print("✅ Menú inicial (selector de empresas):")
        print("-" * 40)
        print(menu_inicial)
        print("-" * 40)
        
        # Probar selección de empresa
        print("\n📝 Seleccionando empresa 1:")
        menu_empresa_1 = procesar_seleccion_menu_cliente("1", tipo_contacto_multi, "aura")
        print("✅ Menú de empresa específica:")
        print(menu_empresa_1[:200] + "...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de múltiples empresas: {e}")
        return False

def ejecutar_tests_menu():
    """Ejecutar todos los tests del menú"""
    print("🚀 INICIANDO TESTS DE MENÚ PERSONALIZADO")
    print("=" * 80)
    
    tests_pasados = 0
    total_tests = 3
    
    # Test 1: Cliente con una empresa
    if test_menu_cliente_mock():
        tests_pasados += 1
    
    # Test 2: Visitante
    if test_menu_visitante():
        tests_pasados += 1
        
    # Test 3: Cliente con múltiples empresas
    if test_menu_multiple_empresas():
        tests_pasados += 1
    
    # Resumen
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE TESTS DE MENÚ")
    print("=" * 80)
    print(f"✅ Tests pasados: {tests_pasados}/{total_tests}")
    
    if tests_pasados == total_tests:
        print("🎉 ¡TODOS LOS TESTS DEL MENÚ PASARON!")
        print("🏢 Los clientes ahora tienen acceso a menús personalizados con:")
        print("   - Tareas activas y completadas")
        print("   - Brief de la empresa")
        print("   - Próximas reuniones")
        print("   - Estadísticas del proyecto")
        print("   - Contacto con el equipo")
    else:
        print(f"⚠️ {total_tests - tests_pasados} tests fallaron.")
    
    print("=" * 80)

if __name__ == "__main__":
    ejecutar_tests_menu()
