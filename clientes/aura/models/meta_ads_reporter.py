from clientes.aura.utils.supabase_client import supabase

class MetaAdsReporter:
    def __init__(self):
        self.supabase = supabase

    def report_ads(self, ad_data):
        response = self.supabase.insert(ad_data)
        return response