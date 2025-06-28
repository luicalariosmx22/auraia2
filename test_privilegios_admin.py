#!/usr/bin/env python3
"""
🎯 Test específico para el admin Luica Larios
Verifica que como SuperAdmin tienes acceso completo
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clientes.aura.auth.privilegios import PrivilegiosManager

def test_admin_luica():
    """Test de privilegios para el admin Luica Larios"""
    print("=" * 70)
    print("👑 TEST: PRIVILEGIOS SUPERADMIN LUICA LARIOS")
    print("=" * 70)
    
    # Tu perfil de admin
    usuario_admin = {
        "tipo": "usuario_cliente",
        "nombre": "Luica Larios Admin",
        "correo": "bluetiemx@gmail.com",
        "telefono": "5216624644200",
        "rol": "superadmin",
        "es_supervisor": True,
        "modulos": ["tareas", "admin", "configuracion"],
        "nombre_nora": "aura"
    }
    
    print(f"👤 Usuario: {usuario_admin['nombre']}")
    print(f"🏷️ Rol: {usuario_admin['rol']}")
    print(f"📞 Teléfono: {usuario_admin['telefono']}")
    print(f"🔑 Supervisor: {usuario_admin['es_supervisor']}")
    print()
    
    # Crear manager de privilegios
    privilegios = PrivilegiosManager(usuario_admin)
    
    # Verificar tipo
    print(f"🎯 Tipo de usuario detectado: {privilegios.get_tipo_usuario()}")
    print()
    
    # Tablas críticas que el admin DEBE poder acceder
    tablas_criticas = [
        "usuarios_clientes",
        "configuracion_bot", 
        "base_conocimiento",
        "clientes",
        "facturacion",
        "logs_sistema",
        "cliente_empresas",
        "meta_ads_anuncios"
    ]
    
    print("🔍 Verificando acceso de SuperAdmin a todas las tablas...")
    print()
    
    total_accesos = 0
    accesos_correctos = 0
    
    for tabla in tablas_criticas:
        print(f"📊 {tabla}:")
        
        # Verificar los 3 tipos de acceso
        read = privilegios.puede_acceder(tabla, "read")
        write = privilegios.puede_acceder(tabla, "write") 
        admin = privilegios.puede_acceder(tabla, "admin")
        
        total_accesos += 3
        if read: accesos_correctos += 1
        if write: accesos_correctos += 1  
        if admin: accesos_correctos += 1
        
        print(f"   READ: {'✅' if read else '❌'}")
        print(f"   WRITE: {'✅' if write else '❌'}")
        print(f"   ADMIN: {'✅' if admin else '❌'}")
        print()
    
    # Resumen final
    porcentaje = (accesos_correctos / total_accesos) * 100
    print("=" * 50)
    print(f"📊 RESUMEN DE PRIVILEGIOS SUPERADMIN:")
    print(f"✅ Accesos otorgados: {accesos_correctos}/{total_accesos}")
    print(f"📈 Porcentaje de acceso: {porcentaje:.1f}%")
    
    if porcentaje >= 95:
        print("🎉 PERFECTO: Acceso completo como SuperAdmin")
    elif porcentaje >= 80:
        print("⚠️ BUENO: Acceso mayoritario, revisar restricciones")
    else:
        print("❌ PROBLEMA: Acceso limitado para SuperAdmin")
    
    print("=" * 50)
    
    # Test de operaciones específicas
    print()
    print("🧪 TEST DE OPERACIONES ESPECÍFICAS:")
    print()
    
    operaciones_test = [
        ("Leer usuarios internos", "usuarios_clientes", "read"),
        ("Modificar configuración", "configuracion_bot", "write"),
        ("Administrar base conocimiento", "base_conocimiento", "admin"),
        ("Acceder a facturación", "facturacion", "read"),
        ("Ver logs del sistema", "logs_sistema", "read"),
        ("Crear nuevos usuarios", "usuarios_clientes", "admin")
    ]
    
    for desc, tabla, operacion in operaciones_test:
        puede = privilegios.puede_acceder(tabla, operacion)
        status = "✅" if puede else "❌"
        print(f"{status} {desc}: {'Permitido' if puede else 'Denegado'}")
    
    print()
    print("=" * 70)
    print("👑 TEST COMPLETADO - PRIVILEGIOS SUPERADMIN")
    print("=" * 70)

if __name__ == "__main__":
    test_admin_luica()
