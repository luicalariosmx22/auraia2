#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 Script de prueba para el sistema unificado de webhooks Meta
Opción 1: Usar solo logs_webhooks_meta
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.meta_webhook_helpers import (
    registrar_evento_supabase,
    obtener_estadisticas_webhooks,
    procesar_eventos_pendientes,
    marcar_evento_procesado
)

# Cargar variables de entorno
load_dotenv()

def test_agregar_campos_tabla():
    """Test 1: Verificar que la tabla tiene los campos necesarios"""
    print("\n🧪 TEST 1: Verificación de estructura de tabla")
    print("=" * 60)
    
    try:
        # Hacer una consulta simple para verificar los campos
        response = supabase.table('logs_webhooks_meta').select('*').limit(1).execute()
        
        if response.data:
            campos = list(response.data[0].keys())
            print(f"✅ Campos actuales en logs_webhooks_meta: {campos}")
            
            # Verificar campos críticos
            campos_necesarios = ['procesado', 'procesado_en', 'tipo_objeto', 'objeto_id', 'timestamp']
            campos_faltantes = [c for c in campos_necesarios if c not in campos]
            
            if campos_faltantes:
                print(f"❌ Campos faltantes: {campos_faltantes}")
                return False
            else:
                print("✅ Todos los campos necesarios están presentes")
                return True
        else:
            print("⚠️ Tabla vacía, agregando un evento de prueba...")
            # Agregar un evento de prueba para verificar estructura
            return test_registrar_evento()
            
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
        return False

def test_registrar_evento():
    """Test 2: Registrar un evento de prueba"""
    print("\n🧪 TEST 2: Registro de evento de prueba")
    print("=" * 60)
    
    try:
        ahora = datetime.utcnow().isoformat()
        
        # Registrar evento de prueba
        resultado = registrar_evento_supabase(
            objeto='campaign',
            objeto_id='test_campaign_123',
            campo='status',
            valor='ACTIVE',
            hora_evento=ahora
        )
        
        if resultado:
            print("✅ Evento registrado exitosamente")
            
            # Verificar que se guardó correctamente
            response = supabase.table('logs_webhooks_meta')\
                .select('*')\
                .eq('objeto_id', 'test_campaign_123')\
                .execute()
            
            if response.data:
                evento = response.data[0]
                print(f"📋 Evento guardado: ID={evento.get('id')}, Procesado={evento.get('procesado', 'NULL')}")
                return evento['id']
            else:
                print("❌ Evento no encontrado después del registro")
                return False
        else:
            print("❌ Error registrando evento")
            return False
            
    except Exception as e:
        print(f"❌ Error en test de registro: {e}")
        return False

def test_obtener_estadisticas():
    """Test 3: Obtener estadísticas"""
    print("\n🧪 TEST 3: Estadísticas de webhooks")
    print("=" * 60)
    
    try:
        stats = obtener_estadisticas_webhooks()
        
        print(f"📊 Total eventos: {stats['total_eventos']}")
        print(f"📊 Eventos procesados: {stats['eventos_procesados']}")
        print(f"📊 Eventos pendientes: {stats['eventos_pendientes']}")
        print(f"📊 Tipos de objeto: {stats['tipos_objeto']}")
        print(f"📊 Última actualización: {stats['ultima_actualizacion']}")
        
        return stats['total_eventos'] > 0
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return False

def test_marcar_procesado(evento_id):
    """Test 4: Marcar evento como procesado"""
    print("\n🧪 TEST 4: Marcar evento como procesado")
    print("=" * 60)
    
    try:
        if not evento_id:
            print("⚠️ No hay evento ID para probar")
            return False
            
        resultado = marcar_evento_procesado(evento_id)
        
        if resultado:
            print(f"✅ Evento {evento_id} marcado como procesado")
            
            # Verificar que se actualizó
            response = supabase.table('logs_webhooks_meta')\
                .select('procesado, procesado_en')\
                .eq('id', evento_id)\
                .execute()
            
            if response.data:
                evento = response.data[0]
                print(f"📋 Estado actualizado: Procesado={evento.get('procesado')}, Fecha={evento.get('procesado_en')}")
                return evento.get('procesado') == True
            else:
                print("❌ No se pudo verificar actualización")
                return False
        else:
            print("❌ Error marcando evento como procesado")
            return False
            
    except Exception as e:
        print(f"❌ Error en test marcar procesado: {e}")
        return False

def test_procesar_eventos_pendientes():
    """Test 5: Procesar eventos pendientes"""
    print("\n🧪 TEST 5: Procesamiento de eventos pendientes")
    print("=" * 60)
    
    try:
        # Agregar algunos eventos sin procesar
        eventos_test = []
        for i in range(3):
            ahora = datetime.utcnow().isoformat()
            resultado = registrar_evento_supabase(
                objeto='ad',
                objeto_id=f'test_ad_{i}',
                campo='status',
                valor='PAUSED',
                hora_evento=ahora
            )
            if resultado:
                eventos_test.append(f'test_ad_{i}')
        
        print(f"📝 Creados {len(eventos_test)} eventos de prueba")
        
        # Procesar eventos pendientes
        procesados = procesar_eventos_pendientes()
        print(f"✅ Procesados {procesados} eventos")
        
        return procesados > 0
        
    except Exception as e:
        print(f"❌ Error en test procesar eventos: {e}")
        return False

