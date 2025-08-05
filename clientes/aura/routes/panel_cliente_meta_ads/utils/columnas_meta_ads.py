# 🗄️ CONTEXTO BD PARA GITHUB COPILOT
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas
# BD ACTUAL: meta_ads_anuncios_detalle(96), meta_ads_reportes_semanales(35), meta_ads_cuentas(15)

# Mapeo de nombres de columnas a campos de la API de Meta
MAPEO_COLUMNAS_META_ADS = {
    'importe_gastado': 'spend',
    'impresiones': 'impressions',
    'alcance': 'reach',
    'clicks': 'clicks',
    'link_clicks': 'inline_link_clicks',
    'unique_clicks': 'unique_clicks',
    'ctr': 'ctr',
    'cpc': 'cpc',
    'unique_ctr': 'unique_ctr',
    'post_reactions': 'post_reactions',
    'comments': 'comments',
    'shares': 'shares',
    'video_plays': 'video_plays'
}

def limpiar_columnas_solicitadas(columnas):
    """Limpia y valida las columnas solicitadas contra el mapeo."""
    if not columnas:
        return list(MAPEO_COLUMNAS_META_ADS.keys())
    return [col for col in columnas if col in MAPEO_COLUMNAS_META_ADS]

def obtener_fields_para_meta(columnas):
    """Convierte nombres de columnas locales a campos de la API de Meta."""
    fields = []
    for col in columnas:
        if col in MAPEO_COLUMNAS_META_ADS:
            fields.append(MAPEO_COLUMNAS_META_ADS[col])
    # Campos obligatorios para identificación
    fields.extend(['ad_id', 'adset_id', 'campaign_id'])
    return list(set(fields))  # Eliminar duplicados

def obtener_breakdowns():
    """Retorna la lista de breakdowns necesarios."""
    return ['publisher_platform']
