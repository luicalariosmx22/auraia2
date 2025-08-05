#!/usr/bin/env python3
"""
Script para verificar cuentas de Meta Ads
"""
import os
from dotenv import load_dotenv
from clientes.aura.utils.supabase_client import supabase

load_dotenv()

def verificar_cuentas():
    try:
        # Obtener todas las cuentas
        result = supabase.table('meta_ads_cuentas').select('*').execute()
        
        print(f"🔍 Cuentas encontradas: {len(result.data) if result.data else 0}")
        
        if result.data:
            for cuenta in result.data:
                nombre = cuenta.get('nombre_cliente', 'Sin nombre')
                estado = cuenta.get('estado_actual', 'Sin estado')
                id_cuenta = cuenta.get('id_cuenta_publicitaria', 'Sin ID')
                print(f"  📋 {nombre} (ID: {id_cuenta}) - Estado: {estado}")
        else:
            print("❌ No hay cuentas de Meta Ads configuradas")
            print("💡 Necesitas agregar cuentas primero para que el webhook funcione")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verificar_cuentas()
