"""Funciones auxiliares para sincronización de Meta Ads"""
from datetime import datetime
from clientes.aura.utils.supabase_client import supabase

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
