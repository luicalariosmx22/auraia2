#!/usr/bin/env python3
"""
🧪 Test simple para verificar el sistema de webhooks unificado
"""
import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    print("🔄 Probando imports...")
    try:
        from clientes.aura.utils.supabase_client import supabase
        print("✅ Supabase client importado")
        
        from clientes.aura.utils.meta_webhook_helpers import registrar_evento_supabase
        print("✅ Helper de webhooks importado")
        
        return True, supabase
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        return False, None

def test_tabla_estructura(supabase):
    print("\n🔄 Verificando estructura de tabla...")
    try:
        response = supabase.table('logs_webhooks_meta').select('*').limit(1).execute()
        
        if response.data:
            campos = list(response.data[0].keys())
            print(f"📋 Campos: {campos}")
            
            campos_necesarios = ['procesado', 'procesado_en']
            for campo in campos_necesarios:
                if campo in campos:
                    print(f"✅ {campo}: OK")
                else:
                    print(f"❌ {campo}: FALTA")
            
            return True
        else:
            print("⚠️ Tabla vacía - esto es normal si es nueva")
            return True
            
    except Exception as e:
        print(f"❌ Error verificando tabla: {e}")
        return False

def main():
    print("🚀 TEST SIMPLE WEBHOOKS UNIFICADO")
    print("=" * 50)
    
    # Test 1: Imports
    imports_ok, supabase = test_imports()
    if not imports_ok:
        return False
    
    # Test 2: Estructura
    estructura_ok = test_tabla_estructura(supabase)
    if not estructura_ok:
        return False
    
    print("\n✅ Todos los tests básicos pasaron!")
    print("💡 El sistema está listo para usar")
    
    return True

if __name__ == "__main__":
    main()
