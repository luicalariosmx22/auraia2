#!/usr/bin/env python3
"""
Script de diagnóstico para probar el arranque de la aplicación sin módulos problemáticos
"""

import sys
import os
from datetime import datetime

def test_app_startup():
    """Prueba el arranque de la aplicación Flask"""
    print("🚀 DIAGNÓSTICO DE ARRANQUE DE APLICACIÓN")
    print("=" * 50)
    print(f"Hora de inicio: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        print("📦 Intentando importar la aplicación...")
        from clientes.aura import create_app
        
        print("🏭 Creando instancia de la aplicación...")
        app = create_app()
        
        print("✅ APLICACIÓN CREADA EXITOSAMENTE")
        print(f"🎯 Aplicación: {app}")
        print(f"📊 Rutas registradas: {len(app.url_map._rules)}")
        
        # Listar algunas rutas para verificar que todo está bien
        print("\n📋 Algunas rutas registradas:")
        count = 0
        for rule in app.url_map.iter_rules():
            if count < 10:  # Solo mostrar las primeras 10
                print(f"  - {rule.rule} [{','.join(rule.methods)}]")
                count += 1
            else:
                break
        
        print(f"Hora de finalización: {datetime.now().strftime('%H:%M:%S')}")
        print("\n✅ DIAGNÓSTICO COMPLETADO - LA APLICACIÓN ARRANCA CORRECTAMENTE")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN EL ARRANQUE: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # Cambiar al directorio correcto
    os.chdir("/mnt/c/Users/PC/PYTHON/Auraai2")
    
    success = test_app_startup()
    
    if success:
        print("\n💡 SOLUCIÓN: El problema estaba en el módulo que se comentó")
        print("💡 Revisar las importaciones de reportes_meta_ads para optimizar")
    else:
        print("\n🔍 SIGUIENTE PASO: Revisar el error específico mostrado arriba")
        print("🔍 Puede ser necesario comentar más módulos para encontrar el problema")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
