#!/usr/bin/env python3
"""
Test para verificar qué funciones RPC de Supabase funcionan realmente
"""

import os
import sys
from dotenv import load_dotenv
sys.path.append('.')

load_dotenv('.env.local')

def test_supabase_rpc():
    """Prueba diferentes funciones RPC de Supabase"""
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        print("🔍 PROBANDO FUNCIONES RPC DE SUPABASE")
        print("=" * 50)
        
        # SQL simple de prueba
        test_sql = "SELECT 1 as test_value"
        
        # Probar diferentes funciones y parámetros
        test_cases = [
            ('exec_sql', {'sql': test_sql}),
            ('exec_sql', {'sql_query': test_sql}),
            ('exec_sql', {'query': test_sql}),
            ('execute_sql', {'sql': test_sql}),
            ('execute_sql', {'sql_query': test_sql}),
            ('execute_sql', {'query': test_sql}),
            ('run_sql', {'sql': test_sql}),
            ('run_sql', {'sql_query': test_sql}),
            ('run_sql', {'query': test_sql}),
        ]
        
        for func_name, params in test_cases:
            try:
                print(f"\n🧪 Probando: supabase.rpc('{func_name}', {params})")
                result = supabase.rpc(func_name, params).execute()
                print(f"   ✅ FUNCIONA - Resultado: {result.data}")
                
                # Si encontramos uno que funciona, usamos ese
                if result.data:
                    print(f"\n🎯 FUNCIÓN VÁLIDA ENCONTRADA:")
                    print(f"   Función: {func_name}")
                    print(f"   Parámetros: {params}")
                    return func_name, params
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n⚠️ Ninguna función RPC funcionó. Probando método directo...")
        
        # Si las RPC no funcionan, probar inserción directa
        try:
            # Solo probar que podemos leer tabla existente
            result = supabase.table('configuracion_bot').select('nombre_nora').limit(1).execute()
            print(f"✅ Supabase conectado. BD funciona. Resultado: {result.data}")
            
            print(f"\n💡 RECOMENDACIÓN: Usar tabla().insert() en lugar de RPC")
            return None, None
            
        except Exception as e:
            print(f"❌ Error básico de Supabase: {e}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error importando Supabase: {e}")
        return None, None

if __name__ == "__main__":
    test_supabase_rpc()
