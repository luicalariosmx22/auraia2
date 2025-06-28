#!/usr/bin/env python3
"""
Test específico para probar confirmaciones con múltiples coincidencias
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_confirmacion_multiples():
    """Test para probar confirmaciones cuando hay múltiples coincidencias"""
    print("🔧 TEST: CONFIRMACIONES CON MÚLTIPLES COINCIDENCIAS")
    print("=" * 60)
    
    try:
        from clientes.aura.utils.consultor_tareas import procesar_consulta_tareas
        from clientes.aura.utils.gestor_estados import tiene_confirmacion_pendiente, limpiar_confirmacion_tareas
        
        # Usuario con privilegios de superadmin
        usuario_admin = {
            'id': 1,
            'nombre_completo': 'Admin Test',
            'telefono': '+56900000002',
            'email': 'admin@test.com',
            'rol': 'super_admin',  # Corregido: usar 'rol' en lugar de 'role'
            'tipo': 'usuario_cliente',
            'is_active': True,
            'cliente_id': 1
        }
        
        telefono_test = "+5214424081240"
        
        # Limpiar cualquier estado previo
        limpiar_confirmacion_tareas(telefono_test)
        
        print("1️⃣ Probando consulta que debería requerir confirmación:")
        print("   📝 Consulta: 'tareas de suspiros'")
        
        # Esta consulta debería encontrar múltiples empresas y requerir confirmación
        resultado = procesar_consulta_tareas(
            "tareas de suspiros", 
            usuario_admin, 
            telefono_test, 
            "aura"
        )
        
        print(f"   📊 Resultado:\n{resultado}")
        
        # Verificar si se estableció una confirmación pendiente
        hay_confirmacion = tiene_confirmacion_pendiente(telefono_test)
        print(f"   🔍 ¿Hay confirmación pendiente? {hay_confirmacion}")
        
        if hay_confirmacion:
            print("\n2️⃣ Simulando respuesta del usuario:")
            print("   📝 Usuario responde: '2' (selecciona segunda opción)")
            
            # Simular respuesta del usuario
            resultado_confirmacion = procesar_consulta_tareas(
                "2",
                usuario_admin,
                telefono_test,
                "aura"
            )
            
            print(f"   📊 Resultado de confirmación:\n{resultado_confirmacion}")
            
            # Verificar que se limpió la confirmación
            hay_confirmacion_despues = tiene_confirmacion_pendiente(telefono_test)
            print(f"   🔍 ¿Hay confirmación después? {hay_confirmacion_despues}")
        else:
            print("   ⚠️ No se estableció confirmación cuando debería haberla")
        
        print("\n3️⃣ Probando otra consulta ambigua:")
        print("   📝 Consulta: 'tareas de david'")
        
        # Limpiar estado previo
        limpiar_confirmacion_tareas(telefono_test)
        
        resultado2 = procesar_consulta_tareas(
            "tareas de david", 
            usuario_admin, 
            telefono_test, 
            "aura"
        )
        
        print(f"   📊 Resultado:\n{resultado2}")
        
        hay_confirmacion2 = tiene_confirmacion_pendiente(telefono_test)
        print(f"   🔍 ¿Hay confirmación pendiente? {hay_confirmacion2}")
        
        # Limpiar al final
        limpiar_confirmacion_tareas(telefono_test)
        
        print(f"\n" + "=" * 60)
        print("✅ Test de confirmaciones completado")
        
    except Exception as e:
        print(f"❌ Error en test de confirmaciones: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_confirmacion_multiples()
