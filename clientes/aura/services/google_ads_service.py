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
    
    def listar_cuentas_mcc(self) -> List[Dict]:
        """
        Lista todas las cuentas del MCC para importación
        Alias de listar_cuentas_accesibles que devuelve solo la lista de cuentas
        """
        try:
            total, cuentas = self.listar_cuentas_accesibles()
            # Convertir formato a lo que espera el panel
            cuentas_formato_panel = []
            for cuenta in cuentas:
                cuenta_panel = {
                    'customer_id': cuenta['id'],
                    'nombre_cliente': cuenta['nombre'],
                    'activa': cuenta['accesible'] and cuenta['estado'] == 'ENABLED',
                    'accesible': cuenta['accesible'],
                    'problema': cuenta['problema'],
                    'ads_activos': 0,  # Se calculará después
                    'moneda': cuenta['moneda'],
                    'zona_horaria': cuenta['zona_horaria']
                }
                cuentas_formato_panel.append(cuenta_panel)
            
            logger.info(f"✅ Devolviendo {len(cuentas_formato_panel)} cuentas para importación")
            return cuentas_formato_panel
            
        except Exception as e:
            logger.error(f"❌ Error listando cuentas del MCC: {e}")
            return []
    
    def obtener_info_cuenta(self, customer_id: str) -> Dict:
        """
        Obtiene información actualizada de una cuenta específica
        """
        if not self.client:
            raise RuntimeError("Cliente de Google Ads no configurado")
        
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Obtener información básica de la cuenta
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
            
            # Mapeo manual para cuentas conocidas
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
            
            for row in response:
                # Obtener número de anuncios activos
                ads_activos = self.obtener_ads_activos_cuenta(customer_id)
                
                info = {
                    'nombre_cliente': row.customer.descriptive_name or nombres_conocidos.get(customer_id, f"Cuenta {customer_id}"),
                    'activa': row.customer.status.name == 'ENABLED',
                    'accesible': True,
                    'problema': None,
                    'ads_activos': ads_activos,
                    'moneda': row.customer.currency_code or 'MXN',
                    'zona_horaria': row.customer.time_zone or 'America/Mexico_City'
                }
                
                logger.debug(f"✅ Info actualizada para cuenta {customer_id}: {info}")
                return info
            
            # Si no se encuentra la cuenta, devolver info por defecto
            return {
                'nombre_cliente': nombres_conocidos.get(customer_id, f"Cuenta {customer_id}"),
                'activa': False,
                'accesible': False,
                'problema': 'Cuenta no accesible desde la API',
                'ads_activos': 0,
                'moneda': 'MXN',
                'zona_horaria': 'America/Mexico_City'
            }
            
        except GoogleAdsException as e:
            logger.warning(f"⚠️ Cuenta {customer_id} no accesible: {e}")
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
            
            return {
                'nombre_cliente': nombres_conocidos.get(customer_id, f"Cuenta {customer_id}"),
                'activa': False,
                'accesible': False,
                'problema': f'Error de API: {str(e)[:100]}...' if len(str(e)) > 100 else str(e),
                'ads_activos': 0,
                'moneda': 'MXN',
                'zona_horaria': 'America/Mexico_City'
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo info de cuenta {customer_id}: {e}")
            return {
                'nombre_cliente': f"Cuenta {customer_id}",
                'activa': False,
                'accesible': False,
                'problema': f'Error: {str(e)[:100]}...' if len(str(e)) > 100 else str(e),
                'ads_activos': 0,
                'moneda': 'MXN',
                'zona_horaria': 'America/Mexico_City'
            }
    
    def obtener_ads_activos_cuenta(self, customer_id: str) -> int:
        """
        Obtiene el número de anuncios activos para una cuenta específica
        """
        if not self.client:
            raise RuntimeError("Cliente de Google Ads no configurado")
        
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Consultar anuncios activos (ENABLED)
            query = """
                SELECT 
                    ad_group_ad.ad.id
                FROM ad_group_ad 
                WHERE ad_group_ad.status = 'ENABLED'
                AND ad_group.status = 'ENABLED'
                AND campaign.status = 'ENABLED'
            """
            
            response = ga_service.search(customer_id=customer_id, query=query)
            
            # Contar anuncios activos
            ads_activos = sum(1 for _ in response)
            
            logger.debug(f"✅ Cuenta {customer_id} tiene {ads_activos} anuncios activos")
            return ads_activos
            
        except GoogleAdsException as e:
            logger.warning(f"⚠️ No se pueden obtener anuncios activos para cuenta {customer_id}: {e}")
            return 0
        except Exception as e:
            logger.error(f"❌ Error obteniendo anuncios activos de cuenta {customer_id}: {e}")
            return 0

# Crear instancia global del servicio para importación
google_ads_service = GoogleAdsService()
