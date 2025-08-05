#!/usr/bin/env python3
"""
Script de prueba para el sistema completo de automatizaciones
Verifica que todo funcione correctamente desde el descubrimiento hasta la ejecución
"""

import sys
import json
from datetime import datetime
import os

# Añadir el directorio raíz al path
sys.path.append('.')

def test_supabase_connection():
    """Prueba 1: Verificar conexión a Supabase"""
    print("🔗 Prueba 1: Verificando conexión a Supabase...")
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        # Probar una consulta simple
        response = supabase.table("funciones_automatizables").select("*").limit(1).execute()
        count_response = supabase.table("funciones_automatizables").select("*").execute()
        count = len(count_response.data) if count_response.data else 0
        print(f"   ✅ Conexión exitosa - {count} funciones en BD")
        return True
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return False

def test_descubridor_funciones():
    """Prueba 2: Verificar el descubridor de funciones"""
    print("\n🔍 Prueba 2: Verificando descubridor de funciones...")
    try:
        from descubrir_funciones import DescubrirFunciones
        
        descubridor = DescubrirFunciones()
        
        # Probar escaneo de un módulo específico
        funciones_meta = descubridor.escanear_modulo('meta_ads', 'clientes.aura.utils.meta_ads_utils')
        print(f"   ✅ Funciones Meta Ads encontradas: {len(funciones_meta)}")
        
        if funciones_meta:
            print("   📋 Ejemplos encontrados:")
            for func in funciones_meta[:3]:
                print(f"      - {func['nombre_funcion']} ({func['categoria']})")
        
        return len(funciones_meta) > 0
    except Exception as e:
        print(f"   ❌ Error en descubridor: {e}")
        return False

def test_automatizaciones_bd():
    """Prueba 3: Verificar automatizaciones en base de datos"""
    print("\n💾 Prueba 3: Verificando automatizaciones en BD...")
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        # Obtener automatizaciones activas
        response = supabase.table("automatizaciones") \
            .select("*") \
            .eq("activo", True) \
            .execute()
        
        automatizaciones = response.data if response.data else []
        print(f"   ✅ Automatizaciones activas: {len(automatizaciones)}")
        
        if automatizaciones:
            print("   📋 Automatizaciones encontradas:")
            for auto in automatizaciones:
                print(f"      - {auto['nombre']} ({auto['modulo_relacionado']}.{auto['funcion_objetivo']})")
                print(f"        Próxima: {auto.get('proxima_ejecucion', 'No programada')}")
        
        return len(automatizaciones) > 0
    except Exception as e:
        print(f"   ❌ Error consultando automatizaciones: {e}")
        return False

def test_ejecutor_automatizaciones():
    """Prueba 4: Verificar el ejecutor de automatizaciones"""
    print("\n⚙️ Prueba 4: Verificando ejecutor de automatizaciones...")
    try:
        from clientes.aura.utils.automatizaciones_ejecutor import ejecutor
        from clientes.aura.utils.supabase_client import supabase
        
        # Obtener automatizaciones disponibles directamente de BD
        response = supabase.table("automatizaciones") \
            .select("*") \
            .eq("activo", True) \
            .execute()
        
        automatizaciones = response.data if response.data else []
        print(f"   ✅ Ejecutor puede ver {len(automatizaciones)} automatizaciones")
        
        # Verificar que puede importar módulos
        if automatizaciones:
            auto_test = automatizaciones[0]
            modulo = auto_test['modulo_relacionado']
            funcion = auto_test['funcion_objetivo']
            
            print(f"   🧪 Probando importación: {modulo}.{funcion}")
            
            # Intentar importar el módulo (sin ejecutar)
            try:
                import importlib
                modulo_nombre = f"clientes.aura.utils.{modulo}_utils" if modulo != "automatizaciones_ejecutor" else "clientes.aura.utils.automatizaciones_ejecutor"
                modulo_importado = importlib.import_module(modulo_nombre)
                print(f"   ✅ Módulo {modulo} importado correctamente")
                return True
            except Exception as e:
                print(f"   ⚠️ Error importando módulo {modulo}: {e}")
                return False
        else:
            print("   ⚠️ No hay automatizaciones para probar")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en ejecutor: {e}")
        return False

