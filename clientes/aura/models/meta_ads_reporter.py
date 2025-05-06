from clientes.aura.utils import supabase_client as supabase

class MetaAdsReporter:
    def __init__(self):
        self.supabase = supabase

    def report_ads(self, ad_data):
        response = self.supabase.insert(ad_data)
        return response