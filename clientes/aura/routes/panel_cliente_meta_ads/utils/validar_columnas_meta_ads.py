COLUMNAS_VALIDAS_META_ADS = {
    "ad_id", "ad_name", "spend", "adset_id", "campaign_id",
    "reach", "impressions", "clicks", "ctr", "cpc", "unique_clicks",
    "quality_ranking", "engagement_rate_ranking", "conversion_rate_ranking",
    "date_start", "date_stop", "campaign_name", "adset_name"
}

BREAKDOWNS_VALIDOS = {"publisher_platform"}

def limpiar_columnas_solicitadas(columnas_solicitadas):
    if not columnas_solicitadas:
        return list(COLUMNAS_VALIDAS_META_ADS)
    columnas_limpias = []
    for col in columnas_solicitadas:
        if col in COLUMNAS_VALIDAS_META_ADS:
            columnas_limpias.append(col)
    return columnas_limpias

def obtener_breakdowns():
    return list(BREAKDOWNS_VALIDOS)