def test_api_endpoints():
    """Test 6: Simular llamadas a los endpoints API"""
    print("\n🧪 TEST 6: Simulación de endpoints API")
    print("=" * 60)
    
    try:
        # Test estadísticas (simular lógica del endpoint)
        print("📡 Simulando /api/webhooks/estadisticas...")
        
        eventos_response = supabase.table('logs_webhooks_meta')\
            .select('tipo_objeto, procesado')\
            .execute()
        
        eventos = eventos_response.data or []
        total_eventos = len(eventos)
        procesados = len([e for e in eventos if e.get('procesado', False)])
        no_procesados = total_eventos - procesados
        
        tipos_objeto = {}
        for evento in eventos:
            tipo = evento.get('tipo_objeto', 'unknown')
            tipos_objeto[tipo] = tipos_objeto.get(tipo, 0) + 1
        
        estadisticas = {
            'total_eventos': total_eventos,
            'procesados': procesados,
            'no_procesados': no_procesados,
            'tipos_objeto': tipos_objeto
        }
        
        print(f"✅ Estadísticas API: {estadisticas}")
        
        # Test obtener eventos (simular lógica del endpoint)
        print("📡 Simulando /api/webhooks/eventos...")
        
        query = supabase.table('logs_webhooks_meta').select('*')
        response = query.order('timestamp', desc=True).limit(5).execute()
        
        eventos = response.data or []
        print(f"✅ Eventos obtenidos: {len(eventos)}")
        
        for evento in eventos[:2]:
            print(f"   📋 {evento.get('tipo_objeto')} - {evento.get('objeto_id')} - Procesado: {evento.get('procesado', False)}")
        
        return total_eventos > 0
        
    except Exception as e:
        print(f"❌ Error simulando endpoints: {e}")
        return False

def limpiar_eventos_test():
    """Limpiar eventos de prueba"""
    print("\n🧹 Limpiando eventos de prueba...")
    
    try:
        # Eliminar eventos de prueba
        response = supabase.table('logs_webhooks_meta')\
            .delete()\
            .like('objeto_id', 'test_%')\
            .execute()
        
        print("✅ Eventos de prueba eliminados")
        
    except Exception as e:
        print(f"⚠️ Error limpiando eventos: {e}")

def main():
    """Ejecutar todos los tests"""
    print("🚀 INICIANDO TESTS DEL SISTEMA WEBHOOKS UNIFICADO")
    print("=" * 80)
    print("📋 Opción 1: Usar solo logs_webhooks_meta")
    print("=" * 80)
    
    tests_pasados = 0
    total_tests = 6
    
    # Test 1: Verificar estructura
    if test_agregar_campos_tabla():
        tests_pasados += 1
    
    # Test 2: Registrar evento
    evento_id = test_registrar_evento()
    if evento_id:
        tests_pasados += 1
    
    # Test 3: Estadísticas
    if test_obtener_estadisticas():
        tests_pasados += 1
    
    # Test 4: Marcar procesado
    if test_marcar_procesado(evento_id):
        tests_pasados += 1
    
    # Test 5: Procesar pendientes
    if test_procesar_eventos_pendientes():
        tests_pasados += 1
    
    # Test 6: API endpoints
    if test_api_endpoints():
        tests_pasados += 1
    
    # Resultados finales
    print("\n" + "=" * 80)
    print("📊 RESULTADOS FINALES")
    print("=" * 80)
    print(f"✅ Tests pasados: {tests_pasados}/{total_tests}")
    print(f"📈 Porcentaje de éxito: {(tests_pasados/total_tests)*100:.1f}%")
    
    if tests_pasados == total_tests:
        print("🎉 ¡TODOS LOS TESTS PASARON! El sistema webhooks unificado está funcionando correctamente.")
        estado = "EXITOSO"
    elif tests_pasados >= total_tests * 0.8:
        print("⚠️ La mayoría de tests pasaron. Revisar los fallos menores.")
        estado = "PARCIAL"
    else:
        print("❌ Varios tests fallaron. Revisar la implementación.")
        estado = "FALLIDO"
    
    # Preguntar si limpiar
    try:
        respuesta = input("\n🧹 ¿Limpiar eventos de prueba? (y/N): ").lower()
        if respuesta in ['y', 'yes', 's', 'si']:
            limpiar_eventos_test()
    except KeyboardInterrupt:
        print("\n👋 Test interrumpido por el usuario")
    
    print(f"\n🏁 Test completado con estado: {estado}")
    
    # Instrucciones siguientes
    if estado == "EXITOSO":
        print("\n💡 PRÓXIMOS PASOS:")
        print("1. ✅ El sistema está listo para usar")
        print("2. 🔄 Actualizar el frontend para usar los nuevos campos")
        print("3. 🚀 Desplegar los cambios a producción")
        print("4. 📊 Monitorear estadísticas en el panel")
    
    return estado == "EXITOSO"

if __name__ == "__main__":
    main()