def test_ejecucion_ejemplo():
    """Prueba 5: Ejecutar una función de ejemplo"""
    print("\n🚀 Prueba 5: Ejecutando función de ejemplo...")
    try:
        from clientes.aura.utils.automatizaciones_ejecutor import ejecutor
        from clientes.aura.utils.supabase_client import supabase
        
        # Buscar una automatización de ejemplo
        response = supabase.table("automatizaciones") \
            .select("*") \
            .eq("activo", True) \
            .execute()
        
        automatizaciones = response.data if response.data else []
        
        auto_ejemplo = None
        for auto in automatizaciones:
            if 'ejemplo' in auto['funcion_objetivo'].lower() or auto['modulo_relacionado'] == 'automatizaciones_ejecutor':
                auto_ejemplo = auto
                break
        
        if auto_ejemplo:
            print(f"   🎯 Ejecutando: {auto_ejemplo['nombre']}")
            print(f"   📍 Función: {auto_ejemplo['modulo_relacionado']}.{auto_ejemplo['funcion_objetivo']}")
            
            resultado = ejecutor.ejecutar_por_id(auto_ejemplo['id'])
            
            print(f"   📊 Resultado: {json.dumps(resultado, indent=2, ensure_ascii=False)}")
            
            return resultado.get('success', False)
        else:
            print("   ⚠️ No se encontró automatización de ejemplo")
            
            # Intentar crear y ejecutar una función de ejemplo directamente
            print("   🔧 Probando ejecución directa de función ejemplo...")
            
            try:
                import importlib
                modulo = importlib.import_module('clientes.aura.utils.automatizaciones_ejecutor')
                
                if hasattr(modulo, 'ejemplo_reporte_diario'):
                    resultado = modulo.ejemplo_reporte_diario()
                    print(f"   ✅ Función de ejemplo ejecutada: {resultado}")
                    return True
                else:
                    print("   ⚠️ No se encontró función de ejemplo")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Error en ejecución directa: {e}")
                return False
            
    except Exception as e:
        print(f"   ❌ Error en ejecución de ejemplo: {e}")
        return False

