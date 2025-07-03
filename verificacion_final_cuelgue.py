#!/usr/bin/env python3
"""
Script final de verificación para el problema de cuelgue en el arranque
"""

def check_optimization_status():
    """Verifica el estado de las optimizaciones implementadas"""
    
    print("🔍 VERIFICACIÓN DE OPTIMIZACIONES PARA CUELGUE DE ARRANQUE")
    print("=" * 60)
    
    # Verificar la optimización del módulo reportes_meta_ads
    try:
        with open('clientes/aura/routes/reportes_meta_ads/__init__.py', 'r') as f:
            content = f.read()
            
        optimizations = {
            'lazy_import_routes': 'def lazy_import_routes' in content,
            'get_estadisticas_bp': 'def get_estadisticas_bp' in content,
            'lazy_loading': 'lazy_estadisticas_bp' in content,
        }
        
        # Verificar que la importación solo esté dentro de get_estadisticas_bp
        import_lines = [line.strip() for line in content.split('\n') if 'from .estadisticas import estadisticas_ads_bp' in line]
        direct_import = any('def get_estadisticas_bp' not in content[:content.find(line)] for line in import_lines if line)
        optimizations['no_direct_estadisticas_import'] = not direct_import
        
        print("📊 Estado de optimizaciones en reportes_meta_ads:")
        for opt, status in optimizations.items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {opt.replace('_', ' ').title()}: {'Implementado' if status else 'Faltante'}")
            
    except Exception as e:
        print(f"❌ Error verificando optimizaciones: {e}")
        return False
    
    # Verificar logging adicional en __init__.py
    try:
        with open('clientes/aura/__init__.py', 'r') as f:
            content = f.read()
            
        logging_checks = {
            'importacion_logging': 'importado correctamente' in content,
            'registro_logging': 'registrado correctamente' in content,
            'cron_async': 'threading.Thread' in content,
            'step_by_step_logging': content.count('print(') > 10
        }
        
        print("\n📋 Estado de logging de diagnóstico:")
        for check, status in logging_checks.items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {check.replace('_', ' ').title()}: {'Presente' if status else 'Faltante'}")
            
    except Exception as e:
        print(f"❌ Error verificando logging: {e}")
        return False
    
    return all(optimizations.values()) and all(logging_checks.values())

def provide_recommendations():
    """Proporciona recomendaciones para el siguiente paso"""
    
    print("\n🛠️  RECOMENDACIONES PARA RESOLVER EL CUELGUE:")
    print("=" * 50)
    print("1. 🚀 Probar arranque con las optimizaciones implementadas")
    print("2. 📊 Monitorear los logs detallados para identificar el punto exacto")
    print("3. 🔧 Si persiste, el problema puede estar en:")
    print("   - Importaciones circulares en otros módulos")
    print("   - Conexiones a base de datos al inicializar")
    print("   - Dependencias pesadas en otros blueprints")
    print("4. 🎯 Usar la carga lazy para otros módulos problemáticos")
    print("5. ⚡ Considerar mover inicializaciones pesadas a after_first_request")

def main():
    print("🚀 VERIFICACIÓN FINAL DE OPTIMIZACIONES ANTI-CUELGUE")
    print(f"Timestamp: {__import__('datetime').datetime.now()}")
    print("-" * 60)
    
    success = check_optimization_status()
    
    provide_recommendations()
    
    if success:
        print("\n✅ OPTIMIZACIONES IMPLEMENTADAS CORRECTAMENTE")
        print("💡 La aplicación debería arrancar más rápido sin colgarse")
        print("🔄 Tiempo para probar el arranque real!")
    else:
        print("\n⚠️  ALGUNAS OPTIMIZACIONES FALTAN")
        print("🔧 Revisar las optimizaciones marcadas como faltantes")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
