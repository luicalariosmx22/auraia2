from datetime import datetime, timedelta
from clientes.aura.utils.supabase_client import supabase

# 🗄️ CONTEXTO BD PARA GITHUB COPILOT
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas
# BD ACTUAL: meta_ads_cuentas(15), meta_ads_anuncios_detalle(96), meta_ads_reportes_semanales(35)

def sincronizar_gasto_anuncios(empresa_id, ad_account_id, access_token):
    """Función para sincronizar gastos de anuncios de Meta Ads"""
    try:
        # Aquí iría la lógica de sincronización
        # Por ahora solo registramos el intento
        supabase.table('meta_ads_sync_log').insert({
            'empresa_id': empresa_id,
            'ad_account_id': ad_account_id,
            'estado': 'completado',
            'created_at': datetime.now().isoformat()
        }).execute()
        
        return True
    except Exception as e:
        print(f"Error al sincronizar gastos: {e}")
        return False
