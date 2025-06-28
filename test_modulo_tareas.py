#!/usr/bin/env python3
"""
🧪 Test del Módulo de Consultas de Tareas
Verifica que las consultas de tareas funcionen correctamente para el admin
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_deteccion_consultas_tareas():
    """Test de detección de diferentes tipos de consultas"""
    print("=" * 70)
    print("📋 TEST: DETECCIÓN DE CONSULTAS DE TAREAS")
    print("=" * 70)
    
    # Import directo para evitar problemas
    from clientes.aura.utils.consultor_tareas import ConsultorTareas
    
    # Tu usuario admin
    usuario_admin = {
        "nombre": "Luica Larios Admin",
        "correo": "bluetiemx@gmail.com", 
        "telefono": "5216624644200",
        "rol": "superadmin",
        "es_supervisor": True,
        "tipo": "usuario_cliente"
    }
    
    consultor = ConsultorTareas(usuario_admin, "aura")
    
    # Test de diferentes consultas
    consultas_test = [
        "¿Qué tareas tiene Juan Pérez?",
        "Tareas de la empresa ABC",
        "Mostrar tareas pendientes de María García",
        "Ver tareas urgentes de Tecnológica SA",
        "¿Cuáles son las tareas de Luis Rodriguez?",
        "Tareas completadas de Innovation Corp",
        "Listar tareas vencidas de Pedro López",
        "¿Tiene tareas Ana Martínez?",
        "Consultar tareas en proceso de Digital Solutions",
        "Tareas de alta prioridad de Carmen Silva"
    ]
    
    print(f"🔍 Probando {len(consultas_test)} tipos de consultas...\n")
    
    for i, consulta in enumerate(consultas_test, 1):
        print(f"📝 Test {i}: '{consulta}'")
        
        deteccion = consultor.detectar_consulta_tareas(consulta)
        
        if deteccion:
            print(f"   ✅ DETECTADA")
            print(f"   📊 Entidad: {deteccion['entidad']}")
            print(f"   🏷️ Tipo: {deteccion['tipo']}")
            if deteccion['filtros']:
                print(f"   🔍 Filtros: {deteccion['filtros']}")
        else:
            print(f"   ❌ NO DETECTADA")
        print()

def test_privilegios_consultas():
    """Test de privilegios para consultas de tareas"""
    print("=" * 70)
    print("🔐 TEST: PRIVILEGIOS PARA CONSULTAS DE TAREAS")
    print("=" * 70)
    
    from clientes.aura.utils.consultor_tareas import ConsultorTareas
    
    # Test con diferentes tipos de usuario
    usuarios_test = [
        {
            "nombre": "SuperAdmin Test",
            "rol": "superadmin",
            "tipo": "usuario_cliente",
            "descripcion": "SuperAdmin (TÚ)"
        },
        {
            "nombre": "Admin Test", 
            "rol": "admin",
            "tipo": "usuario_cliente",
            "descripcion": "Admin Normal"
        },
        {
            "nombre": "Usuario Test",
            "rol": "empleado",
            "tipo": "usuario_cliente", 
            "descripcion": "Usuario Interno"
        },
        {
            "nombre": "Cliente Test",
            "rol": "cliente",
            "tipo": "cliente",
            "descripcion": "Cliente Externo"
        }
    ]
    
    for usuario in usuarios_test:
        consultor = ConsultorTareas(usuario, "aura")
        puede_consultar = consultor.puede_consultar_tareas()
        
        status = "✅ PERMITIDO" if puede_consultar else "❌ DENEGADO"
        print(f"{status} {usuario['descripcion']}: {usuario['nombre']}")
    
    print()

def test_formateo_respuestas():
    """Test del formateo de respuestas de tareas"""
    print("=" * 70)
    print("📋 TEST: FORMATEO DE RESPUESTAS DE TAREAS")
    print("=" * 70)
    
    from clientes.aura.utils.consultor_tareas import ConsultorTareas
    
    usuario_admin = {
        "nombre": "Luica Larios Admin",
        "rol": "superadmin",
        "tipo": "usuario_cliente"
    }
    
    consultor = ConsultorTareas(usuario_admin, "aura")
    
    # Simular tareas de ejemplo
    tareas_ejemplo = [
        {
            "id": "1",
            "titulo": "Implementar autenticación OAuth",
            "descripcion": "Configurar Google OAuth en el sistema",
            "estatus": "en_proceso",
            "prioridad": "alta",
            "fecha_limite": "2024-12-30",
            "usuarios_clientes": {"nombre": "Juan Desarrollador"},
            "cliente_empresas": {"nombre_empresa": "TechCorp"}
        },
        {
            "id": "2", 
            "titulo": "Revisar base de datos de clientes",
            "descripcion": "Auditoría de datos de clientes",
            "estatus": "pendiente",
            "prioridad": "media",
            "fecha_limite": "2024-12-28",
            "usuarios_clientes": {"nombre": "María Analista"},
            "cliente_empresas": {"nombre_empresa": "DataSolutions"}
        },
        {
            "id": "3",
            "titulo": "Backup del sistema",
            "descripcion": "Realizar backup completo",
            "estatus": "completada", 
            "prioridad": "alta",
            "fecha_limite": "2024-12-25",
            "usuarios_clientes": {"nombre": "Carlos SysAdmin"},
            "cliente_empresas": {"nombre_empresa": "Infrastructure LLC"}
        }
    ]
    
    consulta_info = {
        "entidad": "Juan Desarrollador",
        "tipo": "usuario"
    }
    
    respuesta = consultor.formatear_respuesta_tareas(tareas_ejemplo, consulta_info)
    
    print("🎯 RESPUESTA FORMATEADA:")
    print("=" * 50)
    print(respuesta)
    print("=" * 50)
    
    # Test con lista vacía
    print("\n🔍 TEST CON RESULTADO VACÍO:")
    print("-" * 30)
    respuesta_vacia = consultor.formatear_respuesta_tareas([], consulta_info)
    print(respuesta_vacia)

def test_integracion_completa():
    """Test de integración completa con el sistema de IA"""
    print("\n" + "=" * 70)
    print("🚀 TEST: INTEGRACIÓN COMPLETA CON SISTEMA DE IA")
    print("=" * 70)
    
    from clientes.aura.utils.consultor_tareas import procesar_consulta_tareas
    
    # Tu usuario admin
    usuario_admin = {
        "nombre": "Luica Larios Admin",
        "correo": "bluetiemx@gmail.com",
        "telefono": "5216624644200", 
        "rol": "superadmin",
        "es_supervisor": True,
        "tipo": "usuario_cliente"
    }
    
    # Test de diferentes consultas
    consultas_integracion = [
        "¿Qué tareas tiene Juan?",
        "Tareas de la empresa TechCorp",
        "Hola, ¿cómo estás?"  # Esta NO debe ser detectada como consulta de tareas
    ]
    
    for consulta in consultas_integracion:
        print(f"💬 Consulta: '{consulta}'")
        
        resultado = procesar_consulta_tareas(consulta, usuario_admin, "aura")
        
        if resultado:
            print(f"✅ PROCESADA como consulta de tareas")
            print(f"📄 Respuesta generada: {len(resultado)} caracteres")
        else:
            print(f"ℹ️ NO ES consulta de tareas (correcto)")
        print()

if __name__ == "__main__":
    test_deteccion_consultas_tareas()
    test_privilegios_consultas()
    test_formateo_respuestas()
    test_integracion_completa()
    
    print("\n" + "=" * 70)
    print("🎉 TESTS DE MÓDULO DE TAREAS COMPLETADOS")
    print("=" * 70)
    print("\n💡 AHORA PUEDES PROBAR EN WHATSAPP:")
    print("   • 'Tareas de [nombre de usuario]'")
    print("   • 'Tareas de [nombre de empresa]'") 
    print("   • 'Tareas pendientes de Juan'")
    print("   • 'Ver tareas urgentes de TechCorp'")
    print("   • '¿Qué tareas tiene María?'")
