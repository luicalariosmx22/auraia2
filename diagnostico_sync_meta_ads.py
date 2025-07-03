#!/usr/bin/env python3
"""
Script de diagnóstico para la sincronización de Meta Ads
Verifica las optimizaciones sin necesidad de dependencias completas
"""

def analizar_funcion_sincronizacion():
    """Analiza el código de sincronización para verificar optimizaciones"""
    
    archivo = 'clientes/aura/routes/reportes_meta_ads/estadisticas.py'
    
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        # Verificar optimizaciones clave
        optimizaciones = {
            'timeout_reducido': 'timeout=15' in contenido or 'timeout=10' in contenido,
            'limite_requests': 'max_requests' in contenido,
            'manejo_rate_limit': 'status_code == 429' in contenido,
            'limite_anuncios': 'len(datos_a) > 100' in contenido,
            'timeout_retries': 'timeout_retries' in contenido,
            'batch_requests': 'obtener_nombres_batch' in contenido,
            'manejo_errores_segunda_consulta': 'except Exception as e:' in contenido and 'datos_b = []' in contenido
        }
        
        print("🔍 ANÁLISIS DE OPTIMIZACIONES DE SINCRONIZACIÓN META ADS")
        print("=" * 60)
        
        todas_ok = True
        for nombre, presente in optimizaciones.items():
            status = "✅" if presente else "❌"
            print(f"{status} {nombre.replace('_', ' ').title()}: {'Presente' if presente else 'Faltante'}")
            if not presente:
                todas_ok = False
        
        print("\n" + "=" * 60)
        if todas_ok:
            print("✅ TODAS LAS OPTIMIZACIONES ESTÁN PRESENTES")
            print("🚀 El sistema debería manejar mejor los timeouts y cuelgues")
        else:
            print("⚠️  ALGUNAS OPTIMIZACIONES FALTAN")
            
        # Contar líneas de logging añadidas
        logging_lines = contenido.count('[SYNC]')
        print(f"📊 Líneas de logging encontradas: {logging_lines}")
        
        # Verificar funciones críticas
        funciones_criticas = [
            'def sincronizar_anuncios_meta_ads',
            'def fetch_all',
            'def obtener_nombres_batch'
        ]
        
        print("\n🔧 FUNCIONES CRÍTICAS:")
        for funcion in funciones_criticas:
            presente = funcion in contenido
            status = "✅" if presente else "❌"
            print(f"{status} {funcion}")
            
        return todas_ok
        
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {archivo}")
        return False
    except Exception as e:
        print(f"❌ Error analizando archivo: {e}")
        return False

def sugerir_proximos_pasos():
    """Sugiere los próximos pasos para resolver el problema"""
    
    print("\n🛠️  PRÓXIMOS PASOS SUGERIDOS:")
    print("=" * 40)
    print("1. 🔄 Reiniciar el proceso de sincronización")
    print("2. 👀 Monitorear los logs más detallados")
    print("3. ⏱️  Si se cuelga en 'Anuncios encontrados (A)', el problema está en la segunda consulta")
    print("4. 🔥 Si persiste, reducir aún más el timeout o saltar cuentas problemáticas")
    print("5. 📈 Considerar procesar las cuentas de una en una para diagnóstico")
    
    print("\n🔍 PUNTOS DE DIAGNÓSTICO:")
    print("- Si se detiene en '[SYNC] Preparando segunda consulta': problema en params_b")
    print("- Si se detiene en '[SYNC] Iniciando segunda consulta': problema en fetch_all")
    print("- Si se detiene en '[SYNC] Recopilando IDs únicos': problema en procesamiento")
    print("- Si se detiene en '[SYNC] Obteniendo nombres': problema en batch requests")

def main():
    print("🚀 DIAGNÓSTICO DE SINCRONIZACIÓN META ADS")
    print("Analizando optimizaciones implementadas...\n")
    
    exito = analizar_funcion_sincronizacion()
    
    sugerir_proximos_pasos()
    
    if exito:
        print("\n✅ Diagnóstico completado. Las optimizaciones están implementadas.")
        print("💡 Si el problema persiste, es probable que sea un timeout de red específico.")
    else:
        print("\n❌ Diagnóstico encontró problemas. Revisar optimizaciones faltantes.")
    
    return exito

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
