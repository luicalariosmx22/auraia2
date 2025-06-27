import logging
from .supabase_client import supabase

class SupabaseGoogleAdsClient:
    def __init__(self):
        self.client = supabase
        logging.basicConfig(level=logging.DEBUG)

    def obtener_campanas(self, nombre_nora, empresa_id):
        """
        Obtiene las campañas de Google Ads para un cliente y empresa específicos
        """
        try:
            # Seleccionar solo las columnas que necesitamos
            response = self.client.table('google_ads_campanas') \
                .select('estado_campana,campana,presupuesto,tipo_campana,impresiones,ctr,costo,clics,conversiones,costo_conversion') \
                .eq('nombre_nora', nombre_nora) \
                .eq('empresa_id', empresa_id) \
                .execute()
            logging.debug(f"Respuesta de campañas: {response}")
            return response.data if response else []
        except Exception as e:
            print(f"Error al obtener campañas: {str(e)}")
            return []

    def obtener_anuncios(self, nombre_nora, empresa_id):
        """
        Obtiene los anuncios de Google Ads para un cliente y empresa específicos
        """
        try:
            # Seleccionar solo las columnas que necesitamos
            response = self.client.table('google_ads_reporte_anuncios') \
                .select('campana,grupo_anuncios,estado_anuncio,tipo_anuncio,titulo_1,descripcion_1,impresiones,clics,ctr,costo,conversiones') \
                .eq('nombre_nora', nombre_nora) \
                .eq('empresa_id', empresa_id) \
                .execute()
            logging.debug(f"Respuesta de anuncios: {response}")
            return response.data if response else []
        except Exception as e:
            print(f"Error al obtener anuncios: {str(e)}")
            return []

    def obtener_palabras_clave(self, nombre_nora, empresa_id):
        """
        Obtiene las palabras clave de Google Ads para un cliente y empresa específicos
        """
        try:
            # Seleccionar solo las columnas que necesitamos y filtramos los estados
            response = self.client.table('google_ads_palabras_clave') \
                .select('palabra_clave,tipo_concordancia,estado_palabra_clave,campana,impresiones,clics') \
                .eq('nombre_nora', nombre_nora) \
                .eq('empresa_id', empresa_id) \
                .not_('estado_palabra_clave', 'eq', 'Habilitado') \
                .not_('palabra_clave', 'eq', 'Habilitado') \
                .not_('palabra_clave', 'eq', 'Estado de palabras clave') \
                .order('impresiones', desc=True) \
                .execute()
            logging.debug(f"Respuesta de keywords: {response}")
            return [k for k in (response.data if response else []) 
                   if k.get('palabra_clave') and k.get('palabra_clave') != 'NULL']
        except Exception as e:
            print(f"Error al obtener palabras clave: {str(e)}")
            return []

    def calcular_estadisticas(self, nombre_nora, empresa_id):
        """
        Calcula estadísticas generales para el dashboard usando el nombre de Nora y la empresa seleccionada
        """
        try:
            campanas = self.obtener_campanas(nombre_nora, empresa_id)
            
            stats = {
                'total_campañas': len(campanas),
                'campañas_activas': len([c for c in campanas if c.get('estado_campana', '') == 'enabled']),
                'total_impresiones': sum(float(c.get('impresiones', 0)) for c in campanas),
                'total_clics': sum(float(c.get('clics', 0)) for c in campanas)
            }
            
            # Calcular CTR promedio
            if stats['total_impresiones'] > 0:
                stats['ctr_promedio'] = round((stats['total_clics'] / stats['total_impresiones']) * 100, 2)
            else:
                stats['ctr_promedio'] = 0
                
            return stats
            
        except Exception as e:
            print(f"Error al calcular estadísticas: {str(e)}")
            return {
                'total_campañas': 0,
                'campañas_activas': 0,
                'total_impresiones': 0,
                'total_clics': 0,
                'ctr_promedio': 0
            }
