#!/usr/bin/env python3
"""
🔍 Verificación simple del gestor de estados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_gestor_estados_simple():
    """Test básico del gestor de estados sin dependencias complejas"""
    print("🔄 TEST GESTOR ESTADOS BÁSICO")
    print("=" * 30)
    
    try:
        # Importar solo el gestor de estados
        from clientes.aura.utils.gestor_estados import (
            establecer_confirmacion_tareas,
            tiene_confirmacion_pendiente,
            obtener_confirmacion_tareas,
            limpiar_confirmacion_tareas
        )
        
        telefono_test = "+5214424081236"
        
        print("1️⃣ Estado inicial:")
        tiene_inicial = tiene_confirmacion_pendiente(telefono_test)
        print(f"   Confirmación pendiente: {tiene_inicial}")
        
        print("\n2️⃣ Establecer confirmación:")
        consulta_info = {"entidad": "suspiros", "tipo": "empresa"}
        info_busqueda = {
            "empresas_encontradas": [
                {"id": 1, "nombre_empresa": "SUSPIROS CAKES - BORIS"},
                {"id": 2, "nombre_empresa": "SUSPIROS PASTELERIAS"},
                {"id": 3, "nombre_empresa": "Suspiros Pastelerias"}
            ],
            "requiere_confirmacion": True
        }
        
        establecer_confirmacion_tareas(telefono_test, consulta_info, info_busqueda)
        
        print("\n3️⃣ Verificar confirmación establecida:")
        tiene_despues = tiene_confirmacion_pendiente(telefono_test)
        print(f"   Confirmación pendiente: {tiene_despues}")
        
        if tiene_despues:
            datos = obtener_confirmacion_tareas(telefono_test)
            print(f"   Datos recuperados: {datos is not None}")
            if datos:
                print(f"   Entidad: {datos.get('consulta_info', {}).get('entidad')}")
                print(f"   Opciones: {len(datos.get('info_busqueda', {}).get('empresas_encontradas', []))}")
        
        print("\n4️⃣ Limpiar confirmación:")
        limpiar_confirmacion_tareas(telefono_test)
        tiene_final = tiene_confirmacion_pendiente(telefono_test)
        print(f"   Confirmación pendiente final: {tiene_final}")
        
        return not tiene_inicial and tiene_despues and not tiene_final
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_procesamiento_numero():
    """Test de procesamiento de respuesta numérica"""
    print("\n📊 TEST PROCESAMIENTO NÚMERO")
    print("=" * 30)
    
    try:
        # Simular datos de confirmación
        empresas_mock = [
            {"id": 1, "nombre_empresa": "SUSPIROS CAKES - BORIS"},
            {"id": 2, "nombre_empresa": "SUSPIROS PASTELERIAS"},
            {"id": 3, "nombre_empresa": "Suspiros Pastelerias"}
        ]
        
        def procesar_respuesta_numerica(respuesta, opciones):
            """Simulación simple del procesamiento"""
            respuesta = respuesta.strip()
            
            # Intentar convertir a número
            try:
                numero = int(respuesta)
                if 1 <= numero <= len(opciones):
                    return opciones[numero - 1]
            except ValueError:
                pass
            
            # Buscar por nombre
            respuesta_lower = respuesta.lower()
            for opcion in opciones:
                if respuesta_lower in opcion["nombre_empresa"].lower():
                    return opcion
            
            return None
        
        # Tests
        casos = [
            ("2", empresas_mock, empresas_mock[1]),  # Selección numérica
            ("1", empresas_mock, empresas_mock[0]),  # Primera opción
            ("pastelerias", empresas_mock, empresas_mock[1]),  # Por nombre
            ("99", empresas_mock, None),  # Número inválido
            ("xyz", empresas_mock, None)  # Nombre inválido
        ]
        
        exitos = 0
        for respuesta, opciones, esperado in casos:
            resultado = procesar_respuesta_numerica(respuesta, opciones)
            es_correcto = resultado == esperado
            
            print(f"\n   Respuesta: '{respuesta}'")
            print(f"   Esperado: {esperado['nombre_empresa'] if esperado else 'None'}")
            print(f"   Obtenido: {resultado['nombre_empresa'] if resultado else 'None'}")
            print(f"   ✅ {'Correcto' if es_correcto else '❌ Incorrecto'}")
            
            if es_correcto:
                exitos += 1
        
        print(f"\n📊 Resultado: {exitos}/{len(casos)} casos correctos")
        return exitos == len(casos)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTS SIMPLES DE CONFIRMACIÓN")
    print("=" * 40)
    
    test1 = test_gestor_estados_simple()
    test2 = test_procesamiento_numero()
    
    print("\n" + "=" * 40)
    print("📊 RESUMEN:")
    print(f"   ✅ Gestor Estados: {'ÉXITO' if test1 else 'FALLO'}")
    print(f"   ✅ Proc. Números: {'ÉXITO' if test2 else 'FALLO'}")
    
    if test1 and test2:
        print("\n🎉 ¡FUNCIONALIDAD BÁSICA CORRECTA!")
        print("💡 El problema puede estar en la integración con WhatsApp")
    else:
        print("\n⚠️ Problemas en funcionalidad básica")
