# Archivo: clientes/aura/tasks/meta_ads_sync_all.py
# Sincroniza campañas, conjuntos y anuncios de una cuenta Meta Ads
from clientes.aura.routes.sincronizar_meta_ads import sincronizar_gasto_anuncios
from clientes.aura.utils.supabase_client import supabase
import requests

def sincronizar_todo_meta_ads(ad_account_id, access_token):
    # 1. Sincronizar campañas
    url_campanas = f"https://graph.facebook.com/v19.0/act_{ad_account_id}/campaigns"
    params = {
        'access_token': access_token,
        'fields': 'id,name',
        'limit': 100
    }
    resp = requests.get(url_campanas, params=params)
    data = resp.json()
    if 'data' in data:
        for camp in data['data']:
            supabase.table('meta_ads_campañas').upsert({
                'campana_id': camp['id'],
                'nombre_campana': camp['name'],
                'id_cuenta_publicitaria': ad_account_id
            }).execute()
    # 2. Sincronizar conjuntos de anuncios
    url_conjuntos = f"https://graph.facebook.com/v19.0/act_{ad_account_id}/adsets"
    params = {
        'access_token': access_token,
        'fields': 'id,name,campaign_id',  # ← Pedir campaign_id
        'limit': 100
    }
    resp = requests.get(url_conjuntos, params=params)
    data = resp.json()
    if 'data' in data:
        for conj in data['data']:
            supabase.table('meta_ads_conjuntos_anuncios').upsert({
                'conjunto_id': conj['id'],
                'nombre_conjunto': conj['name'],
                'id_cuenta_publicitaria': ad_account_id,
                'meta_ads_campaña_id': conj.get('campaign_id')  # ← Guardar relación campaña
            }).execute()
    # 3. Sincronizar anuncios y gasto
    sincronizar_gasto_anuncios(ad_account_id, ad_account_id, access_token)
