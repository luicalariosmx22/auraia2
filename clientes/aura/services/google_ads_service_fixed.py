# -*- coding: utf-8 -*-
"""
Servicio integrado de Google Ads para el panel de administración
Versión corregida con soporte para todas las cuentas del MCC
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleAdsService:
    """
    Servicio para interactuar con la API de Google Ads
    Incluye soporte para todas las cuentas del MCC, incluso las que tienen problemas
    """
    
    def __init__(self):
        self.client = None
        self._setup_client()
    
    def _setup_client(self):
        """Configura el cliente de Google Ads con las credenciales del entorno"""
        try:
            # Cargar variables de entorno
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env.local')
            load_dotenv(env_path)
            
            # Obtener y validar customer ID
            raw_customer_id = os.getenv("GOOGLE_LOGIN_CUSTOMER_ID", "")
            # Limpiar: remover comentarios, espacios y guiones
            login_customer_id = raw_customer_id.split('#')[0].strip().replace("-", "").replace(" ", "")
            
            # Validar que tenga exactamente 10 dígitos
            if not login_customer_id.isdigit() or len(login_customer_id) != 10:
                raise ValueError(f"GOOGLE_LOGIN_CUSTOMER_ID debe tener exactamente 10 dígitos. Valor actual: '{raw_customer_id}' -> '{login_customer_id}'")
            
            config = {
                "developer_token": os.getenv("GOOGLE_DEVELOPER_TOKEN"),
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "refresh_token": os.getenv("GOOGLE_REFRESH_TOKEN"),
                "login_customer_id": login_customer_id,
                "use_proto_plus": True
            }
            
            # Validar que todas las credenciales estén presentes
            missing_credentials = [k for k, v in config.items() if not v and k != "use_proto_plus"]
            if missing_credentials:
                raise ValueError(f"Credenciales faltantes: {', '.join(missing_credentials)}")
            
            self.client = GoogleAdsClient.load_from_dict(config)
            
            logger.info("✅ Cliente de Google Ads configurado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error configurando cliente de Google Ads: {e}")
            raise
    
    def listar_cuentas_accesibles(self) -> Tuple[int, List[Dict]]:
        """
        Lista todas las cuentas del MCC, incluyendo las que tienen problemas
        Muestra información detallada sobre el estado de cada cuenta
        """
        if not self.client:
            raise RuntimeError("Cliente de Google Ads no configurado")

        try:
            # Primero, obtener todas las cuentas del MCC usando list_accessible_customers
            customer_service = self.client.get_service("CustomerService")
            accessible_customers = customer_service.list_accessible_customers()
            
            logger.info(f"✅ Found {len(accessible_customers.resource_names)} customers in MCC")
            
            cuentas_completas = []
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Cuentas adicionales que están en el MCC pero no aparecen en list_accessible_customers
            # debido a problemas de facturación/deuda
            cuentas_faltantes = [
                "1785583613",  # Musicando
                "4890270350",  # RIMS 2
                "5291123262"   # Vetervan
            ]
            
            # Lista completa de customer IDs para procesar
            all_customer_ids = [resource_name.split('/')[-1] for resource_name in accessible_customers.resource_names]
            all_customer_ids.extend(cuentas_faltantes)
            
            # Remover duplicados manteniendo el orden
            seen = set()
            unique_customer_ids = []
            for customer_id in all_customer_ids:
                if customer_id not in seen:
                    seen.add(customer_id)
                    unique_customer_ids.append(customer_id)
            
            logger.info(f"✅ Processing {len(unique_customer_ids)} total customer IDs (including manual additions)")
            
            # Mapeo manual basado en la imagen para nombres conocidos
            nombres_conocidos = {
                "3700518858": "LaReinaPasteleria",
                "1785583613": "Musicando", 
                "4890270350": "RIMS 2",
                "9737121597": "SAL DE JADE",
                "7605115009": "Suspiros Cakes",
                "1554994188": "Suspiros Pastelerías",
                "5291123262": "Vetervan",
                "5119250694": "Aura Marketing LLC"
            }
            
            # Procesar cada cuenta del MCC
            for customer_id in unique_customer_ids:
                try:
                    # Intentar obtener información detallada de la cuenta
                    query = """
                        SELECT 
                            customer.id, 
                            customer.descriptive_name,
                            customer.currency_code,
                            customer.time_zone,
                            customer.test_account,
                            customer.status
                        FROM customer
                        LIMIT 1
                    """
                    
                    response = ga_service.search(customer_id=customer_id, query=query)
                    
                    for row in response:
                        # Cuenta completamente accesible
                        cuenta = {
                            "id": str(row.customer.id),
                            "nombre": row.customer.descriptive_name or nombres_conocidos.get(customer_id, f"Cuenta {row.customer.id}"),
                            "moneda": row.customer.currency_code or "MXN",
                            "zona_horaria": row.customer.time_zone or "America/Mexico_City",
                            "es_test": row.customer.test_account,
                            "estado": row.customer.status.name if hasattr(row.customer.status, 'name') else 'ENABLED',
                            "accesible": True,
                            "problema": None
                        }
                        cuentas_completas.append(cuenta)
                        logger.debug(f"✅ Cuenta accesible: {cuenta['id']} - {cuenta['nombre']}")
                        break
                        
                except Exception as e:
                    # Cuenta en el MCC pero con problemas
                    error_msg = str(e)
                    problema = "Problemas de facturación/deuda"  # Valor por defecto para cuentas faltantes
                    
                    if "CUSTOMER_NOT_ENABLED" in error_msg:
                        problema = "Cuenta deshabilitada"
                    elif "USER_PERMISSION_DENIED" in error_msg:
                        problema = "Sin permisos de acceso"
                    elif "BILLING_SETUP_REQUIRED" in error_msg:
                        problema = "Configuración de facturación requerida"
                    elif "CUSTOMER_SUSPENDED" in error_msg:
                        problema = "Cuenta suspendida"
                    elif "overdue" in error_msg.lower() or "payment" in error_msg.lower():
                        problema = "Problemas de pago/deuda"
                    elif "authorization" in error_msg.lower():
                        problema = "Problemas de autorización"
                    
                    # Agregar cuenta con información limitada pero visible
                    cuenta_problema = {
                        "id": customer_id,
                        "nombre": nombres_conocidos.get(customer_id, f"Cuenta {customer_id}"),
                        "moneda": "MXN",  # Asumir MXN por defecto
                        "zona_horaria": "America/Mexico_City",
                        "es_test": False,
                        "estado": "PROBLEM",
                        "accesible": False,
                        "problema": problema
                    }
                    cuentas_completas.append(cuenta_problema)
                    logger.info(f"⚠️ Cuenta con problemas: {customer_id} - {cuenta_problema['nombre']} - {problema}")
            
            # Ordenar por accesibilidad y luego por nombre
            cuentas_completas.sort(key=lambda x: (not x['accesible'], x['nombre']))
            
            logger.info(f"✅ Total cuentas MCC procesadas: {len(cuentas_completas)}")
            accesibles = len([c for c in cuentas_completas if c['accesible']])
            con_problemas = len([c for c in cuentas_completas if not c['accesible']])
            logger.info(f"   • Accesibles: {accesibles}")
            logger.info(f"   • Con problemas: {con_problemas}")
            
            return len(cuentas_completas), cuentas_completas
            
        except GoogleAdsException as e:
            logger.error(f"❌ Error de Google Ads API: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error listando cuentas del MCC: {e}")
            raise
    
    def obtener_estadisticas_cuenta(self, customer_id: str, dias: int = 30) -> Dict:
        """
        Obtiene estadísticas generales de una cuenta en los últimos N días
        """
        if not self.client:
            raise RuntimeError("Cliente de Google Ads no configurado")
        
        try:
            # Calcular fechas
            fecha_fin = datetime.now()
            fecha_inicio = fecha_fin - timedelta(days=dias)
            
            query = f"""
                SELECT 
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.cost_per_conversion
                FROM account_performance_view
                WHERE segments.date >= '{fecha_inicio.strftime('%Y-%m-%d')}'
                AND segments.date <= '{fecha_fin.strftime('%Y-%m-%d')}'
            """
            
            ga_service = self.client.get_service("GoogleAdsService")
            response = ga_service.search(customer_id=customer_id, query=query)
            
            # Agregar métricas
            total_impressions = 0
            total_clicks = 0
            total_cost_micros = 0
            total_conversions = 0
            
            for row in response:
                total_impressions += row.metrics.impressions
                total_clicks += row.metrics.clicks
                total_cost_micros += row.metrics.cost_micros
                total_conversions += row.metrics.conversions
            
            # Calcular métricas derivadas
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpc = (total_cost_micros / total_clicks / 1000000) if total_clicks > 0 else 0
            cost_per_conversion = (total_cost_micros / total_conversions / 1000000) if total_conversions > 0 else 0
            
            return {
                "impresiones": total_impressions,
                "clics": total_clicks,
                "costo": total_cost_micros / 1000000,  # Convertir de micros a pesos
                "conversiones": total_conversions,
                "ctr": ctr,
                "cpc": cpc,
                "costo_por_conversion": cost_per_conversion,
                "periodo_dias": dias
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas de cuenta {customer_id}: {e}")
            # Retornar datos vacíos en caso de error
            return {
                "impresiones": 0,
                "clics": 0,
                "costo": 0,
                "conversiones": 0,
                "ctr": 0,
                "cpc": 0,
                "costo_por_conversion": 0,
                "periodo_dias": dias,
                "error": str(e)
            }
    
    def obtener_campanas_activas(self, customer_id: str) -> List[Dict]:
        """
        Obtiene lista de campañas activas para una cuenta
        """
        if not self.client:
            raise RuntimeError("Cliente de Google Ads no configurado")
        
        try:
            query = """
                SELECT 
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.advertising_channel_type,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros
                FROM campaign
                WHERE campaign.status = 'ENABLED'
                ORDER BY metrics.cost_micros DESC
                LIMIT 50
            """
            
            ga_service = self.client.get_service("GoogleAdsService")
            response = ga_service.search(customer_id=customer_id, query=query)
            
            campanas = []
            for row in response:
                campana = {
                    "id": row.campaign.id,
                    "nombre": row.campaign.name,
                    "estado": row.campaign.status.name,
                    "tipo": row.campaign.advertising_channel_type.name,
                    "impresiones": row.metrics.impressions,
                    "clics": row.metrics.clicks,
                    "costo": row.metrics.cost_micros / 1000000
                }
                campanas.append(campana)
            
            return campanas
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo campañas de cuenta {customer_id}: {e}")
            return []
    
    def obtener_info_cuenta(self, customer_id: str) -> Dict:
        """
        Obtiene información básica de una cuenta específica.
        Compatible con el panel de administración.
        """
        if not self.client:
            raise RuntimeError("Cliente de Google Ads no configurado")
        
        try:
            query = """
                SELECT 
                    customer.id, 
                    customer.descriptive_name,
                    customer.currency_code,
                    customer.time_zone,
                    customer.test_account,
                    customer.status
                FROM customer
                LIMIT 1
            """
            
            ga_service = self.client.get_service("GoogleAdsService")
            response = ga_service.search(customer_id=customer_id, query=query)
            
            for row in response:
                return {
                    "customer_id": str(row.customer.id),
                    "nombre_cliente": row.customer.descriptive_name or f"Cuenta {row.customer.id}",
                    "moneda": row.customer.currency_code or "MXN",
                    "zona_horaria": row.customer.time_zone or "America/Mexico_City",
                    "es_test": row.customer.test_account,
                    "activa": row.customer.status.name == 'ENABLED' if hasattr(row.customer.status, 'name') else True,
                    "accesible": True,
                    "problema": None,
                    "ads_activos": 0  # Se calculará por separado
                }
            
            # Si no hay resultados, retornar datos básicos
            return {
                "customer_id": customer_id,
                "nombre_cliente": f"Cuenta {customer_id}",
                "moneda": "MXN",
                "zona_horaria": "America/Mexico_City",
                "es_test": False,
                "activa": False,
                "accesible": False,
                "problema": "No se pudo obtener información de la cuenta",
                "ads_activos": 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo info de cuenta {customer_id}: {e}")
            return {
                "customer_id": customer_id,
                "nombre_cliente": f"Cuenta {customer_id}",
                "moneda": "MXN",
                "zona_horaria": "America/Mexico_City",
                "es_test": False,
                "activa": False,
                "accesible": False,
                "problema": str(e),
                "ads_activos": 0
            }
    
    def listar_cuentas_mcc(self) -> List[Dict]:
        """
        Lista todas las cuentas del MCC.
        Alias para listar_cuentas_accesibles que retorna solo la lista de cuentas.
        """
        try:
            total, cuentas = self.listar_cuentas_accesibles()
            
            # Convertir al formato esperado por el panel
            cuentas_formateadas = []
            for cuenta in cuentas:
                cuenta_formateada = {
                    "customer_id": cuenta["id"],
                    "nombre_cliente": cuenta["nombre"],
                    "moneda": cuenta["moneda"],
                    "zona_horaria": cuenta["zona_horaria"],
                    "es_test": cuenta["es_test"],
                    "activa": cuenta["accesible"],
                    "accesible": cuenta["accesible"],
                    "problema": cuenta["problema"],
                    "ads_activos": 0  # Se calculará por separado
                }
                cuentas_formateadas.append(cuenta_formateada)
            
            return cuentas_formateadas
            
        except Exception as e:
            logger.error(f"❌ Error listando cuentas MCC: {e}")
            return []
    
    def obtener_ads_activos_cuenta(self, customer_id: str) -> int:
        """
        Obtiene el número de anuncios activos en una cuenta.
        """
        if not self.client:
            raise RuntimeError("Cliente de Google Ads no configurado")
        
        try:
            query = """
                SELECT 
                    ad_group_ad.ad.id
                FROM ad_group_ad
                WHERE ad_group_ad.status = 'ENABLED'
                AND ad_group.status = 'ENABLED'
                AND campaign.status = 'ENABLED'
            """
            
            ga_service = self.client.get_service("GoogleAdsService")
            response = ga_service.search(customer_id=customer_id, query=query)
            
            # Contar anuncios activos
            count = 0
            for row in response:
                count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo ads activos de cuenta {customer_id}: {e}")
            return 0
    
    def obtener_todos_los_anuncios(self, customer_id: str):
        """
        Obtiene todos los anuncios de una cuenta Google Ads (activos e inactivos),
        devolviendo la estructura detallada igual a Meta Ads para la tabla google_ads_reporte_anuncios.
        """
        if not self.client:
            raise RuntimeError("Cliente de Google Ads no configurado")
        anuncios = []
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Query simplificado - primero obtener solo anuncios básicos
            query = '''
                SELECT
                    ad_group_ad.ad.id,
                    ad_group_ad.status,
                    ad_group_ad.ad.type,
                    ad_group_ad.ad.final_urls,
                    ad_group.name,
                    ad_group.id,
                    campaign.id,
                    campaign.name
                FROM ad_group_ad
                WHERE ad_group_ad.status IN ('ENABLED', 'PAUSED', 'REMOVED')
            '''
            
            response = ga_service.search(customer_id=customer_id, query=query)
            
            for row in response:
                ad = row.ad_group_ad.ad
                tipo_anuncio = ad.type.name if hasattr(ad.type, 'name') else str(ad.type)
                
                # Solo procesar Responsive Search Ads por ahora
                if tipo_anuncio != 'RESPONSIVE_SEARCH_AD':
                    continue
                
                # Obtener detalles específicos del RSA en un query separado
                try:
                    rsa_query = f'''
                        SELECT
                            ad_group_ad.ad.responsive_search_ad.headlines,
                            ad_group_ad.ad.responsive_search_ad.descriptions,
                            ad_group_ad.ad.responsive_search_ad.path1,
                            ad_group_ad.ad.responsive_search_ad.path2,
                            ad_group_ad.ad.final_mobile_urls,
                            ad_group_ad.ad.tracking_url_template,
                            ad_group_ad.ad.final_url_suffix
                        FROM ad_group_ad
                        WHERE ad_group_ad.ad.id = {ad.id}
                    '''
                    
                    rsa_response = ga_service.search(customer_id=customer_id, query=rsa_query)
                    
                    titulos = []
                    descripciones = []
                    path1 = None
                    path2 = None
                    
                    for rsa_row in rsa_response:
                        rsa_ad = rsa_row.ad_group_ad.ad
                        if hasattr(rsa_ad, 'responsive_search_ad'):
                            rsa = rsa_ad.responsive_search_ad
                            titulos = [h.text for h in getattr(rsa, 'headlines', [])]
                            descripciones = [d.text for d in getattr(rsa, 'descriptions', [])]
                            path1 = getattr(rsa, 'path1', None)
                            path2 = getattr(rsa, 'path2', None)
                        break
                
                except Exception as rsa_error:
                    logger.warning(f"Error obteniendo detalles RSA para anuncio {ad.id}: {rsa_error}")
                    titulos = []
                    descripciones = []
                    path1 = None
                    path2 = None
                
                # Mapeo a la estructura de Meta Ads
                anuncio = {
                    'customer_id': customer_id,  # Importante: incluir customer_id para relacionar con cuentas
                    'estado_anuncio': row.ad_group_ad.status.name,
                    'url_final': ad.final_urls[0] if getattr(ad, 'final_urls', []) else None,
                    'titulo_1': titulos[0] if len(titulos) > 0 else None,
                    'pos_titulo_1': 1 if len(titulos) > 0 else None,
                    'titulo_2': titulos[1] if len(titulos) > 1 else None,
                    'pos_titulo_2': 2 if len(titulos) > 1 else None,
                    'titulo_3': titulos[2] if len(titulos) > 2 else None,
                    'pos_titulo_3': 3 if len(titulos) > 2 else None,
                    'titulo_4': titulos[3] if len(titulos) > 3 else None,
                    'pos_titulo_4': 4 if len(titulos) > 3 else None,
                    'titulo_5': titulos[4] if len(titulos) > 4 else None,
                    'pos_titulo_5': 5 if len(titulos) > 4 else None,
                    'titulo_6': titulos[5] if len(titulos) > 5 else None,
                    'pos_titulo_6': 6 if len(titulos) > 5 else None,
                    'titulo_7': titulos[6] if len(titulos) > 6 else None,
                    'pos_titulo_7': 7 if len(titulos) > 6 else None,
                    'titulo_8': titulos[7] if len(titulos) > 7 else None,
                    'pos_titulo_8': 8 if len(titulos) > 7 else None,
                    'titulo_9': titulos[8] if len(titulos) > 8 else None,
                    'pos_titulo_9': 9 if len(titulos) > 8 else None,
                    'titulo_10': titulos[9] if len(titulos) > 9 else None,
                    'pos_titulo_10': 10 if len(titulos) > 9 else None,
                    'titulo_11': titulos[10] if len(titulos) > 10 else None,
                    'pos_titulo_11': 11 if len(titulos) > 10 else None,
                    'titulo_12': titulos[11] if len(titulos) > 11 else None,
                    'pos_titulo_12': 12 if len(titulos) > 11 else None,
                    'titulo_13': titulos[12] if len(titulos) > 12 else None,
                    'pos_titulo_13': 13 if len(titulos) > 12 else None,
                    'titulo_14': titulos[13] if len(titulos) > 13 else None,
                    'pos_titulo_14': 14 if len(titulos) > 13 else None,
                    'titulo_15': titulos[14] if len(titulos) > 14 else None,
                    'pos_titulo_15': 15 if len(titulos) > 14 else None,
                    'descripcion_1': descripciones[0] if len(descripciones) > 0 else None,
                    'pos_desc_1': 1 if len(descripciones) > 0 else None,
                    'descripcion_2': descripciones[1] if len(descripciones) > 1 else None,
                    'pos_desc_2': 2 if len(descripciones) > 1 else None,
                    'descripcion_3': descripciones[2] if len(descripciones) > 2 else None,
                    'pos_desc_3': 3 if len(descripciones) > 2 else None,
                    'descripcion_4': descripciones[3] if len(descripciones) > 3 else None,
                    'pos_desc_4': 4 if len(descripciones) > 3 else None,
                    'ruta_1': path1,
                    'ruta_2': path2,
                    'url_final_movil': None,  # Se obtendrá en query separado si es necesario
                    'plantilla_seguimiento': None,
                    'sufijo_url_final': None,
                    'param_personalizado': None,
                    'campaña': getattr(row.campaign, 'name', None),
                    'grupo_anuncios': getattr(row.ad_group, 'name', None),
                    'estado': row.ad_group_ad.status.name,
                    'motivos_estado': None,
                    'calidad_anuncio': None,
                    'mejoras_efectividad': None,
                    'tipo_anuncio': tipo_anuncio,
                    'clics': 0,  # Se obtendrá en query de métricas separado
                    'impresiones': 0,
                    'ctr': 0.0,
                    'codigo_moneda': 'MXN',  # Default, se obtendrá de la cuenta
                    'cpc_promedio': 0.0,
                    'costo': 0.0,
                    'porcentaje_conversion': 0.0,
                    'conversiones': 0,
                    'costo_por_conversion': 0.0,
                    'id_campaña': str(row.campaign.id) if hasattr(row.campaign, 'id') else None,
                    'id_grupo_anuncios': str(row.ad_group.id) if hasattr(row.ad_group, 'id') else None,
                    'id_anuncio': str(ad.id) if hasattr(ad, 'id') else None,
                }
                anuncios.append(anuncio)
            
            logger.info(f"✅ Obtenidos {len(anuncios)} anuncios para cuenta {customer_id}")
            return anuncios
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo anuncios para {customer_id}: {e}")
            return []
        
    def obtener_keywords_cuenta(self, customer_id: str, periodo_dias: int = 30) -> List[Dict]:
        """
        Obtiene las keywords de una cuenta específica con métricas de rendimiento
        
        Args:
            customer_id: ID de cliente de Google Ads
            periodo_dias: Número de días a incluir en el informe (por defecto: 30)
            
        Returns:
            Lista de keywords con sus métricas
        """
        try:
            if not self.client:
                logger.error("Cliente de Google Ads no configurado")
                return []
            
            # Crear servicio de Google Ads
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Query para obtener keywords con métricas
            # Calcular fechas para el rango
            fecha_fin = datetime.now()
            fecha_inicio = fecha_fin - timedelta(days=periodo_dias)  # Usar el período especificado
            
            fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
            fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')
            
            query = f"""
                SELECT 
                    ad_group_criterion.keyword.text,
                    ad_group_criterion.keyword.match_type,
                    ad_group_criterion.status,
                    campaign.name,
                    campaign.id,
                    ad_group.name,
                    ad_group.id,
                    ad_group_criterion.criterion_id,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.cost_micros,
                    metrics.conversions
                FROM keyword_view 
                WHERE 
                    segments.date BETWEEN '{fecha_inicio_str}' AND '{fecha_fin_str}'
                    AND ad_group_criterion.keyword.text != ''
                ORDER BY metrics.clicks DESC
                LIMIT 50
            """
            
            logger.info(f"🔍 Obteniendo keywords para cuenta {customer_id} (período: {periodo_dias} días)...")
            
            # Ejecutar query
            response = ga_service.search(customer_id=customer_id, query=query)
            
            keywords = []
            for row in response:
                # Obtener métricas
                impressions = row.metrics.impressions if hasattr(row.metrics, 'impressions') else 0
                clicks = row.metrics.clicks if hasattr(row.metrics, 'clicks') else 0
                ctr = row.metrics.ctr if hasattr(row.metrics, 'ctr') else 0.0
                avg_cpc = row.metrics.average_cpc if hasattr(row.metrics, 'average_cpc') else 0
                cost_micros = row.metrics.cost_micros if hasattr(row.metrics, 'cost_micros') else 0
                conversions = row.metrics.conversions if hasattr(row.metrics, 'conversions') else 0
                
                # Convertir tipos de concordancia
                match_type_map = {
                    1: 'EXACTA',
                    2: 'FRASE', 
                    3: 'AMPLIA',
                    4: 'AMPLIA_MODIFICADA'
                }
                
                keyword_info = {
                    'palabra_clave': row.ad_group_criterion.keyword.text,
                    # Eliminamos 'texto_keyword' ya que no existe en la tabla
                    'tipo_concordancia': match_type_map.get(row.ad_group_criterion.keyword.match_type.value, 'DESCONOCIDO'),
                    'estado': row.ad_group_criterion.status.name,
                    'estado_palabra_clave': row.ad_group_criterion.status.name,
                    'campaña': row.campaign.name,
                    'grupo_anuncios': row.ad_group.name,
                    'impresiones': str(impressions),
                    'clics': str(clicks),
                    'ctr': str(round(ctr * 100, 2)),  # Convertir a porcentaje
                    'cpc_promedio': str(avg_cpc / 1000000),  # Convertir de micros a unidad
                    'costo': str(cost_micros / 1000000),  # Convertir de micros a unidad
                    'conversiones': str(conversions),
                    'codigo_moneda': 'MXN',
                    'nombre_nora': 'aura',
                    'id_campaña': int(row.campaign.id) if hasattr(row.campaign, 'id') else None,
                    'id_grupo_anuncios': int(row.ad_group.id) if hasattr(row.ad_group, 'id') else None,
                    'id_palabra_clave': int(row.ad_group_criterion.criterion_id) if hasattr(row.ad_group_criterion, 'criterion_id') else None,
                    'porcentaje_conversion': "0.00" if clicks == 0 else str(round((conversions / clicks) * 100, 2)),
                    'costo_por_conversion': "0.00" if conversions <= 0 else str(round(cost_micros / conversions / 1000000, 2)),
                    'url_final': '',  # No disponible directamente en la consulta
                    'url_final_movil': '',  # No disponible directamente en la consulta
                    'motivos_estado': None  # No disponible directamente en la consulta
                }
                
                keywords.append(keyword_info)
            
            logger.info(f"✅ Obtenidas {len(keywords)} keywords para cuenta {customer_id}")
            return keywords
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo keywords para {customer_id}: {e}")
            return []
    
    def obtener_anuncios_con_metricas(self, customer_id, periodo_dias=30):
        """
        Obtiene anuncios con métricas reales de rendimiento para un período específico
        """
        if not self.client:
            raise RuntimeError("Cliente de Google Ads no configurado")
            
        try:
            ads_service = self.client.get_service("GoogleAdsService")
            
            # Calcular fecha de inicio
            fecha_fin = datetime.now()
            fecha_inicio = fecha_fin - timedelta(days=periodo_dias)
            
            fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
            fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')
            
            query = f"""
                SELECT 
                    ad_group_ad.ad.id,
                    ad_group_ad.ad.final_urls,
                    ad_group_ad.ad.responsive_search_ad.headlines,
                    ad_group_ad.ad.responsive_search_ad.descriptions,
                    ad_group_ad.ad.responsive_search_ad.path1,
                    ad_group_ad.ad.responsive_search_ad.path2,
                    campaign.name,
                    ad_group.name,
                    ad_group_ad.status,
                    ad_group_ad.ad.type,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.ctr,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.average_cpc,
                    campaign.id,
                    ad_group.id
                FROM ad_group_ad 
                WHERE segments.date BETWEEN '{fecha_inicio_str}' AND '{fecha_fin_str}'
                AND ad_group_ad.status != 'REMOVED'
                ORDER BY metrics.impressions DESC
            """
            
            logger.info(f"🔍 Consultando anuncios con métricas para cuenta {customer_id} ({periodo_dias} días)")
            
            response = ads_service.search_stream(customer_id=customer_id, query=query)
            
            anuncios = []
            for batch in response:
                for row in batch.results:
                    try:
                        # Extraer títulos
                        titulos = {}
                        if hasattr(row.ad_group_ad.ad, 'responsive_search_ad') and row.ad_group_ad.ad.responsive_search_ad.headlines:
                            for i, headline in enumerate(row.ad_group_ad.ad.responsive_search_ad.headlines[:15], 1):
                                titulos[f'titulo_{i}'] = headline.text
                                titulos[f'pos_titulo_{i}'] = headline.pinned_field.name if headline.pinned_field else ''
                        
                        # Extraer descripciones
                        descripciones = {}
                        if hasattr(row.ad_group_ad.ad, 'responsive_search_ad') and row.ad_group_ad.ad.responsive_search_ad.descriptions:
                            for i, desc in enumerate(row.ad_group_ad.ad.responsive_search_ad.descriptions[:4], 1):
                                descripciones[f'descripcion_{i}'] = desc.text
                                descripciones[f'pos_desc_{i}'] = desc.pinned_field.name if desc.pinned_field else ''
                        
                        # Construir objeto del anuncio con métricas reales
                        anuncio = {
                            'id_anuncio': str(row.ad_group_ad.ad.id),
                            'customer_id': customer_id,
                            'url_final': row.ad_group_ad.ad.final_urls[0] if row.ad_group_ad.ad.final_urls else '',
                            'campaña': row.campaign.name,
                            'grupo_anuncios': row.ad_group.name,
                            'estado': row.ad_group_ad.status.name,
                            'tipo_anuncio': row.ad_group_ad.ad.type.name,
                            'id_campaña': str(row.campaign.id),
                            'id_grupo_anuncios': str(row.ad_group.id),
                            
                            # Métricas reales
                            'impresiones': str(row.metrics.impressions),
                            'clics': str(row.metrics.clicks),
                            'ctr': f"{row.metrics.ctr:.2f}",
                            'costo': f"{row.metrics.cost_micros / 1000000:.2f}",
                            'conversiones': str(row.metrics.conversions),
                            'costo_por_conversion': "0.00" if row.metrics.conversions <= 0 else f"{row.metrics.cost_micros / row.metrics.conversions / 1000000:.2f}",
                            
                            # Rutas
                            'ruta_1': row.ad_group_ad.ad.responsive_search_ad.path1 if hasattr(row.ad_group_ad.ad, 'responsive_search_ad') else '',
                            'ruta_2': row.ad_group_ad.ad.responsive_search_ad.path2 if hasattr(row.ad_group_ad.ad, 'responsive_search_ad') else '',
                            
                            # Otros campos
                            'codigo_moneda': 'MXN',
                            'nombre_nora': 'aura',
                            'empresa_id': None  # Se asignará más tarde si es necesario
                        }
                        
                        # Agregar títulos y descripciones
                        anuncio.update(titulos)
                        anuncio.update(descripciones)
                        
                        anuncios.append(anuncio)
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Error procesando anuncio individual: {e}")
                        continue
            
            logger.info(f"✅ Obtenidos {len(anuncios)} anuncios con métricas para cuenta {customer_id}")
            return anuncios
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo anuncios con métricas para cuenta {customer_id}: {e}")
            return []
