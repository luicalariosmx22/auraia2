#!/usr/bin/env python3
"""
Script para verificar y poblar la tabla meta_ads_cuentas
"""

import sys
import os
sys.path.append('.')

try:
    from clientes.aura.utils.supabase_client import supabase
    
    print("=== VERIFICANDO TABLA META_ADS_CUENTAS ===")
    
    # Verificar si la tabla existe y tiene datos
    result = supabase.table('meta_ads_cuentas').select('*').execute()
    
    print(f"Cuentas encontradas: {len(result.data)}")
    
    if result.data:
        print("\nCuentas existentes:")
        for cuenta in result.data:
            print(f"- ID: {cuenta.get('id_cuenta_publicitaria')}")
            print(f"  Cliente: {cuenta.get('nombre_cliente')}")
            print(f"  Plataforma: {cuenta.get('tipo_plataforma')}")
            print(f"  Visible: {cuenta.get('nombre_visible')}")
            print()
    else:
        print("\n❌ No se encontraron cuentas en la tabla")
        print("Vamos a agregar algunas cuentas de prueba...")
        
        # Agregar cuentas de prueba
        cuentas_prueba = [
            {
                'id_cuenta_publicitaria': 'act_123456789',
                'nombre_cliente': 'Empresa Demo 1',
                'tipo_plataforma': 'facebook',
                'nombre_visible': 'aura',
                'account_status': 'active',
                'fecha_creacion': '2024-01-01'
            },
            {
                'id_cuenta_publicitaria': 'act_987654321',
                'nombre_cliente': 'Empresa Demo 2', 
                'tipo_plataforma': 'instagram',
                'nombre_visible': 'aura',
                'account_status': 'active',
                'fecha_creacion': '2024-01-01'
            },
            {
                'id_cuenta_publicitaria': 'act_555666777',
                'nombre_cliente': 'Empresa Demo 3',
                'tipo_plataforma': 'facebook',
                'nombre_visible': 'aura',
                'account_status': 'active', 
                'fecha_creacion': '2024-01-01'
            }
        ]
        
        for cuenta in cuentas_prueba:
            try:
                insert_result = supabase.table('meta_ads_cuentas').insert(cuenta).execute()
                print(f"✅ Cuenta agregada: {cuenta['nombre_cliente']}")
            except Exception as e:
                print(f"❌ Error agregando {cuenta['nombre_cliente']}: {e}")
        
        print("\n✅ Cuentas de prueba agregadas exitosamente")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
