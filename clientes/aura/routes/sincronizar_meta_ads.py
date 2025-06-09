# ✅ Archivo: clientes/aura/routes/panel_cliente_meta_ads/sincronizar_meta_ads.py
# 👉 Consulta manual de gasto semanal por anuncio y actualización en Supabase

import requests
from datetime import datetime, timedelta
from clientes.aura.utils.supabase_client import supabase
import os
from flask import Blueprint, jsonify, request

panel_cliente_meta_ads_bp = Blueprint('panel_cliente_meta_ads', __name__)

def sincronizar_gasto_anuncios(empresa_id, ad_account_id, access_token):
    hoy = datetime.utcnow().date()
    inicio = hoy - timedelta(days=7)
    fin = hoy

    # --- NUEVO: Definir campos básicos y rankings ---
    fields = (
        "impressions,reach,frequency,spend,"
        "clicks,inline_link_clicks,unique_clicks,unique_inline_link_clicks,"
        "ctr,cpc,cost_per_unique_click,cost_per_unique_inline_link_click,"
        "quality_ranking,engagement_rate_ranking,conversion_rate_ranking"
    )
    url = f"https://graph.facebook.com/v19.0/act_{ad_account_id}/insights"
    params = {
        'access_token': access_token,
        'level': 'ad',
        'fields': fields,
        'time_range[since]': str(inicio),
        'time_range[until]': str(fin),
        'limit': 100
    }

    # Debug: mostrar la URL y los parámetros que se usarán para la petición
    print("[MetaAds][DEBUG] URL:", url)
    print("[MetaAds][DEBUG] Params:", params)

    # Debug extra: muestra cómo sería el request completo para Postman
    import urllib.parse
    query_string = urllib.parse.urlencode(params)
    print("[MetaAds][DEBUG][Postman] Request URL:")
    print(f"{url}?{query_string}")

    # 1. Llamada principal: básicos y rankings
    response = requests.get(url, params=params)
    data = response.json()
    if 'error' in data:
        print(f"❌ Error al consultar Meta API: {data['error']}")
        return
    # 2. Llamada para actions
    actions_fields = 'actions,video_play_actions,video_avg_time_watched_actions,post_engagement,post_reactions,post_comments,post_shares,thruplays,thruplay_rate,website_ctr,website_purchase_roas,purchase_roas'
    params_actions = params.copy()
    params_actions['fields'] = actions_fields
    response_actions = requests.get(url, params=params_actions)
    data_actions = response_actions.json()
    # 3. Llamada para mensajes
    messages_fields = 'messaging_conversations_started,cost_per_messaging_conversation_started'
    params_messages = params.copy()
    params_messages['fields'] = messages_fields
    response_messages = requests.get(url, params=params_messages)
    data_messages = response_messages.json()
    # Indexar por ad_id para unir resultados
    def index_by_ad_id(data):
        return {ad.get('ad_id'): ad for ad in data.get('data', [])}
    base_ads = index_by_ad_id(data)
    actions_ads = index_by_ad_id(data_actions)
    messages_ads = index_by_ad_id(data_messages)
    tablas_actualizadas = []
    for ad_id, ad in base_ads.items():
        nombre = ad.get('ad_name')
        gasto = float(ad.get('spend', 0))
        conjunto_id = ad.get('adset_id')
        campana_id = ad.get('campaign_id')
        # Unir datos de actions y mensajes
        ad_actions = actions_ads.get(ad_id, {})
        ad_messages = messages_ads.get(ad_id, {})
        # Campos básicos
        def safe_int(val):
            try:
                return int(float(val))
            except:
                return 0
        def safe_float(val):
            try:
                return float(val)
            except:
                return 0.0
        def safe_str(val):
            return str(val) if val is not None else None
        alcance = safe_int(ad.get('reach', 0))
        impresiones = safe_int(ad.get('impressions', 0))
        clicks = safe_int(ad.get('clicks', 0))
        link_clicks = safe_int(ad.get('link_clicks', 0))
        inline_link_clicks = safe_int(ad.get('inline_link_clicks', 0))
        interacciones = clicks + link_clicks + inline_link_clicks
        mensajes = safe_int(ad_messages.get('messaging_conversations_started', 0))
        # --- NUEVO: Extraer campos avanzados de actions ---
        advanced_fields = {}
        for field in ['actions','video_play_actions','video_avg_time_watched_actions','post_engagement','post_reactions','post_comments','post_shares','thruplays','thruplay_rate','website_ctr','website_purchase_roas','purchase_roas']:
            val = ad_actions.get(field, 0)
            # Si es numérico, decide si es int o float
            if isinstance(val, (int, float)):
                if isinstance(val, float) and val.is_integer():
                    advanced_fields[field] = safe_int(val)
                elif isinstance(val, int):
                    advanced_fields[field] = val
                else:
                    advanced_fields[field] = safe_float(val)
            elif isinstance(val, str):
                try:
                    fval = float(val)
                    if fval.is_integer():
                        advanced_fields[field] = safe_int(fval)
                    else:
                        advanced_fields[field] = safe_float(fval)
                except:
                    advanced_fields[field] = safe_str(val)
            else:
                advanced_fields[field] = safe_str(val)
        # Mensajes avanzados
        for field in ['messaging_conversations_started','cost_per_messaging_conversation_started']:
            val = ad_messages.get(field, 0)
            if isinstance(val, (int, float)):
                if isinstance(val, float) and val.is_integer():
                    advanced_fields[field] = safe_int(val)
                elif isinstance(val, int):
                    advanced_fields[field] = val
                else:
                    advanced_fields[field] = safe_float(val)
            elif isinstance(val, str):
                try:
                    fval = float(val)
                    if fval.is_integer():
                        advanced_fields[field] = safe_int(fval)
                    else:
                        advanced_fields[field] = safe_float(fval)
                except:
                    advanced_fields[field] = safe_str(val)
            else:
                advanced_fields[field] = safe_str(val)
        # Buscar si ya existe un anuncio con ese nombre y cuenta publicitaria
        query = supabase.table('meta_ads_anuncios_detalle').select('id').eq('nombre_anuncio', nombre).eq('id_cuenta_publicitaria', ad_account_id)
        existente = query.execute()
        fields_to_update = {
            'importe_gastado': gasto,
            'conjunto_id': conjunto_id,
            'campana_id': campana_id,
            'alcance': alcance,
            'impresiones': impresiones,
            'interacciones': interacciones,
            'clicks': clicks,
            'link_clicks': link_clicks,
            'inline_link_clicks': inline_link_clicks,
            'mensajes': mensajes,
            **advanced_fields
        }
        fields_to_insert = {
            'ad_id': ad_id,
            'nombre_anuncio': nombre,
            'importe_gastado': gasto,
            'id_cuenta_publicitaria': ad_account_id,
            'conjunto_id': conjunto_id,
            'campana_id': campana_id,
            'alcance': alcance,
            'impresiones': impresiones,
            'interacciones': interacciones,
            'clicks': clicks,
            'link_clicks': link_clicks,
            'inline_link_clicks': inline_link_clicks,
            'mensajes': mensajes,
            **advanced_fields
        }
        if existente.data:
            supabase.table('meta_ads_anuncios_detalle')\
                .update(fields_to_update)\
                .eq('id', existente.data[0]['id']).execute()
            print(f"🔄 Actualizado: {nombre} → ${gasto}")
            if 'meta_ads_anuncios_detalle' not in tablas_actualizadas:
                tablas_actualizadas.append('meta_ads_anuncios_detalle')
        else:
            supabase.table('meta_ads_anuncios_detalle').insert(fields_to_insert).execute()
            print(f"🆕 Insertado: {nombre} (ad_id {ad_id}) para cuenta {ad_account_id}")
            if 'meta_ads_anuncios_detalle' not in tablas_actualizadas:
                tablas_actualizadas.append('meta_ads_anuncios_detalle')
    # Mostrar resumen de tablas sincronizadas
    print("[MetaAds][DEBUG] Tablas sincronizadas en esta ejecución:", tablas_actualizadas)

@panel_cliente_meta_ads_bp.route('/panel_cliente/meta_ads/sincronizar', methods=['POST'])
def route_sincronizar_gasto_anuncios():
    try:
        # Obtener los parámetros del formulario
        empresa_id = request.form.get('empresa_id')
        ad_account_id = request.form.get('ad_account_id')
        access_token = request.form.get('access_token')

        sincronizar_gasto_anuncios(empresa_id, ad_account_id, access_token)
        return jsonify({'status': 'ok', 'message': 'Sincronización completada'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
