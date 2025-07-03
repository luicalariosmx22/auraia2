#!/usr/bin/env python3
"""
Script de prueba para verificar las optimizaciones en la sincronización de Meta Ads.
Este script simula una sincronización pequeña para validar que no hay cuelgues.
"""

import sys
import os
from datetime import datetime, timedelta

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sincronizacion_meta_ads():
    """
    Prueba la sincronización de Meta Ads con un rango pequeño de fechas.
    """
    try:
        # Importar la función de sincronización
        from clientes.aura.routes.reportes_meta_ads.estadisticas import sincronizar_anuncios_meta_ads
        
        print("="*60)
        print("PRUEBA DE SINCRONIZACIÓN META ADS OPTIMIZADA")
        print("="*60)
        
        # Configurar fechas de prueba (últimos 3 días para que sea rápido)
        fecha_fin = datetime.utcnow().date()
        fecha_inicio = fecha_fin - timedelta(days=2)
        
        print(f"Fechas de prueba: {fecha_inicio} a {fecha_fin}")
        print(f"Iniciando sincronización a las: {datetime.now().strftime('%H:%M:%S')}")
        
        # Ejecutar sincronización
        inicio_tiempo = datetime.now()
        resultado = sincronizar_anuncios_meta_ads(fecha_inicio, fecha_fin)
        fin_tiempo = datetime.now()
        
        duracion = fin_tiempo - inicio_tiempo
        
        print(f"Sincronización completada a las: {fin_tiempo.strftime('%H:%M:%S')}")
        print(f"Duración total: {duracion.total_seconds():.2f} segundos")
        
        if resultado:
            print(f"Anuncios procesados: {resultado.get('procesados', 0)}")
            print(f"Cuentas sin anuncios: {len(resultado.get('sin_anuncios', []))}")
            
            if resultado.get('sin_anuncios'):
                print("Cuentas sin anuncios:")
                for cuenta in resultado['sin_anuncios']:
                    print(f"  - {cuenta.get('nombre_cliente')} (ID: {cuenta.get('id_cuenta_publicitaria')})")
        else:
            print("ERROR: La sincronización retornó None o falló")
            return False
        
        print("\n✅ PRUEBA COMPLETADA EXITOSAMENTE")
        print(f"✅ No se detectaron cuelgues ni timeouts")
        print(f"✅ Tiempo de ejecución: {duracion.total_seconds():.2f}s")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN LA PRUEBA: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_configuracion():
    """
    Verifica que las variables de entorno estén configuradas correctamente.
    """
    print("Verificando configuración...")
    
    # Verificar META_ACCESS_TOKEN
    if not os.environ.get('META_ACCESS_TOKEN'):
        print("❌ ERROR: META_ACCESS_TOKEN no configurado")
        return False
    else:
        token = os.environ.get('META_ACCESS_TOKEN')
        print(f"✅ META_ACCESS_TOKEN configurado (primeros 10 chars: {token[:10]}...)")
    
    # Verificar conexión a Supabase
    try:
        from clientes.aura.utils.supabase_client import supabase
        result = supabase.table('meta_ads_cuentas').select('count', count='exact').limit(1).execute()
        print(f"✅ Conexión a Supabase OK (cuentas encontradas: {result.count})")
    except Exception as e:
        print(f"❌ ERROR en conexión a Supabase: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("SCRIPT DE PRUEBA - SINCRONIZACIÓN META ADS OPTIMIZADA")
    print("Este script verificará que las optimizaciones funcionen correctamente")
    print("-" * 60)
    
    # Verificar configuración
    if not verificar_configuracion():
        print("❌ Configuración incorrecta, abortando prueba")
        sys.exit(1)
    
    # Ejecutar prueba
    exito = test_sincronizacion_meta_ads()
    
    if exito:
        print("\n🎉 TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("El sistema de sincronización optimizado está funcionando correctamente")
        sys.exit(0)
    else:
        print("\n💥 FALLÓ LA PRUEBA")
        print("Revisar los logs para identificar problemas")
        sys.exit(1)
