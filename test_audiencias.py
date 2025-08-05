#!/usr/bin/env python3
"""
Prueba rápida de las funciones de audiencias Meta Ads
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_importaciones():
    """Prueba que las funciones se puedan importar correctamente"""
    try:
        from clientes.aura.routes.panel_cliente_meta_ads.campanas import (
            obtener_audiencias_con_filtros,
            obtener_detalle_audiencia,
            obtener_estadisticas_audiencias,
            sincronizar_audiencias_desde_meta
        )
        print("✅ Todas las funciones de audiencias se importaron correctamente")
        return True
    except ImportError as e:
        print(f"❌ Error importando funciones: {e}")
        return False

def test_funciones_basicas():
    """Prueba básica de las funciones (sin conectar a Meta API)"""
    try:
        from clientes.aura.routes.panel_cliente_meta_ads.campanas import (
            obtener_audiencias_con_filtros,
            obtener_estadisticas_audiencias
        )
        
        # Probar función con nombre de nora ficticio
        audiencias = obtener_audiencias_con_filtros("test_nora", {})
        print(f"✅ obtener_audiencias_con_filtros ejecutada. Resultado: {len(audiencias)} audiencias")
        
        # Probar estadísticas
        stats = obtener_estadisticas_audiencias("test_nora", {})
        print(f"✅ obtener_estadisticas_audiencias ejecutada. Total: {stats.get('total_audiencias', 0)}")
        
        return True
    except Exception as e:
        print(f"❌ Error en pruebas básicas: {e}")
        return False

if __name__ == "__main__":
    print("🧪 PRUEBAS DE AUDIENCIAS META ADS")
    print("=" * 50)
    
    success = True
    
    # Prueba 1: Importaciones
    print("\n1. Probando importaciones...")
    success &= test_importaciones()
    
    # Prueba 2: Funciones básicas
    print("\n2. Probando funciones básicas...")
    success &= test_funciones_basicas()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TODAS LAS PRUEBAS PASARON")
        print("\nLas funciones de audiencias están listas para usar.")
        print("Para acceder a la interfaz, visita:")
        print("http://localhost:5000/panel_cliente/{nombre_nora}/meta_ads/audiencias")
    else:
        print("💥 ALGUNAS PRUEBAS FALLARON")
        print("Revisar los errores arriba.")
