#!/usr/bin/env python3
"""
🧪 Test del mensaje de bienvenida para empleados
"""

from clientes.aura.handlers.process_message import generar_mensaje_bienvenida_empleado

def test_mensaje_empleado():
    """Test del mensaje de bienvenida personalizado"""
    
    print("🧪 TEST MENSAJE BIENVENIDA EMPLEADOS")
    print("=" * 50)
    
    # Simular datos de usuario_cliente
    usuario_empleado = {
        "tipo": "usuario_cliente",
        "id": "123-abc-456",
        "nombre": "Juan Pérez",
        "rol": "Desarrollador",
        "telefono": "6629360887"
    }
    
    print("👤 DATOS DEL EMPLEADO:")
    print(f"   Nombre: {usuario_empleado['nombre']}")
    print(f"   Rol: {usuario_empleado['rol']}")
    print(f"   Teléfono: {usuario_empleado['telefono']}")
    
    print("\n📱 MENSAJE GENERADO:")
    mensaje = generar_mensaje_bienvenida_empleado(usuario_empleado, "aura")
    print(mensaje)
    
    print("\n" + "=" * 50)
    print("✅ MENSAJE LISTO PARA WHATSAPP")

if __name__ == "__main__":
    test_mensaje_empleado()
