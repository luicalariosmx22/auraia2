# Script para poblar la tabla google_ads_cuentas con datos de ejemplo
# Ejecutar: python poblar_google_ads_cuentas.py

from clientes.aura.utils.supabase_client import supabase
from clientes.aura.services.google_ads_service import GoogleAdsService

def poblar_cuentas_google_ads():
    """
    Pobla la tabla google_ads_cuentas con cuentas reales del MCC
    """
    print("🚀 Iniciando poblado de cuentas de Google Ads...")
    
    try:
        # Crear instancia del servicio
        service = GoogleAdsService()
        
        # Obtener todas las cuentas del MCC
        print("📊 Obteniendo cuentas del MCC...")
        cuentas_mcc = service.listar_cuentas_mcc()
        print(f"✅ Se encontraron {len(cuentas_mcc)} cuentas")
        
        # Verificar cuentas existentes
        existentes = supabase.table('google_ads_cuentas').select('customer_id').execute().data or []
        existentes_ids = {c['customer_id'] for c in existentes}
        print(f"📋 Cuentas ya existentes en BD: {len(existentes_ids)}")
        
        # Preparar datos para insertar
        nuevas_cuentas = []
        for cuenta in cuentas_mcc:
            customer_id = cuenta['customer_id']
            
            if customer_id in existentes_ids:
                print(f"⏩ Saltando cuenta existente: {customer_id}")
                continue
            
            cuenta_data = {
                'customer_id': customer_id,
                'nombre_cliente': cuenta['nombre_cliente'],
                'nombre_visible': 'aura',  # Nora por defecto
                'empresa_id': None,  # Se vinculará después manualmente
                'conectada': True,
                'account_status': 1 if cuenta['activa'] else 0,
                'accesible': cuenta['accesible'],
                'problema': cuenta.get('problema'),
                'ads_activos': cuenta['ads_activos'],
                'anuncios_activos': cuenta['ads_activos'],
                'moneda': cuenta.get('moneda', 'MXN'),
                'zona_horaria': cuenta.get('zona_horaria', 'America/Mexico_City'),
                'es_test': False
            }
            
            nuevas_cuentas.append(cuenta_data)
            print(f"✅ Preparando: {customer_id} - {cuenta['nombre_cliente']}")
        
        # Insertar cuentas nuevas
        if nuevas_cuentas:
            print(f"💾 Insertando {len(nuevas_cuentas)} cuentas nuevas...")
            result = supabase.table('google_ads_cuentas').insert(nuevas_cuentas).execute()
            print(f"✅ {len(result.data)} cuentas insertadas correctamente")
            
            # Mostrar resumen
            print("\n📊 RESUMEN DE CUENTAS INSERTADAS:")
            for cuenta in result.data:
                status = "🟢 Activa" if cuenta['account_status'] == 1 and cuenta['accesible'] else "❌ Inactiva/Inaccesible"
                print(f"  - {cuenta['customer_id']}: {cuenta['nombre_cliente']} ({status})")
        else:
            print("ℹ️ No hay cuentas nuevas para insertar")
        
        print("\n🎉 Proceso completado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante el proceso: {e}")
        raise

if __name__ == "__main__":
    poblar_cuentas_google_ads()
