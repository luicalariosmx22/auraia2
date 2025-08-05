#!/usr/bin/env python3
"""
Script de prueba para depurar la sincronización de audiencias
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

def probar_conexion_meta():
    """Prueba la conexión a Meta API"""
    try:
        import requests
        
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            print("❌ No se encontró META_ACCESS_TOKEN")
            return False
            
        print(f"✅ Token encontrado: {access_token[:20]}...")
        
        # Probar con una cuenta simple
        url = "https://graph.facebook.com/v19.0/me"
        params = {'access_token': access_token}
        
        response = requests.get(url, params=params, timeout=10)
        print(f"📡 Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conexión exitosa: {data}")
            return True
        else:
            print(f"❌ Error en respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Error probando conexión: {e}")
        return False

def obtener_cuentas_publicitarias():
    """Obtiene las cuentas publicitarias disponibles"""
    try:
        import requests
        
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            return []
            
        url = "https://graph.facebook.com/v19.0/me/adaccounts"
        params = {
            'access_token': access_token,
            'fields': 'id,name,account_status',
            'limit': 100
        }
        
        response = requests.get(url, params=params, timeout=10)
        print(f"📡 Consultando cuentas publicitarias - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            cuentas = data.get('data', [])
            print(f"🏢 Cuentas encontradas: {len(cuentas)}")
            
            for cuenta in cuentas:
                print(f"   - {cuenta['id']}: {cuenta.get('name', 'Sin nombre')} ({cuenta.get('account_status', 'Sin estado')})")
                
            return cuentas
        else:
            print(f"❌ Error obteniendo cuentas: {response.text}")
            return []
            
    except Exception as e:
        print(f"💥 Error obteniendo cuentas: {e}")
        return []

def probar_audiencias_cuenta(cuenta_id):
    """Prueba obtener audiencias de una cuenta específica"""
    try:
        import requests
        
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            return []
            
        # Limpiar el prefijo 'act_' si existe
        if cuenta_id.startswith('act_'):
            cuenta_id = cuenta_id[4:]
            
        url = f"https://graph.facebook.com/v19.0/act_{cuenta_id}/customaudiences"
        params = {
            'access_token': access_token,
            'fields': 'id,name,description,subtype,approximate_count,delivery_status,operation_status,data_source,time_created',
            'limit': 100
        }
        
        print(f"\n🔍 Probando audiencias para cuenta: {cuenta_id}")
        print(f"🌐 URL: {url}")
        
        response = requests.get(url, params=params, timeout=30)
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            audiencias = data.get('data', [])
            print(f"👥 Audiencias encontradas: {len(audiencias)}")
            
            for audiencia in audiencias:
                print(f"   - {audiencia.get('id')}: {audiencia.get('name', 'Sin nombre')}")
                print(f"     Tipo: {audiencia.get('subtype', 'N/A')}")
                print(f"     Estado: {audiencia.get('delivery_status', 'N/A')}")
                print(f"     Tamaño: {audiencia.get('approximate_count', 0)}")
                
            return audiencias
        else:
            print(f"❌ Error: {response.text}")
            return []
            
    except Exception as e:
        print(f"💥 Error probando audiencias: {e}")
        return []

def verificar_supabase():
    """Verifica la conexión a Supabase"""
    try:
        from clientes.aura.utils.supabase_client import supabase
        
        # Probar consulta simple
        resultado = supabase.table("meta_ads_cuentas").select("*").limit(5).execute()
        print(f"✅ Supabase conectado. Cuentas en BD: {len(resultado.data)}")
        
        for cuenta in resultado.data:
            print(f"   - {cuenta.get('id_cuenta_publicitaria')}: {cuenta.get('nombre_cliente')}")
            
        return True
    except Exception as e:
        print(f"❌ Error con Supabase: {e}")
        return False

if __name__ == "__main__":
    print("🧪 DEPURACIÓN DE SINCRONIZACIÓN DE AUDIENCIAS")
    print("=" * 60)
    
    # 1. Verificar variables de entorno
    print("\n1. Verificando variables de entorno...")
    meta_token = os.getenv('META_ACCESS_TOKEN')
    if meta_token:
        print(f"✅ META_ACCESS_TOKEN: {meta_token[:20]}...")
    else:
        print("❌ META_ACCESS_TOKEN no encontrado")
    
    # 2. Probar conexión Meta
    print("\n2. Probando conexión a Meta API...")
    probar_conexion_meta()
    
    # 3. Verificar Supabase
    print("\n3. Verificando Supabase...")
    verificar_supabase()
    
    # 4. Obtener cuentas publicitarias
    print("\n4. Obteniendo cuentas publicitarias...")
    cuentas = obtener_cuentas_publicitarias()
    
    # 5. Probar audiencias en cada cuenta
    if cuentas:
        print("\n5. Probando audiencias en cada cuenta...")
        for cuenta in cuentas[:3]:  # Solo las primeras 3 para no saturar
            probar_audiencias_cuenta(cuenta['id'])
    
    print("\n" + "=" * 60)
    print("🏁 Depuración completada")
