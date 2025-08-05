#!/usr/bin/env python3
"""
Script para probar la sincronización real de audiencias con las funciones corregidas
"""

import sys
import os
from dotenv import load_dotenv

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar variables de entorno
load_dotenv()

# Importar la función real
try:
    from clientes.aura.routes.panel_cliente_meta_ads.campanas import (
        sincronizar_audiencias_desde_meta,
        sincronizar_saved_audiences_desde_meta
    )
    print("✅ Funciones importadas correctamente")
except Exception as e:
    print(f"❌ Error importando funciones: {e}")
    sys.exit(1)

def test_sincronizacion():
    """Probar ambas funciones de sincronización"""
    
    print("🧪 PRUEBA DE SINCRONIZACIÓN DE AUDIENCIAS")
    print("=" * 60)
    
    nombre_nora = "aura"  # Cambiar por el nombre correcto si es diferente
    
    # Test 1: Sincronizar audiencias personalizadas
    print(f"\n1️⃣ Probando sincronización de audiencias personalizadas...")
    try:
        resultado = sincronizar_audiencias_desde_meta(nombre_nora, "26907830")  # Una cuenta específica
        print(f"📊 Resultado: {resultado}")
        
        if resultado.get('ok'):
            print(f"✅ Éxito: {resultado.get('audiencias_sincronizadas', 0)} audiencias sincronizadas")
            if resultado.get('errores'):
                print(f"⚠️ Errores: {resultado['errores']}")
        else:
            print(f"❌ Error: {resultado.get('error', 'Error desconocido')}")
            
    except Exception as e:
        print(f"💥 Excepción en audiencias personalizadas: {e}")
    
    # Test 2: Sincronizar audiencias guardadas
    print(f"\n2️⃣ Probando sincronización de audiencias guardadas...")
    try:
        resultado = sincronizar_saved_audiences_desde_meta(nombre_nora, "26907830")  # Una cuenta específica
        print(f"📊 Resultado: {resultado}")
        
        if resultado.get('ok'):
            print(f"✅ Éxito: {resultado.get('audiencias_sincronizadas', 0)} audiencias guardadas sincronizadas")
            if resultado.get('errores'):
                print(f"⚠️ Errores: {resultado['errores']}")
        else:
            print(f"❌ Error: {resultado.get('error', 'Error desconocido')}")
            
    except Exception as e:
        print(f"💥 Excepción en audiencias guardadas: {e}")

if __name__ == "__main__":
    test_sincronizacion()
