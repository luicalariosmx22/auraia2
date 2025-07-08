# ✅ Mapeo maestro de columnas Nora → Meta API

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

# ✅ Las columnas válidas para seleccionar (solo claves internas Nora)
COLUMNAS_VALIDAS_META_ADS = set(MAPEO_COLUMNAS_META_ADS.keys())

# ✅ Breakdown único que usamos actualmente
BREAKDOWNS_VALIDOS = {"publisher_platform"}

# ✅ Limpieza centralizada de columnas (para validar input del frontend)
def limpiar_columnas_solicitadas(columnas_solicitadas):
    if not columnas_solicitadas:
        return list(COLUMNAS_VALIDAS_META_ADS)
    return [col for col in columnas_solicitadas if col in COLUMNAS_VALIDAS_META_ADS]

# ✅ Generador de fields que enviamos al API de Meta
def obtener_fields_para_meta(columnas_validas):
    return [MAPEO_COLUMNAS_META_ADS[col] for col in columnas_validas if col in MAPEO_COLUMNAS_META_ADS]

# ✅ Breakdowns siempre fijos
def obtener_breakdowns():
    return list(BREAKDOWNS_VALIDOS)
