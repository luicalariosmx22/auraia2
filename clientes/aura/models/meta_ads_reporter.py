from clientes.aura.utils.supabase_client import supabase

# 🗄️ CONTEXTO BD PARA GITHUB COPILOT
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas
# BD ACTUAL: meta_ads_anuncios_detalle(96), meta_ads_reportes_semanales(35), meta_ads_cuentas(15)

class MetaAdsReporter:
    def __init__(self):
        self.supabase = supabase

    def report_ads(self, ad_data):
        response = self.supabase.insert(ad_data)
        return response