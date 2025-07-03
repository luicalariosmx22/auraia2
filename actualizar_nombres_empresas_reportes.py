#!/usr/bin/env python3
"""
Script para actualizar los nombres de empresa en reportes existentes.
Corrige el problema donde empresa_nombre muestra el nombre_cliente en lugar del nombre real de la empresa.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase import create_client, Client

# Configuración de Supabase
SUPABASE_URL = "https://pjsehdlxbegcqczapiud.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBqc2VoZGx4YmVnY3FjemFwaXVkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzMzMjAzNzQsImV4cCI6MjA0ODg5NjM3NH0.mawNLmFPWBd9vABGgEo8ub6RTxeQC3UjSnDkRqlQhog"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def actualizar_nombres_empresas():
    """
    Actualiza todos los reportes existentes para que tengan el nombre real de la empresa
    en lugar del nombre_cliente de la cuenta publicitaria.
    """
    print("🔄 Iniciando actualización de nombres de empresas en reportes...")
    
    # 1. Obtener todos los reportes
    try:
        reportes = supabase.table('meta_ads_reportes_semanales').select('*').execute().data or []
        print(f"📊 Reportes encontrados: {len(reportes)}")
    except Exception as e:
        print(f"❌ Error al obtener reportes: {e}")
        return
    
    if not reportes:
        print("ℹ️ No hay reportes para actualizar.")
        return
    
    # 2. Obtener mapeo de empresas
    try:
        empresas = supabase.table('cliente_empresas').select('id,nombre_empresa').execute().data or []
        empresas_map = {emp['id']: emp['nombre_empresa'] for emp in empresas}
        print(f"🏢 Empresas encontradas: {len(empresas)}")
    except Exception as e:
        print(f"❌ Error al obtener empresas: {e}")
        return
    
    # 3. Actualizar cada reporte
    actualizados = 0
    errores = 0
    
    for reporte in reportes:
        reporte_id = reporte.get('id')
        empresa_id = reporte.get('empresa_id')
        empresa_nombre_actual = reporte.get('empresa_nombre', '')
        
        if not empresa_id:
            print(f"⚠️ Reporte {reporte_id}: Sin empresa_id")
            continue
            
        nombre_empresa_real = empresas_map.get(empresa_id)
        if not nombre_empresa_real:
            print(f"⚠️ Reporte {reporte_id}: Empresa ID {empresa_id} no encontrada")
            continue
            
        # Solo actualizar si el nombre es diferente
        if empresa_nombre_actual != nombre_empresa_real:
            try:
                supabase.table('meta_ads_reportes_semanales').update({
                    'empresa_nombre': nombre_empresa_real
                }).eq('id', reporte_id).execute()
                
                print(f"✅ Reporte {reporte_id}: '{empresa_nombre_actual}' → '{nombre_empresa_real}'")
                actualizados += 1
            except Exception as e:
                print(f"❌ Error al actualizar reporte {reporte_id}: {e}")
                errores += 1
        else:
            print(f"✓ Reporte {reporte_id}: Ya tiene el nombre correcto")
    
    print(f"\n📈 Resumen:")
    print(f"   • Reportes actualizados: {actualizados}")
    print(f"   • Errores: {errores}")
    print(f"   • Total procesados: {len(reportes)}")
    
    if actualizados > 0:
        print("🎉 ¡Actualización completada! Los reportes ahora muestran los nombres reales de las empresas.")
    else:
        print("ℹ️ No se requirieron actualizaciones.")

if __name__ == "__main__":
    actualizar_nombres_empresas()