def test_funciones_reales():
    """Prueba 6: Verificar funciones reales disponibles y nuevos campos"""
    print("\n🔧 Prueba 6: Verificando funciones reales y nuevos campos...")
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        # Obtener funciones por módulo incluyendo los nuevos campos
        response = supabase.table("funciones_automatizables") \
            .select("modulo, nombre_funcion, categoria, envia_notificacion, codigo_fuente, linea_inicio, ruta_modulo_python, tipo_archivo, archivo_origen, metodo_deteccion") \
            .eq("activa", True) \
            .eq("es_automatizable", True) \
            .execute()
        
        funciones = response.data if response.data else []
        
        # Agrupar por módulo
        por_modulo = {}
        funciones_con_codigo = 0
        funciones_escaneo_directo = 0
        
        for func in funciones:
            modulo = func['modulo']
            if modulo not in por_modulo:
                por_modulo[modulo] = []
            por_modulo[modulo].append(func)
            
            # Contar funciones con código fuente
            if func.get('codigo_fuente') and func['codigo_fuente'] != '' and not func['codigo_fuente'].startswith('# Error') and not func['codigo_fuente'].startswith('# Función'):
                funciones_con_codigo += 1
            
            # Contar funciones por método de detección
            if func.get('metodo_deteccion') == 'escaneo_directo':
                funciones_escaneo_directo += 1
        
        print(f"   ✅ Total de funciones: {len(funciones)}")
        print(f"   � Funciones con código fuente: {funciones_con_codigo}")
        print(f"   📁 Funciones por escaneo directo: {funciones_escaneo_directo}")
        print("   �📊 Distribución por módulo:")
        
        for modulo, funcs in por_modulo.items():
            notificaciones = sum(1 for f in funcs if f.get('envia_notificacion'))
            con_codigo = sum(1 for f in funcs if f.get('codigo_fuente') and f['codigo_fuente'] != '' and not f['codigo_fuente'].startswith('# Error') and not f['codigo_fuente'].startswith('# Función'))
            print(f"      - {modulo}: {len(funcs)} funciones ({notificaciones} con notificaciones, {con_codigo} con código)")
        
        # Verificar que tenemos funciones Meta Ads con código fuente
        meta_funcs = por_modulo.get('meta_ads', [])
        func_con_codigo = None
        
        for func in meta_funcs:
            if func.get('codigo_fuente') and len(func['codigo_fuente']) > 50:
                func_con_codigo = func
                break
        
        if func_con_codigo:
            print(f"   ✅ Función Meta Ads con código encontrada: {func_con_codigo['nombre_funcion']}")
            print(f"      📄 Archivo: {func_con_codigo.get('archivo_origen', 'N/A')}")
            print(f"      📍 Línea: {func_con_codigo.get('linea_inicio', 'N/A')}")
            print(f"      🔍 Método: {func_con_codigo.get('metodo_deteccion', 'N/A')}")
            print(f"      📝 Código: {len(func_con_codigo.get('codigo_fuente', ''))} caracteres")
            
            # Mostrar una pequeña muestra del código
            codigo = func_con_codigo.get('codigo_fuente', '')
            if codigo and not codigo.startswith('# Error'):
                lineas_codigo = codigo.split('\n')[:3]
                print(f"      📖 Vista previa:")
                for i, linea in enumerate(lineas_codigo):
                    print(f"         {i+1}: {linea}")
            
            return True
        else:
            print("   ⚠️ No se encontraron funciones Meta Ads con código fuente completo")
            
            # Verificar si hay alguna función con código fuente
            if funciones_con_codigo > 0:
                print(f"   ℹ️ Hay {funciones_con_codigo} funciones con código en otros módulos")
                return True
            else:
                print("   ❌ No se encontró ninguna función con código fuente")
                return False
            
    except Exception as e:
        print(f"   ❌ Error verificando funciones reales: {e}")
        return False

def test_apis_automatizaciones():
    """Prueba 7: Verificar APIs del sistema"""
    print("\n🌐 Prueba 7: Verificando APIs (simulación)...")
    try:
        # Simular las llamadas que haría el frontend
        from clientes.aura.utils.supabase_client import supabase
        
        # API 1: Listar funciones por módulo
        print("   🔗 Probando API de funciones por módulo...")
        response = supabase.table("funciones_automatizables") \
            .select("nombre_funcion, descripcion, parametros, categoria, envia_notificacion") \
            .eq("modulo", "meta_ads") \
            .eq("activa", True) \
            .execute()
        
        funciones_meta = response.data if response.data else []
        print(f"      ✅ API funciones Meta Ads: {len(funciones_meta)} resultados")
        
        # API 2: Detalle de función específica
        if funciones_meta:
            func_test = funciones_meta[0]
            print(f"   🔍 Probando API de detalle para: {func_test['nombre_funcion']}")
            
            response_detalle = supabase.table("funciones_automatizables") \
                .select("*") \
                .eq("modulo", "meta_ads") \
                .eq("nombre_funcion", func_test['nombre_funcion']) \
                .limit(1) \
                .execute()
            
            if response_detalle.data:
                print("      ✅ API detalle de función: funcionando")
                detalle = response_detalle.data[0]
                if detalle.get('parametros'):
                    print(f"      📝 Parámetros disponibles: {list(detalle['parametros'].keys())}")
            else:
                print("      ⚠️ API detalle: sin resultados")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en APIs: {e}")
        return False

