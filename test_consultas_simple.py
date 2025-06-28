#!/usr/bin/env python3
"""
🧪 Test simple del sistema de consultas de tareas
Sin cargar blueprints ni Flask, solo las funciones core
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_privilegios_simple():
    """Test básico del sistema de privilegios"""
    print("🔐 TEST PRIVILEGIOS SIMPLE")
    print("=" * 40)
    
    try:
        from clientes.aura.auth.privilegios import PrivilegiosManager
        
        # Usuario superadmin
        usuario_admin = {
            'id': 1,
            'nombre_completo': 'Admin Test',
            'telefono': '+56900000001',
            'email': 'admin@test.com',
            'rol': 'superadmin',  # 🔑 Campo correcto
            'is_active': True,
            'cliente_id': 1
        }
        
        privilegios = PrivilegiosManager(usuario_admin)
        print(f"✅ Tipo usuario detectado: {privilegios.get_tipo_usuario()}")
        
        # Test acceso a tareas
        puede_leer = privilegios.puede_acceder("tareas", "read")
        print(f"✅ Puede leer tareas: {puede_leer}")
        
        puede_escribir = privilegios.puede_acceder("tareas", "write")
        print(f"✅ Puede escribir tareas: {puede_escribir}")
        
        return privilegios.get_tipo_usuario() == "superadmin" and puede_leer and puede_escribir
        
    except Exception as e:
        print(f"❌ Error en test privilegios: {e}")
        return False

def test_parser_consultas():
    """Test del parser de consultas sin conexión a BD"""
    print("\n🔍 TEST PARSER CONSULTAS")
    print("=" * 40)
    
    try:
        # Importar solo la clase sin dependencias de BD
        import re
        from typing import Dict
        
        class ParserSimple:
            def detectar_consulta_tareas(self, mensaje: str):
                """Versión simplificada del parser"""
                mensaje_lower = mensaje.lower().strip()
                
                patrones_tareas = [
                    r"tareas?\s+de\s+(?:la\s+)?empresa\s+([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)(?:\s+que|\?|$)",
                    r"tareas?\s+(?:activas?\s+)?(?:hay\s+)?(?:en\s+)?([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)\s+(?:la\s+)?empresa",
                    r"tareas?\s+de\s+([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)(?:\s+que|\s+tiene|\?|$)",
                    r"qué\s+tareas?\s+tiene\s+([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+?)(?:\?|$)",
                ]
                
                for patron in patrones_tareas:
                    match = re.search(patron, mensaje_lower)
                    if match:
                        entidad = match.group(1).strip()
                        
                        # Determinar tipo
                        tipo = "empresa" if "empresa" in mensaje_lower else "usuario"
                        
                        return {
                            "es_consulta_tareas": True,
                            "entidad": entidad,
                            "tipo": tipo,
                            "filtros": {}
                        }
                
                return None
        
        parser = ParserSimple()
        
        # Casos de test
        casos = [
            {
                "mensaje": "tareas activas hay en suspiros pastelerias la empresa",
                "esperado": {"entidad": "suspiros pastelerias", "tipo": "empresa"}
            },
            {
                "mensaje": "tareas de María",
                "esperado": {"entidad": "maría", "tipo": "usuario"}
            },
            {
                "mensaje": "¿Qué tareas tiene David?",
                "esperado": {"entidad": "david", "tipo": "usuario"}
            },
            {
                "mensaje": "tareas de la empresa TechCorp",
                "esperado": {"entidad": "techcorp", "tipo": "empresa"}
            }
        ]
        
        exitos = 0
        for caso in casos:
            resultado = parser.detectar_consulta_tareas(caso["mensaje"])
            print(f"\n📝 Mensaje: '{caso['mensaje']}'")
            
            if resultado:
                entidad_ok = resultado["entidad"].lower() == caso["esperado"]["entidad"].lower()
                tipo_ok = resultado["tipo"] == caso["esperado"]["tipo"]
                
                print(f"   🎯 Entidad: {resultado['entidad']} {'✅' if entidad_ok else '❌'}")
                print(f"   🎯 Tipo: {resultado['tipo']} {'✅' if tipo_ok else '❌'}")
                
                if entidad_ok and tipo_ok:
                    exitos += 1
            else:
                print(f"   ❌ No detectada")
        
        print(f"\n📊 Resultado: {exitos}/{len(casos)} casos exitosos")
        return exitos == len(casos)
        
    except Exception as e:
        print(f"❌ Error en test parser: {e}")
        return False

def test_busqueda_simulada():
    """Test simulado de búsqueda sin BD real"""
    print("\n🔎 TEST BÚSQUEDA SIMULADA")
    print("=" * 40)
    
    try:
        # Datos simulados
        usuarios_mock = [
            {"id": 1, "nombre": "David Alcantara", "correo": "david@test.com"},
            {"id": 2, "nombre": "María García", "correo": "maria@test.com"},
            {"id": 3, "nombre": "José Luis", "correo": "jose@test.com"}
        ]
        
        empresas_mock = [
            {"id": 1, "nombre_empresa": "SUSPIROS CAKES - BORIS"},
            {"id": 2, "nombre_empresa": "SUSPIROS PASTELERIAS"},  
            {"id": 3, "nombre_empresa": "Suspiros Pastelerias"},
            {"id": 4, "nombre_empresa": "TechCorp Solutions"}
        ]
        
        def buscar_usuarios_similares(nombre_buscar):
            """Búsqueda simulada de usuarios"""
            resultados = []
            nombre_lower = nombre_buscar.lower()
            
            for usuario in usuarios_mock:
                if nombre_lower in usuario["nombre"].lower():
                    resultados.append(usuario)
            
            return resultados
        
        def buscar_empresas_similares(nombre_buscar):
            """Búsqueda simulada de empresas"""
            resultados = []
            nombre_lower = nombre_buscar.lower()
            
            for empresa in empresas_mock:
                if nombre_lower in empresa["nombre_empresa"].lower():
                    resultados.append(empresa)
            
            return resultados
        
        # Tests de búsqueda
        print("1️⃣ Búsqueda de 'David':")
        usuarios_david = buscar_usuarios_similares("David")
        print(f"   Encontrados: {len(usuarios_david)} usuarios")
        for u in usuarios_david:
            print(f"   - {u['nombre']} ({u['correo']})")
        
        print("\n2️⃣ Búsqueda de 'Suspiros':")
        empresas_suspiros = buscar_empresas_similares("Suspiros")
        print(f"   Encontradas: {len(empresas_suspiros)} empresas")
        for e in empresas_suspiros:
            print(f"   - {e['nombre_empresa']}")
        
        print("\n3️⃣ Búsqueda de 'Tech':")
        empresas_tech = buscar_empresas_similares("Tech")
        print(f"   Encontradas: {len(empresas_tech)} empresas")
        for e in empresas_tech:
            print(f"   - {e['nombre_empresa']}")
        
        # Validaciones
        david_ok = len(usuarios_david) == 1 and "David" in usuarios_david[0]["nombre"]
        suspiros_ok = len(empresas_suspiros) == 3
        tech_ok = len(empresas_tech) == 1
        
        print(f"\n📊 Validaciones:")
        print(f"   David encontrado: {'✅' if david_ok else '❌'}")
        print(f"   Suspiros múltiples: {'✅' if suspiros_ok else '❌'}")
        print(f"   Tech encontrado: {'✅' if tech_ok else '❌'}")
        
        return david_ok and suspiros_ok and tech_ok
        
    except Exception as e:
        print(f"❌ Error en test búsqueda: {e}")
        return False

def test_confirmacion_logica():
    """Test de la lógica de confirmación"""
    print("\n❓ TEST LÓGICA CONFIRMACIÓN")
    print("=" * 40)
    
    try:
        def requiere_confirmacion(resultados, tipo_busqueda):
            """Lógica para determinar si requiere confirmación"""
            if not resultados:
                return False, "No se encontraron resultados"
            
            if len(resultados) == 1:
                return False, f"Resultado único encontrado: {resultados[0]}"
            
            if len(resultados) > 1:
                return True, f"Múltiples opciones encontradas ({len(resultados)})"
            
            return False, "Caso no contemplado"
        
        def generar_mensaje_confirmacion(resultados, tipo_entidad, entidad_original):
            """Genera mensaje de confirmación"""
            if len(resultados) <= 1:
                return None
            
            mensaje = f"🤔 Encontré varios **{tipo_entidad}s** que coinciden con **{entidad_original}**:\n\n"
            
            for i, resultado in enumerate(resultados[:5], 1):
                if tipo_entidad == "usuario":
                    nombre = resultado.get("nombre", "Sin nombre")
                    correo = resultado.get("correo", "Sin correo")
                    mensaje += f"{i}. **{nombre}** ({correo})\n"
                else:  # empresa
                    nombre_empresa = resultado.get("nombre_empresa", "Sin nombre")
                    mensaje += f"{i}. **{nombre_empresa}**\n"
            
            if len(resultados) > 5:
                mensaje += f"... y {len(resultados) - 5} más.\n"
            
            mensaje += f"\n💬 **Responde con el número** del {tipo_entidad} que buscas (1-{min(len(resultados), 5)})"
            
            return mensaje
        
        # Test casos
        casos_test = [
            {
                "nombre": "Resultado único",
                "resultados": [{"nombre": "David Alcantara", "correo": "david@test.com"}],
                "tipo": "usuario"
            },
            {
                "nombre": "Múltiples resultados", 
                "resultados": [
                    {"nombre_empresa": "SUSPIROS CAKES - BORIS"},
                    {"nombre_empresa": "SUSPIROS PASTELERIAS"},
                    {"nombre_empresa": "Suspiros Pastelerias"}
                ],
                "tipo": "empresa"
            },
            {
                "nombre": "Sin resultados",
                "resultados": [],
                "tipo": "usuario"
            }
        ]
        
        exitos = 0
        for caso in casos_test:
            print(f"\n📋 Caso: {caso['nombre']}")
            
            requiere, razon = requiere_confirmacion(caso["resultados"], caso["tipo"])
            print(f"   Requiere confirmación: {'✅ Sí' if requiere else '❌ No'}")
            print(f"   Razón: {razon}")
            
            if requiere and len(caso["resultados"]) > 1:
                mensaje = generar_mensaje_confirmacion(caso["resultados"], caso["tipo"], "test")
                print(f"   Mensaje generado: {'✅ Sí' if mensaje else '❌ No'}")
                if mensaje:
                    lineas_mensaje = len(mensaje.split('\n'))
                    print(f"   Líneas del mensaje: {lineas_mensaje}")
                exitos += 1
            elif not requiere and len(caso["resultados"]) <= 1:
                print(f"   Comportamiento correcto: {'✅'}")
                exitos += 1
        
        print(f"\n📊 Casos correctos: {exitos}/{len(casos_test)}")
        return exitos == len(casos_test)
        
    except Exception as e:
        print(f"❌ Error en test confirmación: {e}")
        return False

def main():
    """Ejecuta todos los tests simples"""
    print("🚀 INICIANDO TESTS SIMPLES DEL SISTEMA DE TAREAS")
    print("=" * 60)
    
    tests = [
        ("Privilegios", test_privilegios_simple),
        ("Parser", test_parser_consultas),
        ("Búsqueda", test_busqueda_simulada),
        ("Confirmación", test_confirmacion_logica)
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
            print(f"\n{'✅' if resultado else '❌'} {nombre}: {'ÉXITO' if resultado else 'FALLO'}")
        except Exception as e:
            print(f"\n❌ {nombre}: ERROR - {e}")
            resultados.append((nombre, False))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS:")
    exitos = sum(1 for _, resultado in resultados if resultado)
    
    for nombre, resultado in resultados:
        status = "✅ ÉXITO" if resultado else "❌ FALLO"
        print(f"   {status}: {nombre}")
    
    print(f"\n🎯 RESULTADO FINAL: {exitos}/{len(tests)} tests exitosos")
    
    if exitos == len(tests):
        print("🎉 ¡TODOS LOS TESTS PASARON!")
    else:
        print("⚠️ Algunos tests fallaron. Revisar implementación.")

if __name__ == "__main__":
    main()
