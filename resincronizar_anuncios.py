#!/usr/bin/env python3
"""
Script para re-sincronizar todos los anuncios con customer_id correcto
"""
import sys
sys.path.append('.')

from clientes.aura.utils.supabase_client import supabase
from clientes.aura.services.google_ads_service_fixed import GoogleAdsService

def limpiar_y_resincronizar():
    print("🧹 Limpiando anuncios existentes...")
    # Eliminar todos los anuncios actuales de aura
    result = supabase.table('google_ads_reporte_anuncios').delete().eq('nombre_nora', 'aura').execute()
    print(f"✅ Eliminados anuncios existentes")
    
    print("🔄 Iniciando re-sincronización con customer_id...")
    
    # Crear servicio
    service = GoogleAdsService()
    
    # Obtener cuentas del MCC
    cuentas_mcc = service.listar_cuentas_mcc()
    cuentas_accesibles = [c for c in cuentas_mcc if c.get('accesible', True)]
    
    print(f"📋 Encontradas {len(cuentas_accesibles)} cuentas accesibles")
    
    total_anuncios = 0
    
    for cuenta in cuentas_accesibles:
        customer_id = cuenta['customer_id']
        nombre_cuenta = cuenta['nombre_cliente']
        
        print(f"\n🔍 Procesando cuenta {customer_id} - {nombre_cuenta}...")
        
        try:
            # Obtener anuncios de esta cuenta
            anuncios = service.obtener_todos_los_anuncios(customer_id)
            
            if anuncios:
                print(f"✅ Obtenidos {len(anuncios)} anuncios para {customer_id}")
                
                # Asegurar que todos los anuncios tienen customer_id
                for anuncio in anuncios:
                    anuncio['customer_id'] = customer_id
                    anuncio['nombre_nora'] = 'aura'
                
                # Insertar en lotes
                batch_size = 10
                for i in range(0, len(anuncios), batch_size):
                    batch = anuncios[i:i+batch_size]
                    try:
                        result = supabase.table('google_ads_reporte_anuncios').insert(batch).execute()
                        print(f"  ✅ Insertado lote {i//batch_size + 1} ({len(batch)} anuncios)")
                    except Exception as e:
                        print(f"  ❌ Error insertando lote: {e}")
                        continue
                
                total_anuncios += len(anuncios)
            else:
                print(f"⚠️ No se encontraron anuncios para {customer_id}")
                
        except Exception as e:
            print(f"❌ Error procesando cuenta {customer_id}: {e}")
            continue
    
    print(f"\n🎉 Re-sincronización completada!")
    print(f"📊 Total de anuncios insertados: {total_anuncios}")
    
    # Verificar resultados
    print("\n📋 Verificando resultados...")
    
    result_verificacion = supabase.table('google_ads_reporte_anuncios').select('*').eq('nombre_nora', 'aura').execute()
    anuncios_verificacion = result_verificacion.data or []
    
    # Agrupar por customer_id
    cuentas_stats = {}
    for anuncio in anuncios_verificacion:
        customer_id = anuncio.get('customer_id', 'Sin customer_id')
        if customer_id not in cuentas_stats:
            cuentas_stats[customer_id] = 0
        cuentas_stats[customer_id] += 1
    
    print(f"📊 Total anuncios en DB: {len(anuncios_verificacion)}")
    for customer_id, total in cuentas_stats.items():
        print(f"  - {customer_id}: {total} anuncios")

if __name__ == "__main__":
    limpiar_y_resincronizar()