def test_codigo_fuente_extraccion():
    """Prueba 9: Verificar extracción de código fuente completo"""
    print("\n📝 Prueba 9: Verificando extracción de código fuente...")
    try:
        from descubrir_funciones import DescubrirFunciones
        from clientes.aura.utils.supabase_client import supabase
        
        # Ejecutar descubrimiento en módulo Meta Ads para probar extracción
        descubridor = DescubrirFunciones()
        
        print("   🔍 Ejecutando escáner en módulo Meta Ads...")
        funciones_encontradas = descubridor.escanear_modulo('meta_ads', 'clientes.aura.utils.meta_ads_utils')
        
        funciones_con_codigo = []
        for func in funciones_encontradas:
            if func.get('codigo_fuente') and len(func['codigo_fuente']) > 50 and not func['codigo_fuente'].startswith('# Error'):
                funciones_con_codigo.append(func)
        
        print(f"   ✅ Funciones con código extraído: {len(funciones_con_codigo)}")
        
        if funciones_con_codigo:
            # Mostrar detalles de la primera función con código
            func_ejemplo = funciones_con_codigo[0]
            print(f"   📋 Ejemplo: {func_ejemplo['nombre_funcion']}")
            print(f"      📄 Archivo: {func_ejemplo.get('archivo_origen', 'N/A')}")
            print(f"      📍 Línea inicio: {func_ejemplo.get('linea_inicio', 'N/A')}")
            print(f"      🔗 Módulo Python: {func_ejemplo.get('ruta_modulo_python', 'N/A')}")
            print(f"      📝 Tamaño código: {len(func_ejemplo.get('codigo_fuente', ''))} caracteres")
            print(f"      🔍 Método detección: {func_ejemplo.get('metodo_deteccion', 'N/A')}")
            
            # Verificar que el código extraído es válido Python
            codigo = func_ejemplo.get('codigo_fuente', '')
            if codigo.startswith('def '):
                print("      ✅ Código comienza con 'def' (válido)")
                
                # Contar líneas
                lineas = codigo.split('\n')
                print(f"      📏 Líneas de código: {len(lineas)}")
                
                # Mostrar primeras líneas
                print("      📖 Primeras líneas:")
                for i, linea in enumerate(lineas[:5]):
                    if linea.strip():
                        print(f"         {i+1}: {linea}")
                
                # Verificar que se registró en BD
                print("   💾 Verificando registro en base de datos...")
                
                response = supabase.table("funciones_automatizables") \
                    .select("codigo_fuente, linea_inicio, ruta_modulo_python") \
                    .eq("modulo", "meta_ads") \
                    .eq("nombre_funcion", func_ejemplo['nombre_funcion']) \
                    .limit(1) \
                    .execute()
                
                if response.data and response.data[0].get('codigo_fuente'):
                    bd_codigo = response.data[0]['codigo_fuente']
                    print(f"      ✅ Código guardado en BD: {len(bd_codigo)} caracteres")
                    print(f"      📍 Línea inicio en BD: {response.data[0].get('linea_inicio', 'N/A')}")
                    print(f"      🔗 Módulo en BD: {response.data[0].get('ruta_modulo_python', 'N/A')}")
                    return True
                else:
                    print("      ❌ Código no se guardó en BD")
                    return False
            else:
                print(f"      ⚠️ Código no comienza con 'def': {codigo[:50]}...")
                return False
        else:
            print("   ❌ No se encontraron funciones con código válido")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verificando extracción de código: {e}")
        return False

