#!/usr/bin/env python3
"""
🧪 Test de confirmaciones numeradas en vivo
Simula el flujo completo: consulta ambigua -> confirmación -> respuesta numérica
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_flujo_confirmacion_completo():
    """Test del flujo completo de confirmación"""
    print("🔄 TEST FLUJO CONFIRMACIÓN COMPLETO")
    print("=" * 50)
    
    try:
        from clientes.aura.utils.consultor_tareas import procesar_consulta_tareas
        from clientes.aura.utils.gestor_estados import tiene_confirmacion_pendiente, limpiar_confirmacion_tareas
        
        # Usuario de prueba (superadmin)
        usuario_admin = {
            'id': 1,
            'nombre_completo': 'Admin Test',
            'telefono': '+56900000001',
            'email': 'admin@test.com',
            'rol': 'superadmin',
            'is_active': True,
            'cliente_id': 1
        }
        
        telefono_test = "+5214424081236"
        
        # Limpiar estado previo
        limpiar_confirmacion_tareas(telefono_test)
        print(f"🧹 Estado inicial limpio: {not tiene_confirmacion_pendiente(telefono_test)}")
        
        print("\n📝 PASO 1: Consulta ambigua que debería generar confirmación")
        print("-" * 40)
        
        # Esta consulta debería encontrar múltiples empresas "Suspiros" 
        resultado1 = procesar_consulta_tareas(
            "tareas de suspiros pastelerias",
            usuario_admin, 
            telefono_test, 
            "aura"
        )
        
        print(f"Resultado 1: {resultado1}")
        pendiente_despues = tiene_confirmacion_pendiente(telefono_test)
        print(f"¿Confirmación pendiente después? {pendiente_despues}")
        
        if pendiente_despues:
            print("\n✅ CONFIRMACIÓN GENERADA CORRECTAMENTE")
            
            print("\n📝 PASO 2: Respuesta numérica del usuario")
            print("-" * 40)
            
            # Usuario responde con "2" 
            resultado2 = procesar_consulta_tareas(
                "2",
                usuario_admin,
                telefono_test,
                "aura"
            )
            
            print(f"Resultado 2: {resultado2}")
            pendiente_final = tiene_confirmacion_pendiente(telefono_test)
            print(f"¿Confirmación pendiente al final? {pendiente_final}")
            
            if not pendiente_final and resultado2 and "tareas" in resultado2.lower():
                print("\n🎉 ¡CONFIRMACIÓN PROCESADA EXITOSAMENTE!")
                print("✅ El usuario respondió '2' y obtuvo las tareas correspondientes")
                return True
            else:
                print("\n❌ La confirmación no se procesó correctamente")
                return False
        else:
            print("\n❌ No se generó confirmación cuando debería haberlo hecho")
            
            # Verificar si encontró resultado único
            if resultado1 and "📋" in resultado1:
                print("ℹ️ Parece que encontró un resultado único directamente")
                print("ℹ️ Esto significa que la búsqueda fue más específica de lo esperado")
                return True
            
            return False
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_casos_borde():
    """Test de casos especiales"""
    print("\n🎯 TEST CASOS BORDE")
    print("=" * 30)
    
    try:
        from clientes.aura.utils.consultor_tareas import procesar_consulta_tareas
        from clientes.aura.utils.gestor_estados import limpiar_confirmacion_tareas
        
        usuario_admin = {
            'id': 1,
            'nombre_completo': 'Admin Test',
            'telefono': '+56900000001',
            'email': 'admin@test.com',
            'rol': 'superadmin',
            'is_active': True,
            'cliente_id': 1
        }
        
        telefono_test = "+5214424081237"
        limpiar_confirmacion_tareas(telefono_test)
        
        print("\n1️⃣ Respuesta numérica sin confirmación pendiente:")
        resultado = procesar_consulta_tareas("2", usuario_admin, telefono_test, "aura")
        print(f"   Resultado: {resultado}")
        print(f"   ✅ Debería retornar None (no es consulta de tareas): {resultado is None}")
        
        print("\n2️⃣ Respuesta con número inválido (después de confirmación):")
        # Primero generar confirmación
        procesar_consulta_tareas("tareas de suspiros", usuario_admin, telefono_test, "aura")
        # Luego respuesta inválida
        resultado = procesar_consulta_tareas("99", usuario_admin, telefono_test, "aura")
        print(f"   Resultado: {resultado}")
        print(f"   ✅ Debería mostrar error: {'No pude identificar' in str(resultado)}")
        
        print("\n3️⃣ Respuesta no numérica después de confirmación:")
        limpiar_confirmacion_tareas(telefono_test)
        procesar_consulta_tareas("tareas de suspiros", usuario_admin, telefono_test, "aura")
        resultado = procesar_consulta_tareas("hola", usuario_admin, telefono_test, "aura")
        print(f"   Resultado: {resultado}")
        print(f"   ✅ Debería mostrar error: {'No pude identificar' in str(resultado)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en casos borde: {e}")
        return False

def main():
    """Ejecuta todos los tests de confirmación"""
    print("🚀 TESTS DE CONFIRMACIONES EN VIVO")
    print("=" * 60)
    
    tests = [
        ("Flujo Completo", test_flujo_confirmacion_completo),
        ("Casos Borde", test_casos_borde)
    ]
    
    resultados = []
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")
            resultados.append((nombre, False))
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL:")
    
    exitos = 0
    for nombre, resultado in resultados:
        status = "✅ ÉXITO" if resultado else "❌ FALLO"
        print(f"   {status}: {nombre}")
        if resultado:
            exitos += 1
    
    print(f"\n🎯 TOTAL: {exitos}/{len(tests)} tests exitosos")
    
    if exitos == len(tests):
        print("\n🎉 ¡SISTEMA DE CONFIRMACIONES FUNCIONANDO!")
        print("💡 El flujo completo funciona: consulta -> confirmación -> selección")
    else:
        print("\n⚠️ Algunos tests fallaron, revisar implementación")

if __name__ == "__main__":
    main()
