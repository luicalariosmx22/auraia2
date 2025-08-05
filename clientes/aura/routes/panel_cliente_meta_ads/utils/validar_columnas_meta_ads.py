# 🗄️ CONTEXTO BD PARA GITHUB COPILOT
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas
# BD ACTUAL: meta_ads_anuncios_detalle(96), meta_ads_cuentas(15), meta_ads_reportes_semanales(35)

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