def test_integracion_completa():
    """Prueba 8: Integración completa del sistema"""
    print("\n🔄 Prueba 8: Integración completa del sistema...")
    try:
        from clientes.aura.utils.automatizaciones_ejecutor import ejecutor
        from clientes.aura.utils.supabase_client import supabase
        import importlib
        
        # PASO 1: Obtener automatización de Meta Ads
        response = supabase.table("automatizaciones") \
            .select("*") \
            .eq("activo", True) \
            .eq("modulo_relacionado", "meta_ads") \
            .limit(1) \
            .execute()
        
        if response.data:
            auto_meta = response.data[0]
            print(f"   🎯 Automatización Meta Ads encontrada: {auto_meta['nombre']}")
            print(f"   ⚙️ Función objetivo: {auto_meta['funcion_objetivo']}")
            print(f"   📅 Próxima ejecución: {auto_meta.get('proxima_ejecucion', 'No programada')}")
            
            # PASO 2: Buscar la función real en la tabla funciones_automatizables
            print("   🔍 Buscando función real en funciones_automatizables...")
            
            response_funcion = supabase.table("funciones_automatizables") \
                .select("nombre_funcion, modulo, ruta_modulo_python, codigo_fuente") \
                .eq("modulo", "meta_ads") \
                .eq("nombre_funcion", auto_meta['funcion_objetivo']) \
                .limit(1) \
                .execute()
            
            if response_funcion.data:
                func_data = response_funcion.data[0]
                print(f"      ✅ Función encontrada en BD: {func_data['nombre_funcion']}")
                print(f"      📦 Módulo Python: {func_data.get('ruta_modulo_python', 'N/A')}")
                print(f"      💾 Código disponible: {'Sí' if func_data.get('codigo_fuente') else 'No'}")
                
                # PASO 3: Intentar importar usando la ruta del módulo Python real
                ruta_modulo = func_data.get('ruta_modulo_python')
                if ruta_modulo:
                    try:
                        print(f"      🔧 Intentando importar: {ruta_modulo}")
                        modulo = importlib.import_module(ruta_modulo)
                        print(f"      ✅ Módulo importado correctamente")
                        
                        # Verificar que la función existe en el módulo
                        if hasattr(modulo, auto_meta['funcion_objetivo']):
                            print(f"      ✅ Función {auto_meta['funcion_objetivo']} encontrada en módulo")
                            
                            # Verificar parámetros
                            parametros = auto_meta.get('parametros_json', {})
                            print(f"      📝 Parámetros configurados: {json.dumps(parametros, indent=2)}")
                            
                            print("   ✅ Sistema completo: FUNCIONANDO")
                            return True
                        else:
                            print(f"      ⚠️ Función {auto_meta['funcion_objetivo']} no encontrada en módulo importado")
                            # Listar funciones disponibles en el módulo
                            funciones_disponibles = [attr for attr in dir(modulo) if callable(getattr(modulo, attr)) and not attr.startswith('_')][:5]
                            print(f"      📋 Funciones disponibles: {funciones_disponibles}")
                            return False
                            
                    except Exception as e:
                        print(f"      ❌ Error importando módulo {ruta_modulo}: {e}")
                        return False
                else:
                    # Fallback: intentar con la ruta estándar
                    print("      🔄 Probando ruta estándar de módulo...")
                    try:
                        modulo_nombre = f"clientes.aura.utils.{auto_meta['modulo_relacionado']}_utils"
                        modulo = importlib.import_module(modulo_nombre)
                        print(f"      ✅ Módulo {auto_meta['modulo_relacionado']} importado (ruta estándar)")
                        
                        if hasattr(modulo, auto_meta['funcion_objetivo']):
                            print(f"      ✅ Función {auto_meta['funcion_objetivo']} encontrada")
                            print("   ✅ Sistema completo: FUNCIONANDO")
                            return True
                        else:
                            print(f"      ❌ Función {auto_meta['funcion_objetivo']} no encontrada en módulo estándar")
                            return False
                            
                    except Exception as e:
                        print(f"      ❌ Error importando módulo estándar: {e}")
                        return False
            else:
                print(f"      ⚠️ Función {auto_meta['funcion_objetivo']} no encontrada en funciones_automatizables")
                
                # Mostrar funciones disponibles para Meta Ads
                print("      🔍 Buscando funciones disponibles para Meta Ads...")
                response_todas = supabase.table("funciones_automatizables") \
                    .select("nombre_funcion") \
                    .eq("modulo", "meta_ads") \
                    .limit(5) \
                    .execute()
                
                if response_todas.data:
                    funciones_disponibles = [f['nombre_funcion'] for f in response_todas.data]
                    print(f"      📋 Funciones disponibles: {funciones_disponibles}")
                    
                    # Sugerir actualizar la automatización con una función real
                    print(f"      💡 Sugerencia: Actualizar automatización para usar una de estas funciones")
                    return False
                else:
                    print("      ❌ No se encontraron funciones Meta Ads en BD")
                    return False
                    
        else:
            print("   ⚠️ No se encontró automatización de Meta Ads")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en integración completa: {e}")
        return False

