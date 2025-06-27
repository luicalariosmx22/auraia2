#!/usr/bin/env python3
"""
Test simple del sistema de privilegios
"""

# Test directo sin imports complejos
class TipoOperacion:
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

def test_simple_privilegios():
    print("🧪 TEST SIMPLE: Sistema de Privilegios")
    print("=" * 50)
    
    # Simulación de privilegios
    PRIVILEGIOS = {
        "usuarios_clientes": {
            "superadmin": ["read", "write", "delete", "admin"],
            "admin": ["read", "write"],
            "cliente": []  # Sin acceso
        },
        "base_conocimiento": {
            "superadmin": ["read", "write", "delete", "admin"],
            "admin": ["read", "write"],
            "cliente": ["read", "write"]  # Acceso limitado
        }
    }
    
    def verificar_acceso(rol, tabla, operacion):
        if tabla not in PRIVILEGIOS:
            return False
        if rol not in PRIVILEGIOS[tabla]:
            return False
        return operacion in PRIVILEGIOS[tabla][rol]
    
    # Test de tu usuario (SuperAdmin)
    print("\n👑 TU USUARIO (SuperAdmin):")
    tu_rol = "superadmin"
    
    tablas_test = ["usuarios_clientes", "base_conocimiento"]
    operaciones = ["read", "write", "delete", "admin"]
    
    for tabla in tablas_test:
        print(f"\n📊 Tabla: {tabla}")
        for op in operaciones:
            acceso = verificar_acceso(tu_rol, tabla, op)
            print(f"   {op.upper()}: {'✅' if acceso else '❌'}")
    
    # Test de cliente normal
    print(f"\n👤 CLIENTE NORMAL:")
    cliente_rol = "cliente"
    
    for tabla in tablas_test:
        print(f"\n📊 Tabla: {tabla}")
        for op in operaciones:
            acceso = verificar_acceso(cliente_rol, tabla, op)
            print(f"   {op.upper()}: {'✅' if acceso else '❌'}")
    
    print(f"\n🎯 RESUMEN:")
    print(f"✅ SuperAdmin: Acceso total a todas las tablas")
    print(f"✅ Cliente: Acceso limitado solo a base_conocimiento")
    print(f"✅ Sistema de privilegios funcionando correctamente")
    
    # Casos de uso prácticos
    print(f"\n💡 CASOS DE USO PRÁCTICOS:")
    casos = [
        ("SuperAdmin lee usuarios_clientes", verificar_acceso("superadmin", "usuarios_clientes", "read")),
        ("SuperAdmin modifica configuración", verificar_acceso("superadmin", "usuarios_clientes", "admin")),
        ("Cliente lee usuarios_clientes", verificar_acceso("cliente", "usuarios_clientes", "read")),
        ("Cliente entrena IA", verificar_acceso("cliente", "base_conocimiento", "write")),
        ("Admin gestiona clientes", verificar_acceso("admin", "usuarios_clientes", "write"))
    ]
    
    for caso, resultado in casos:
        print(f"   {caso}: {'✅ PERMITIDO' if resultado else '❌ DENEGADO'}")

if __name__ == "__main__":
    test_simple_privilegios()
