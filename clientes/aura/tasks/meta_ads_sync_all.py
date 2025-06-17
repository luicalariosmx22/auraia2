# Archivo: clientes/aura/tasks/meta_ads_sync_all.py
# Sincroniza campañas, conjuntos y anuncios de una cuenta Meta Ads
from clientes.aura.routes.sincronizar_meta_ads import sincronizar_gasto_anuncios
from clientes.aura.utils.supabase_client import supabase
import requests
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.api import FacebookAdsApi

# Agregamos nuestro validador de columnas
from clientes.aura.routes.reportes_meta_ads.utils.validar_columnas_meta_ads import limpiar_columnas_solicitadas, obtener_breakdowns


def sincronizar_todo_meta_ads(ad_account_id, access_token, fecha_inicio, fecha_fin, campos_validos=None, breakdowns=None):
    FacebookAdsApi.init(access_token=access_token)
    cuenta = AdAccount(f'act_{ad_account_id}')

    # Si no nos mandaron columnas desde el backend, usamos todas las válidas por default
    if campos_validos is None:
        campos_validos = limpiar_columnas_solicitadas(None)

    if breakdowns is None:
        breakdowns = obtener_breakdowns()

    params = {
        'time_range': {
            'since': fecha_inicio.strftime('%Y-%m-%d'),
            'until': fecha_fin.strftime('%Y-%m-%d')
        },
        'level': 'ad',
        'fields': campos_validos,
        'breakdowns': breakdowns,
        'limit': 100
    }

    insights = cuenta.get_insights(params=params)
    for insight in insights:
        print(insight)
        # Aquí procesas normalmente e insertas a Supabase como ya lo tienes armado
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
