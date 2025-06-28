#!/usr/bin/env python3
"""
Test simple para verificar el consultor de tareas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_simple():
    """Test muy básico"""
    print("🔧 TEST SIMPLE CONSULTOR TAREAS")
    print("=" * 40)
    
    try:
        # Usuario de prueba
        usuario_test = {
            'id': 1,
            'nombre_completo': 'Test User',
            'telefono': '+56900000001',
            'email': 'test@test.com',
            'role': 'super_admin',
            'is_active': True,
            'cliente_id': 1
        }
        
        print("✅ Usuario de prueba creado")
        
        from clientes.aura.utils.consultor_tareas import ConsultorTareas
        print("✅ Módulo ConsultorTareas importado")
        
        consultor = ConsultorTareas(usuario_test, "aura")
        print("✅ ConsultorTareas instanciado")
        
        # Test de detección simple
        mensaje = "tareas de María"
        resultado = consultor.detectar_consulta_tareas(mensaje)
        print(f"✅ Detección test: {resultado}")
        
        print("\n🎯 TEST COMPLETADO EXITOSAMENTE")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple()