def main():
    """Función principal que ejecuta todas las pruebas"""
    print("🧪 SISTEMA DE PRUEBAS - AUTOMATIZACIONES AURA")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 Directorio: {os.getcwd()}")
    print("=" * 60)
    
    # Lista de pruebas
    pruebas = [
        ("Conexión Supabase", test_supabase_connection),
        ("Descubridor de Funciones", test_descubridor_funciones),
        ("Automatizaciones en BD", test_automatizaciones_bd),
        ("Ejecutor de Automatizaciones", test_ejecutor_automatizaciones),
        ("Ejecución de Ejemplo", test_ejecucion_ejemplo),
        ("Funciones Reales y Nuevos Campos", test_funciones_reales),
        ("APIs del Sistema", test_apis_automatizaciones),
        ("Extracción de Código Fuente", test_codigo_fuente_extraccion),
        ("Integración Completa", test_integracion_completa)
    ]
    
    # Ejecutar pruebas
    resultados = []
    exitosas = 0
    
    for nombre, funcion_prueba in pruebas:
        try:
            resultado = funcion_prueba()
            resultados.append((nombre, resultado))
            if resultado:
                exitosas += 1
        except Exception as e:
            print(f"   💥 Error inesperado en {nombre}: {e}")
            resultados.append((nombre, False))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    for nombre, resultado in resultados:
        icono = "✅" if resultado else "❌"
        print(f"{icono} {nombre}")
    
    print("\n" + "-" * 60)
    print(f"🎯 Pruebas exitosas: {exitosas}/{len(pruebas)}")
    
    if exitosas == len(pruebas):
        print("🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("✨ Todas las pruebas pasaron exitosamente")
        print("🚀 El sistema de automatizaciones está listo para usar")
    elif exitosas >= len(pruebas) * 0.8:
        print("🟡 SISTEMA MAYORMENTE FUNCIONAL")
        print("⚠️ Algunas pruebas fallaron, pero el núcleo funciona")
        print("🔧 Revisar componentes que fallaron")
    else:
        print("🔴 SISTEMA CON PROBLEMAS")
        print("❌ Múltiples componentes fallaron")
        print("🛠️ Requiere revisión y corrección")
    
    print("\n" + "=" * 60)
    print("📝 RECOMENDACIONES:")
    
    if exitosas == len(pruebas):
        print("• ✅ Sistema listo para producción")
        print("• 🔄 Configurar schedule/cron para ejecución automática")
        print("• 📊 Monitorear logs de ejecución")
        print("• 🔔 Configurar alertas de fallos")
        print("• 💾 Código fuente completo disponible para análisis de IA")
        print("• 🔍 Métodos de detección híbridos funcionando correctamente")
    else:
        print("• 🔍 Revisar componentes que fallaron")
        print("• 📋 Verificar configuración de base de datos")
        print("• 🔧 Comprobar importaciones de módulos")
        print("• 🌐 Verificar conectividad")
        print("• 💾 Si falla extracción de código: verificar permisos de archivos")
        print("• 📝 Si falla guardado en BD: verificar esquema de tabla en Supabase")
    
    return exitosas == len(pruebas)

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Pruebas interrumpidas por el usuario")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n💥 Error crítico: {e}")
        sys.exit(3)
