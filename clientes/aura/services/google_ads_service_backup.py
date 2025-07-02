# -*- coding: utf-8 -*-
"""
Servicio integrado de Google Ads para el panel de administración
Basado en las pruebas exitosas de conexión REST
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
    Utiliza la configuración exitosa probada en los tests
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
                "use_proto_plus": True,
                "transport": "rest"  # Usar REST que funciona correctamente
            }
            
            # Validar configuración
            missing_vars = []
            for k, v in config.items():
                if not v and k not in ["use_proto_plus", "transport"]:
                    missing_vars.append(k)
            
            if missing_vars:
                raise ValueError(f"Faltan variables de entorno: {missing_vars}")
            
            # Log de configuración (sin mostrar tokens sensibles)
            logger.info(f"Configurando cliente Google Ads:")
            logger.info(f"  - Developer token: {'✓' if config['developer_token'] else '✗'}")
            logger.info(f"  - Client ID: {'✓' if config['client_id'] else '✗'}")
            logger.info(f"  - Client secret: {'✓' if config['client_secret'] else '✗'}")
            logger.info(f"  - Refresh token: {'✓' if config['refresh_token'] else '✗'}")
            logger.info(f"  - Login customer ID: {login_customer_id}")
            logger.info(f"  - Transport: {config['transport']}")
            
            self.client = GoogleAdsClient.load_from_dict(config)
            self.login_customer_id = login_customer_id
            
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
            
            # Procesar cada cuenta del MCC
            for customer_id in all_customer_ids:
                
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
                    problema = "Desconocido"
                    
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
                    logger.info(f"⚠️ Cuenta con problemas: {customer_id} - {problema}")
            
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
            
        except GoogleAdsException as e:
            logger.error(f"❌ Error de Google Ads API: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error listando cuentas del MCC: {e}")
            raise
            
        except GoogleAdsException as e:
            logger.error(f"❌ Error de Google Ads API: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error listando cuentas: {e}")
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
            
            # Acumular métricas
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
            cpc = (total_cost_micros / 1_000_000 / total_clicks) if total_clicks > 0 else 0
            costo_total = total_cost_micros / 1_000_000
            
            estadisticas = {
                "periodo_dias": dias,
                "impresiones": total_impressions,
                "clics": total_clicks,
                "costo_total": round(costo_total, 2),
                "conversiones": total_conversions,
                "ctr": round(ctr, 2),
                "cpc_promedio": round(cpc, 2),
                "fecha_inicio": fecha_inicio.strftime('%Y-%m-%d'),
                "fecha_fin": fecha_fin.strftime('%Y-%m-%d')
            }
            
            logger.info(f"✅ Estadísticas obtenidas para cuenta {customer_id}")
            return estadisticas
            
        except GoogleAdsException as e:
            logger.error(f"❌ Error de Google Ads API obteniendo estadísticas: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            raise
    
    def obtener_campanas_top(self, customer_id: str, limite: int = 10, dias: int = 30) -> List[Dict]:
        """
        Obtiene las campañas principales por impresiones en los últimos N días
        """
        if not self.client:
            raise RuntimeError("Cliente de Google Ads no configurado")
        
        try:
            fecha_fin = datetime.now()
            fecha_inicio = fecha_fin - timedelta(days=dias)
            
            query = f"""
                SELECT 
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.advertising_channel_type,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.ctr
                FROM campaign
                WHERE segments.date >= '{fecha_inicio.strftime('%Y-%m-%d')}'
                AND segments.date <= '{fecha_fin.strftime('%Y-%m-%d')}'
                ORDER BY metrics.impressions DESC
                LIMIT {limite}
            """
            
            ga_service = self.client.get_service("GoogleAdsService")
            response = ga_service.search(customer_id=customer_id, query=query)
            
            campanas = []
            for row in response:
                campana = {
                    "id": str(row.campaign.id),
                    "nombre": row.campaign.name,
                    "estado": row.campaign.status.name,
                    "tipo": row.campaign.advertising_channel_type.name,
                    "impresiones": row.metrics.impressions,
                    "clics": row.metrics.clicks,
                    "costo": round(row.metrics.cost_micros / 1_000_000, 2),
                    "conversiones": row.metrics.conversions,
                    "ctr": round(row.metrics.ctr, 2)
                }
                campanas.append(campana)
            
            logger.info(f"✅ Obtenidas {len(campanas)} campañas top para cuenta {customer_id}")
            return campanas
            
        except GoogleAdsException as e:
            logger.error(f"❌ Error de Google Ads API obteniendo campañas: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error obteniendo campañas: {e}")
            raise
    
    def obtener_palabras_clave_top(self, customer_id: str, limite: int = 20, dias: int = 30) -> List[Dict]:
        """
        Obtiene las palabras clave principales por impresiones
        """
        if not self.client:
            raise RuntimeError("Cliente de Google Ads no configurado")
        
        try:
            fecha_fin = datetime.now()
            fecha_inicio = fecha_fin - timedelta(days=dias)
            
            query = f"""
                SELECT 
                    ad_group_criterion.keyword.text,
                    ad_group_criterion.keyword.match_type,
                    campaign.name,
                    ad_group.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.ctr,
                    metrics.average_cpc
                FROM keyword_view
                WHERE segments.date >= '{fecha_inicio.strftime('%Y-%m-%d')}'
                AND segments.date <= '{fecha_fin.strftime('%Y-%m-%d')}'
                AND ad_group_criterion.status = 'ENABLED'
                ORDER BY metrics.impressions DESC
                LIMIT {limite}
            """
            
            ga_service = self.client.get_service("GoogleAdsService")
            response = ga_service.search(customer_id=customer_id, query=query)
            
            keywords = []
            for row in response:
                keyword = {
                    "texto": row.ad_group_criterion.keyword.text,
                    "tipo_coincidencia": row.ad_group_criterion.keyword.match_type.name,
                    "campana": row.campaign.name,
                    "grupo_anuncios": row.ad_group.name,
                    "impresiones": row.metrics.impressions,
                    "clics": row.metrics.clicks,
                    "costo": round(row.metrics.cost_micros / 1_000_000, 2),
                    "ctr": round(row.metrics.ctr, 2),
                    "cpc_promedio": round(row.metrics.average_cpc / 1_000_000, 2)
                }
                keywords.append(keyword)
            
            logger.info(f"✅ Obtenidas {len(keywords)} palabras clave top para cuenta {customer_id}")
            return keywords
            
        except GoogleAdsException as e:
            logger.error(f"❌ Error de Google Ads API obteniendo keywords: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error obteniendo keywords: {e}")
            raise
    
    def obtener_rendimiento_anuncios(self, customer_id: str, limite: int = 15, dias: int = 30) -> List[Dict]:
        """
        Obtiene el rendimiento de los anuncios principales
        """
        if not self.client:
            raise RuntimeError("Cliente de Google Ads no configurado")
        
        try:
            fecha_fin = datetime.now()
            fecha_inicio = fecha_fin - timedelta(days=dias)
            
            query = f"""
                SELECT 
                    ad_group_ad.ad.id,
                    ad_group_ad.ad.name,
                    ad_group_ad.status,
                    campaign.name,
                    ad_group.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.ctr
                FROM ad_group_ad
                WHERE segments.date >= '{fecha_inicio.strftime('%Y-%m-%d')}'
                AND segments.date <= '{fecha_fin.strftime('%Y-%m-%d')}'
                ORDER BY metrics.impressions DESC
                LIMIT {limite}
            """
            
            ga_service = self.client.get_service("GoogleAdsService")
            response = ga_service.search(customer_id=customer_id, query=query)
            
            anuncios = []
            for row in response:
                anuncio = {
                    "id": str(row.ad_group_ad.ad.id),
                    "nombre": row.ad_group_ad.ad.name or f"Anuncio {row.ad_group_ad.ad.id}",
                    "estado": row.ad_group_ad.status.name,
                    "campana": row.campaign.name,
                    "grupo_anuncios": row.ad_group.name,
                    "impresiones": row.metrics.impressions,
                    "clics": row.metrics.clicks,
                    "costo": round(row.metrics.cost_micros / 1_000_000, 2),
                    "conversiones": row.metrics.conversions,
                    "ctr": round(row.metrics.ctr, 2)
                }
                anuncios.append(anuncio)
            
            logger.info(f"✅ Obtenidos {len(anuncios)} anuncios para cuenta {customer_id}")
            return anuncios
            
        except GoogleAdsException as e:
            logger.error(f"❌ Error de Google Ads API obteniendo anuncios: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error obteniendo anuncios: {e}")
            raise
    
    def obtener_reporte_completo(self, customer_id: str, dias: int = 30) -> Dict:
        """
        Obtiene un reporte completo con todas las métricas principales
        """
        try:
            logger.info(f"🔍 Generando reporte completo para cuenta {customer_id}")
            
            # Obtener todas las métricas en paralelo conceptual
            estadisticas = self.obtener_estadisticas_cuenta(customer_id, dias)
            campanas = self.obtener_campanas_top(customer_id, 10, dias)
            keywords = self.obtener_palabras_clave_top(customer_id, 20, dias)
            anuncios = self.obtener_rendimiento_anuncios(customer_id, 15, dias)
            
            # Calcular estados de anuncios
            estados_anuncios = {}
            for anuncio in anuncios:
                estado = anuncio["estado"]
                estados_anuncios[estado] = estados_anuncios.get(estado, 0) + 1
            
            reporte = {
                "customer_id": customer_id,
                "estadisticas_generales": estadisticas,
                "top_campanas": campanas,
                "top_keywords": keywords,
                "rendimiento_anuncios": anuncios,
                "distribucion_estados_anuncios": estados_anuncios,
                "resumen": {
                    "total_campanas": len(campanas),
                    "total_keywords": len(keywords),
                    "total_anuncios": len(anuncios)
                },
                "generado_en": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info("✅ Reporte completo generado exitosamente")
            return reporte
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte completo: {e}")
            raise

# Instancia global del servicio
google_ads_service = GoogleAdsService()
