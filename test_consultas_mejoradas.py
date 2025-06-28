#!/usr/bin/env python3
"""
🧪 Test del Sistema Mejorado de Consultas de Tareas
Verifica la búsqueda con similitud y confirmaciones
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clientes.aura.utils.consultor_tareas import ConsultorTareas, procesar_consulta_tareas
from clientes.aura.utils.gestor_estados import (
    establecer_confirmacion_tareas, 
    obtener_confirmacion_tareas, 
    limpiar_confirmacion_tareas,
    tiene_confirmacion_pendiente
)

def test_busqueda_similitud():
    """Test de búsqueda por similitud"""
    print("🧪 Probando búsqueda por similitud...")
    
    usuario_admin = {
        "id": 1,
        "telefono": "+5214424081234",
        "rol": "superadmin",
        "tipo": "usuario_cliente",
        "nombre_completo": "Admin Test",
        "email": "admin@test.com",
        "cliente_id": 1,
        "activo": True
    }
    
    consultor = ConsultorTareas(usuario_admin, "aura")
    
    # Test 1: Búsqueda exacta
    print("\n1️⃣ Búsqueda exacta de usuario:")
    usuarios, tipo = consultor.buscar_usuario_por_nombre("David Martinez")
    print(f"   Resultado: {len(usuarios)} usuarios, tipo: {tipo}")
    for usuario in usuarios:
        print(f"   - {usuario.get('nombre', 'Sin nombre')} ({usuario.get('correo', 'Sin correo')})")
    
    # Test 2: Búsqueda parcial
    print("\n2️⃣ Búsqueda parcial de usuario:")
    usuarios, tipo = consultor.buscar_usuario_por_nombre("David")
    print(f"   Resultado: {len(usuarios)} usuarios, tipo: {tipo}")
    for usuario in usuarios:
        print(f"   - {usuario.get('nombre', 'Sin nombre')} ({usuario.get('correo', 'Sin correo')})")
    
    # Test 3: Búsqueda de empresa
    print("\n3️⃣ Búsqueda de empresa:")
    empresas, tipo = consultor.buscar_empresa_por_nombre("Suspiros")
    print(f"   Resultado: {len(empresas)} empresas, tipo: {tipo}")
    for empresa in empresas:
        print(f"   - {empresa.get('nombre_empresa', 'Sin nombre')}")

def test_consulta_con_confirmacion():
    """Test de consulta que requiere confirmación"""
    print("\n🧪 Probando consulta con confirmación...")
    
    usuario_admin = {
        "id": 1,
        "telefono": "+5214424081234",
        "rol": "superadmin",
        "tipo": "usuario_cliente",
        "nombre_completo": "Admin Test",
        "email": "admin@test.com",
        "cliente_id": 1,
        "activo": True
    }
    
    telefono_test = "+5214424081234"
    
    # Test 1: Consulta que debería generar confirmación
    print("\n1️⃣ Consulta ambigua que debería requerir confirmación:")
    resultado = procesar_consulta_tareas("tareas de David", usuario_admin, telefono_test, "aura")
    print(f"Resultado: {resultado}")
    
    # Test 2: Verificar estado pendiente
    print(f"\n2️⃣ ¿Hay confirmación pendiente? {tiene_confirmacion_pendiente(telefono_test)}")
    
    if tiene_confirmacion_pendiente(telefono_test):
        # Test 3: Procesar confirmación
        print("\n3️⃣ Procesando confirmación con número:")
        resultado_confirmacion = procesar_consulta_tareas("1", usuario_admin, telefono_test, "aura")
        print(f"Resultado confirmación: {resultado_confirmacion}")
    
    # Test 4: Verificar que se limpió el estado
    print(f"\n4️⃣ ¿Hay confirmación pendiente después? {tiene_confirmacion_pendiente(telefono_test)}")

def test_consulta_sin_coincidencias():
    """Test de consulta sin coincidencias"""
    print("\n🧪 Probando consulta sin coincidencias...")
    
    usuario_admin = {
        "id": 1,
        "telefono": "+5214424081234",
        "rol": "superadmin",
        "tipo": "usuario_cliente",
        "nombre_completo": "Admin Test",
        "email": "admin@test.com",
        "cliente_id": 1,
        "activo": True
    }
    
    telefono_test = "+5214424081234"
    
    # Test: Consulta de usuario inexistente
    print("\n1️⃣ Consulta de usuario inexistente:")
    resultado = procesar_consulta_tareas("tareas de Juan Perez Inexistente", usuario_admin, telefono_test, "aura")
    print(f"Resultado: {resultado}")

def test_consulta_empresa_ambigua():
    """Test de consulta de empresa con múltiples coincidencias"""
    print("\n🧪 Probando consulta de empresa ambigua...")
    
    usuario_admin = {
        "id": 1,
        "telefono": "+5214424081234",
        "rol": "superadmin",
        "tipo": "usuario_cliente",
        "nombre_completo": "Admin Test",
        "email": "admin@test.com",
        "cliente_id": 1,
        "activo": True
    }
    
    telefono_test = "+5214424081235"  # Diferente para no interferir con otros tests
    
    # Test: Consulta de empresa que debería tener múltiples coincidencias
    print("\n1️⃣ Consulta de empresa con término genérico:")
    resultado = procesar_consulta_tareas("tareas de la empresa Tech", usuario_admin, telefono_test, "aura")
    print(f"Resultado: {resultado}")
    
    # Limpiar estado si quedó pendiente
    limpiar_confirmacion_tareas(telefono_test)

def test_gestor_estados():
    """Test del gestor de estados"""
    print("\n🧪 Probando gestor de estados...")
    
    telefono_test = "+5214424081236"
    
    # Test 1: Establecer estado
    print("\n1️⃣ Estableciendo estado:")
    consulta_info = {"entidad": "David", "tipo": "usuario"}
    info_busqueda = {"usuarios_encontrados": [{"id": 1, "nombre": "David Test"}]}
    establecer_confirmacion_tareas(telefono_test, consulta_info, info_busqueda)
    
    # Test 2: Verificar estado
    print(f"2️⃣ ¿Tiene confirmación pendiente? {tiene_confirmacion_pendiente(telefono_test)}")
    
    # Test 3: Obtener datos
    datos = obtener_confirmacion_tareas(telefono_test)
    print(f"3️⃣ Datos obtenidos: {datos is not None}")
    if datos:
        print(f"    Consulta info: {datos.get('consulta_info')}")
    
    # Test 4: Limpiar estado
    limpiar_confirmacion_tareas(telefono_test)
    print(f"4️⃣ ¿Tiene confirmación después de limpiar? {tiene_confirmacion_pendiente(telefono_test)}")

if __name__ == "__main__":
    print("🚀 Iniciando tests del sistema mejorado de consultas de tareas...")
    
    try:
        test_gestor_estados()
        test_busqueda_similitud()
        test_consulta_sin_coincidencias()
        test_consulta_empresa_ambigua()
        test_consulta_con_confirmacion()
        
        print("\n✅ Todos los tests completados!")
        
    except Exception as e:
        print(f"\n❌ Error en los tests: {e}")
        import traceback
        traceback.print_exc()
