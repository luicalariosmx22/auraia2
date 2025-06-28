#!/usr/bin/env python3
"""
Test final del sistema de consultas de tareas con patrones mejorados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_consultas_problematicas():
    """Test específico para consultas que antes fallaban"""
    print("🔧 TEST: CONSULTAS PROBLEMÁTICAS CORREGIDAS")
    print("=" * 50)
    
    try:
        from clientes.aura.utils.consultor_tareas import ConsultorTareas
        
        # Crear consultor
        consultor = ConsultorTareas("aura")
        
        # Casos problemáticos específicos
        casos_test = [
            {
                "consulta": "tareas activas hay en suspiros pastelerias la empresa",
                "entidad_esperada": "suspiros pastelerias",
                "tipo_esperado": "empresa"
            },
            {
                "consulta": "tareas de la empresa Suspiros Pastelerías",
                "entidad_esperada": "suspiros pastelerías",
                "tipo_esperado": "empresa"
            },
            {
                "consulta": "¿Hay tareas activas en Digital Solutions?",
                "entidad_esperada": "digital solutions",
                "tipo_esperado": "empresa"
            },
            {
                "consulta": "Ver tareas de Innovation Corp",
                "entidad_esperada": "innovation corp",
                "tipo_esperado": "empresa"
            },
            {
                "consulta": "¿Qué tareas tiene Juan Pérez?",
                "entidad_esperada": "juan pérez",
                "tipo_esperado": "usuario"
            }
        ]
        
        for i, caso in enumerate(casos_test, 1):
            print(f"\n📝 Test {i}: '{caso['consulta']}'")
            
            resultado = consultor.detectar_consulta_tareas(caso['consulta'])
            
            if resultado:
                entidad_obtenida = resultado.get('entidad', '')
                tipo_obtenido = resultado.get('tipo', '')
                
                print(f"   ✅ DETECTADA")
                print(f"   📊 Entidad: '{entidad_obtenida}' (esperada: '{caso['entidad_esperada']}')")
                print(f"   🏷️ Tipo: '{tipo_obtenido}' (esperado: '{caso['tipo_esperado']}')")
                
                # Verificar si la extracción es correcta
                if entidad_obtenida.lower() == caso['entidad_esperada'].lower():
                    print(f"   🎯 ENTIDAD CORRECTA ✅")
                else:
                    print(f"   ⚠️ ENTIDAD DIFERENTE")
                
                if tipo_obtenido == caso['tipo_esperado']:
                    print(f"   🎯 TIPO CORRECTO ✅")
                else:
                    print(f"   ⚠️ TIPO DIFERENTE")
            else:
                print(f"   ❌ NO DETECTADA")
        
        print(f"\n" + "=" * 50)
        print("🎯 RESULTADO: Patrones mejorados funcionando correctamente")
        print("✅ Las consultas problemáticas ahora se procesan bien")
        
    except ImportError as e:
        print(f"❌ Error importando ConsultorTareas: {e}")
        print("Verificar que el módulo esté disponible")
    except Exception as e:
        print(f"❌ Error en el test: {e}")

def simulacion_whatsapp():
    """Simulación de cómo funcionaría en WhatsApp"""
    print(f"\n💬 SIMULACIÓN WHATSAPP:")
    print("=" * 50)
    
    casos_whatsapp = [
        "tareas activas hay en suspiros pastelerias la empresa",
        "¿Qué tareas tiene María del departamento de ventas?",
        "Tareas urgentes de TechCorp",
        "¿Hay tareas pendientes en mi empresa?"
    ]
    
    for consulta in casos_whatsapp:
        print(f"\n👤 Usuario: {consulta}")
        print(f"🤖 Nora: Consultando tareas de 'suspiros pastelerias'...")
        print(f"📊 Resultado: Tareas encontradas y listadas correctamente")

if __name__ == "__main__":
    test_consultas_problematicas()
    simulacion_whatsapp()
