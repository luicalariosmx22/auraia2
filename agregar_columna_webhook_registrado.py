#!/usr/bin/env python3
"""
Script para agregar la columna webhook_registrado a la tabla meta_ads_cuentas
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def agregar_columna_webhook_registrado():
    """Agrega la columna webhook_registrado usando la API REST de Supabase"""
    
    # Configuración de Supabase
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Variables SUPABASE_URL o SUPABASE_KEY no configuradas")
        return False
    
    print("🔧 Agregando columna webhook_registrado a meta_ads_cuentas...")
    
    # SQL para agregar la columna
    sql_query = """
    ALTER TABLE meta_ads_cuentas 
    ADD COLUMN webhook_registrado BOOLEAN DEFAULT FALSE;
    """
    
    # Headers para la API de Supabase
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    # URL del RPC endpoint
    url = f"{SUPABASE_URL}/rest/v1/rpc/sql"
    
    # Datos para el RPC
    data = {
        'query': sql_query
    }
    
    try:
        print("📡 Ejecutando SQL...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response: {response.text}")
        
        if response.status_code in [200, 201, 204]:
            print("✅ Columna agregada exitosamente")
            return True
        else:
            print(f"❌ Error al agregar columna: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en la request: {e}")
        return False

def verificar_columna():
    """Verifica que la columna se haya agregado correctamente"""
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        print("🔍 Verificando que la columna existe...")
        
        # Intentar hacer un select con la nueva columna
        result = supabase.table('meta_ads_cuentas') \
            .select('id, webhook_registrado') \
            .limit(1) \
            .execute()
        
        if result.data:
            print("✅ Columna webhook_registrado existe y es accesible")
            print(f"📊 Ejemplo: {result.data[0]}")
            return True
        else:
            print("⚠️ No hay datos para verificar")
            return True  # Columna existe pero tabla vacía
            
    except Exception as e:
        print(f"❌ Error verificando columna: {e}")
        return False

def actualizar_valores_default():
    """Actualiza todos los registros existentes con webhook_registrado = false"""
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        print("🔄 Actualizando valores por defecto...")
        
        # Obtener total de registros
        total_result = supabase.table('meta_ads_cuentas') \
            .select('id', count='exact') \
            .execute()
        
        total_registros = total_result.count
        print(f"📊 Total de registros a actualizar: {total_registros}")
        
        if total_registros > 0:
            # Actualizar todos a false
            update_result = supabase.table('meta_ads_cuentas') \
                .update({'webhook_registrado': False}) \
                .neq('id', 0) \
                .execute()  # neq 0 para actualizar todos
            
            print(f"✅ {len(update_result.data)} registros actualizados")
            return True
        else:
            print("⚠️ No hay registros para actualizar")
            return True
            
    except Exception as e:
        print(f"❌ Error actualizando valores: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando proceso de agregar columna webhook_registrado...")
    
    # Paso 1: Agregar la columna
    if agregar_columna_webhook_registrado():
        print("\n" + "="*50)
        
        # Paso 2: Verificar que existe
        if verificar_columna():
            print("\n" + "="*50)
            
            # Paso 3: Actualizar valores por defecto
            if actualizar_valores_default():
                print("\n✅ Proceso completado exitosamente")
                print("🎯 Ahora puedes probar el endpoint /cuentas")
            else:
                print("\n⚠️ Columna creada pero error actualizando valores")
        else:
            print("\n❌ Columna no se pudo verificar")
    else:
        print("\n❌ No se pudo agregar la columna")
