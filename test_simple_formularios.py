#!/usr/bin/env python3
"""
🧪 Prueba Simple del Sistema de Formularios
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("🔄 Intentando importar PrivilegiosManager...")
    from clientes.aura.auth.privilegios import PrivilegiosManager
    print("✅ PrivilegiosManager importado correctamente")
    
    print("🔄 Intentando importar detector_intenciones...")
    from clientes.aura.utils.detector_intenciones import detector_intenciones
    print("✅ detector_intenciones importado correctamente")
    
    print("🔄 Intentando importar formulario_conversacional...")
    from clientes.aura.utils.formulario_conversacional import crear_formulario_tarea
    print("✅ formulario_conversacional importado correctamente")
    
    print("\n🎉 TODAS LAS IMPORTACIONES EXITOSAS!")
    
    # Prueba básica
    usuario_test = {
        "tipo": "admin",
        "nombre": "Test Admin",
        "rol": "admin"
    }
    
    print("\n🧪 Probando PrivilegiosManager...")
    manager = PrivilegiosManager(usuario_test)
    print(f"   Tipo usuario: {manager.get_tipo_usuario()}")
    print(f"   Puede crear tareas: {manager.puede_acceder('tareas', 'write')}")
    
    print("\n🧪 Probando detector de intenciones...")
    es_crear_tarea = detector_intenciones.es_mensaje_crear_tarea("quiero crear una tarea", usuario_test)
    print(f"   Detecta 'crear tarea': {es_crear_tarea}")
    
    print("\n✅ PRUEBAS BÁSICAS COMPLETADAS!")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error durante las pruebas: {e}")
    import traceback
    traceback.print_exc()
