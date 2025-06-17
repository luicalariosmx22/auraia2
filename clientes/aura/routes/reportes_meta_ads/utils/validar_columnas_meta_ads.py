MAPEO_COLUMNAS_META_ADS = {
    'ad_id': 'ad_id',
    'nombre_anuncio': 'ad_name',
    'conjunto_id': 'adset_id',
    'campana_id': 'campaign_id',
    'importe_gastado': 'spend',
    'impresiones': 'impressions',
    'alcance': 'reach',
    'clicks': 'clicks',
    'unique_clicks': 'unique_clicks',
    'ctr': 'ctr',
    'cpc': 'cpc',
    'unique_ctr': 'unique_ctr',
    'quality_ranking': 'quality_ranking',
    'engagement_rate_ranking': 'engagement_rate_ranking',
    'conversion_rate_ranking': 'conversion_rate_ranking'
}

COLUMNAS_VALIDAS_META_ADS = set(MAPEO_COLUMNAS_META_ADS.keys())

BREAKDOWNS_VALIDOS = {"publisher_platform"}

def limpiar_columnas_solicitadas(columnas_solicitadas):
    if not columnas_solicitadas:
        return list(COLUMNAS_VALIDAS_META_ADS)
    return [col for col in columnas_solicitadas if col in COLUMNAS_VALIDAS_META_ADS]

def obtener_breakdowns():
    return list(BREAKDOWNS_VALIDOS)

def obtener_fields_para_meta(columnas_validas):
    return [MAPEO_COLUMNAS_META_ADS[col] for col in columnas_validas if col in MAPEO_COLUMNAS_META_ADS]
