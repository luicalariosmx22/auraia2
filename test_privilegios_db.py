#!/usr/bin/env python3
"""
🧪 Test del Sistema de Privilegios de Base de Datos
Verifica que los privilegios se asignen correctamente según el tipo de usuario
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clientes.aura.auth.privilegios_db import PrivilegiosDB, TipoUsuario, TipoOperacion

def test_privilegios_admin():
    """Test de privilegios para tu usuario (SuperAdmin)"""
    print("=" * 70)
    print("👑 TEST: PRIVILEGIOS SUPERLADMIN (LUICA LARIOS)")
    print("=" * 70)
    
    # Tu usuario como SuperAdmin
    usuario_admin = {
        "nombre": "Luica Larios Admin",
        "correo": "bluetiemx@gmail.com",
        "telefono": "5216624644200",
        "rol": "superadmin",
        "es_supervisor": True,
        "modulos": ["tareas"],
        "tipo": "usuario_cliente"
    }
    
    # Verificar tipo de usuario
    tipo = PrivilegiosDB.determinar_tipo_usuario(usuario_admin)
    print(f"🎯 Tipo de usuario detectado: {tipo.value}")
    
    # Test de acceso a diferentes tablas
    tablas_criticas = [
        "usuarios_clientes",
        "configuracion_bot", 
        "base_conocimiento",
        "clientes",
        "facturacion",
        "logs_sistema"
    ]
    
    print(f"\n🔍 Verificando acceso a tablas críticas...")
    for tabla in tablas_criticas:
        acceso_read = PrivilegiosDB.tiene_acceso(usuario_admin, tabla, TipoOperacion.READ)
        acceso_write = PrivilegiosDB.tiene_acceso(usuario_admin, tabla, TipoOperacion.WRITE)
        acceso_delete = PrivilegiosDB.tiene_acceso(usuario_admin, tabla, TipoOperacion.DELETE)
        acceso_admin = PrivilegiosDB.tiene_acceso(usuario_admin, tabla, TipoOperacion.ADMIN)
        
        print(f"📊 {tabla}:")
        print(f"   READ: {'✅' if acceso_read else '❌'}")
        print(f"   WRITE: {'✅' if acceso_write else '❌'}")
        print(f"   DELETE: {'✅' if acceso_delete else '❌'}")
        print(f"   ADMIN: {'✅' if acceso_admin else '❌'}")
    
    # Generar reporte completo
    print(f"\n📋 REPORTE COMPLETO DE PRIVILEGIOS:")
    reporte = PrivilegiosDB.generar_reporte_privilegios(usuario_admin)
    print(f"   Tablas totales: {reporte['resumen']['total_tablas']}")
    print(f"   Tablas con acceso: {reporte['resumen']['tablas_con_acceso']}")
    print(f"   Acceso admin: {reporte['resumen']['acceso_admin']}")
    print(f"   Lectura/Escritura: {reporte['resumen']['lectura_escritura']}")

def test_privilegios_cliente():
    """Test de privilegios para un cliente normal"""
    print(f"\n" + "=" * 70)
    print("👤 TEST: PRIVILEGIOS CLIENTE NORMAL")
    print("=" * 70)
    
    # Usuario cliente normal
    usuario_cliente = {
        "nombre": "Juan Pérez Cliente",
        "correo": "juan@empresa.com",
        "telefono": "1234567890",
        "rol": "cliente", 
        "es_supervisor": False,
        "modulos": [],
        "tipo": "usuario_cliente"
    }
    
    tipo = PrivilegiosDB.determinar_tipo_usuario(usuario_cliente)
    print(f"🎯 Tipo de usuario detectado: {tipo.value}")
    
    # Verificar limitaciones de acceso
    tablas_test = [
        ("usuarios_clientes", "❌ No debe tener acceso"),
        ("configuracion_bot", "❌ No debe tener acceso"),
        ("base_conocimiento", "✅ Debe tener acceso limitado"),
        ("clientes", "✅ Debe tener acceso de lectura"),
        ("facturacion", "❌ No debe tener acceso"),
        ("logs_sistema", "❌ No debe tener acceso")
    ]
    
    print(f"\n🔍 Verificando limitaciones de acceso...")
    for tabla, descripcion in tablas_test:
        acceso_read = PrivilegiosDB.tiene_acceso(usuario_cliente, tabla, TipoOperacion.READ)
        acceso_write = PrivilegiosDB.tiene_acceso(usuario_cliente, tabla, TipoOperacion.WRITE)
        acceso_admin = PrivilegiosDB.tiene_acceso(usuario_cliente, tabla, TipoOperacion.ADMIN)
        
        print(f"📊 {tabla} ({descripcion}):")
        print(f"   READ: {'✅' if acceso_read else '❌'}")
        print(f"   WRITE: {'✅' if acceso_write else '❌'}")
        print(f"   ADMIN: {'✅' if acceso_admin else '❌'}")

def test_privilegios_visitante():
    """Test de privilegios para un visitante (sin registro)"""
    print(f"\n" + "=" * 70)
    print("🚶 TEST: PRIVILEGIOS VISITANTE")
    print("=" * 70)
    
    # Visitante sin registro
    usuario_visitante = None
    
    tipo = PrivilegiosDB.determinar_tipo_usuario(usuario_visitante)
    print(f"🎯 Tipo de usuario detectado: {tipo.value}")
    
    # Los visitantes no deben tener acceso a nada
    tablas_test = ["usuarios_clientes", "base_conocimiento", "clientes"]
    
    print(f"\n🔍 Verificando denegación de acceso...")
    for tabla in tablas_test:
        acceso_read = PrivilegiosDB.tiene_acceso(usuario_visitante, tabla, TipoOperacion.READ)
        print(f"📊 {tabla}: {'❌ CORRECTO - Sin acceso' if not acceso_read else '⚠️ ERROR - Tiene acceso'}")

def test_tablas_accesibles():
    """Test de obtención de tablas accesibles por tipo de usuario"""
    print(f"\n" + "=" * 70)
    print("📋 TEST: TABLAS ACCESIBLES POR TIPO DE USUARIO")
    print("=" * 70)
    
    usuarios_test = [
        {
            "nombre": "SuperAdmin",
            "rol": "superadmin",
            "tipo": "usuario_cliente"
        },
        {
            "nombre": "Admin Normal", 
            "rol": "admin",
            "tipo": "usuario_cliente"
        },
        {
            "nombre": "Cliente Normal",
            "rol": "cliente",
            "tipo": "usuario_cliente"
        }
    ]
    
    for usuario in usuarios_test:
        print(f"\n👤 {usuario['nombre']} ({usuario['rol']}):")
        
        # Tablas con acceso de lectura
        tablas_read = PrivilegiosDB.obtener_tablas_accesibles(usuario, TipoOperacion.READ)
        print(f"   📖 Lectura ({len(tablas_read)}): {', '.join(tablas_read)}")
        
        # Tablas con acceso de escritura
        tablas_write = PrivilegiosDB.obtener_tablas_accesibles(usuario, TipoOperacion.WRITE)
        print(f"   ✏️ Escritura ({len(tablas_write)}): {', '.join(tablas_write)}")
        
        # Tablas con acceso admin
        tablas_admin = PrivilegiosDB.obtener_tablas_accesibles(usuario, TipoOperacion.ADMIN)
        print(f"   👑 Admin ({len(tablas_admin)}): {', '.join(tablas_admin)}")

def test_decorador_privilegios():
    """Test del decorador de privilegios"""
    print(f"\n" + "=" * 70)
    print("🎨 TEST: DECORADOR DE PRIVILEGIOS")
    print("=" * 70)
    
    from clientes.aura.auth.privilegios_db import requiere_privilegio
    
    @requiere_privilegio("usuarios_clientes", TipoOperacion.READ)
    def leer_usuarios(usuario):
        return f"Leyendo usuarios para {usuario.get('nombre', 'Usuario')}"
    
    # Test con SuperAdmin (debe permitir)
    admin = {"nombre": "Admin", "rol": "superadmin", "tipo": "usuario_cliente"}
    try:
        resultado = leer_usuarios(admin)
        print(f"✅ SuperAdmin: {resultado}")
    except PermissionError as e:
        print(f"❌ SuperAdmin: {e}")
    
    # Test con Cliente (debe denegar)
    cliente = {"nombre": "Cliente", "rol": "cliente", "tipo": "usuario_cliente"}
    try:
        resultado = leer_usuarios(cliente)
        print(f"⚠️ Cliente: {resultado} (NO DEBERÍA PERMITIR)")
    except PermissionError as e:
        print(f"✅ Cliente: Acceso correctamente denegado - {e}")

if __name__ == "__main__":
    test_privilegios_admin()
    test_privilegios_cliente()
    test_privilegios_visitante()
    test_tablas_accesibles()
    test_decorador_privilegios()
    
    print(f"\n" + "=" * 70)
    print("🎯 TESTS DE PRIVILEGIOS COMPLETADOS")
    print("=" * 70)
