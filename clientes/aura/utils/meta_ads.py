"""
Envoltura ligera para la Marketing API (Graph v23.0).

• _SOLO_ incluye lo necesario para listar campañas activas.  
• Si más adelante necesitas crear campañas, ad sets, creativos, etc.,
  simplemente añade más helpers siguiendo el mismo patrón.
"""

from __future__ import annotations

import os, json, requests, time
from dotenv import load_dotenv
load_dotenv()

API_VER   = "v23.0"
TOKEN     = os.getenv("META_ACCESS_TOKEN")          # token largo o System-User
BASE_URL  = f"https://graph.facebook.com/{API_VER}"

class MetaAPIError(RuntimeError):
    """Error simple para envolver las excepciones HTTP."""

def _request_with_retry(url: str, params: dict, max_retries: int = 3, timeout: int = 30) -> dict:
    """Realiza una petición con reintentos en caso de errores de red."""
    for intento in range(max_retries + 1):
        try:
            res = requests.get(url, params=params, timeout=timeout)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as e:
            # Error HTTP (400, 401, etc.) - no reintentar
            raise MetaAPIError(f"{e} → {res.text}") from None
        except (requests.exceptions.ConnectionError, 
                requests.exceptions.Timeout,
                requests.exceptions.RequestException) as e:
            if intento < max_retries:
                wait_time = (intento + 1) * 2  # 2, 4, 6 segundos
                print(f"⚠️ Error de conexión (intento {intento + 1}/{max_retries + 1}): {e}")
                print(f"⏳ Esperando {wait_time} segundos antes del siguiente intento...")
                time.sleep(wait_time)
                continue
            else:
                raise MetaAPIError(f"Error de conectividad después de {max_retries + 1} intentos: {e}")
    
    # Esto no debería ejecutarse nunca, pero para satisfacer el type checker
    raise MetaAPIError("Error inesperado en _request_with_retry")


def _request(edge: str, params: dict | None = None) -> dict:
    url    = f"{BASE_URL}/{edge.lstrip('/')}"
    params = params or {}
    params["access_token"] = TOKEN
    return _request_with_retry(url, params)

# ─────────────────────────────────────────────────────────────────────────────
#  API pública del helper
# ─────────────────────────────────────────────────────────────────────────────

def listar_campañas_activas(ad_account_id: str, limit: int = 200) -> list:
    """
    Devuelve campañas activas para la cuenta publicitaria indicada.
    
    Args:
        ad_account_id (str): ID de la cuenta publicitaria (sin prefijo 'act_')
        limit (int, optional): Límite de resultados a devolver. Por defecto 200.
        
    Returns:
        list: Lista de campañas activas
    """
    import os
    import requests
    import json
    from clientes.aura.logger import logger
    
    # Obtener token de acceso
    token = os.getenv('META_ACCESS_TOKEN')
    if not token:
        logger.error("No se encontró token de acceso para Meta Ads")
        return []
    
    # Construir filtro para campañas activas
    filtering = json.dumps([{
        "field": "effective_status",
        "operator": "IN",
        "value": ["ACTIVE"]
    }])
    
    # Parámetros de la petición
    params = {
        "fields": "id,name,status,objective,start_time,stop_time,daily_budget,lifetime_budget",
        "filtering": filtering,
        "limit": limit,
        "access_token": token
    }
    
    # URL de la API de Meta para campañas
    url = f"https://graph.facebook.com/v19.0/act_{ad_account_id}/campaigns"
    
    try:
        # Realizar petición con timeout de 10 segundos
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        # Procesar respuesta
        data = response.json()
        campañas = data.get("data", [])
        
        # Dar formato a los resultados
        for campaña in campañas:
            # Convertir presupuesto de centavos a unidades monetarias
            if "daily_budget" in campaña:
                campaña["daily_budget"] = float(campaña["daily_budget"]) / 100
            if "lifetime_budget" in campaña:
                campaña["lifetime_budget"] = float(campaña["lifetime_budget"]) / 100
        
        logger.info(f"Obtenidas {len(campañas)} campañas activas para cuenta {ad_account_id}")
        return campañas
        
    except requests.Timeout:
        logger.error(f"Timeout al consultar campañas activas para cuenta {ad_account_id}")
        return []
    except Exception as e:
        logger.error(f"Error al obtener campañas activas para cuenta {ad_account_id}: {str(e)}")
        return []

def get_token_status(token: str | None = None) -> dict:
    """
    Consulta el endpoint /debug_token de Meta para obtener la expiración y días restantes del token.
    Retorna un dict con expires_at (timestamp), expires_date (YYYY-MM-DD), y days_left.
    """
    import time
    actual_token = token or TOKEN
    if not actual_token:
        return {"error": "No se encontró token de acceso"}
    
    app_token = TOKEN  # El mismo token global sirve como app_token para debug_token
    url = f"https://graph.facebook.com/debug_token"
    params = {
        "input_token": actual_token,
        "access_token": app_token
    }
    try:
        res = requests.get(url, params=params, timeout=15)
        res.raise_for_status()
        data = res.json().get("data", {})
        expires_at = data.get("expires_at")
        if expires_at:
            expires_date = time.strftime('%Y-%m-%d', time.localtime(expires_at))
            days_left = int((expires_at - time.time()) // 86400)
        else:
            expires_date = None
            days_left = None
        return {
            "expires_at": expires_at,
            "expires_date": expires_date,
            "days_left": days_left,
            "is_valid": data.get("is_valid", False),
            "scopes": data.get("scopes", []),
            "user_id": data.get("user_id"),
            "type": data.get("type"),
        }
    except Exception as e:
        return {"error": str(e)}

def obtener_info_cuenta_ads(ad_account_id: str) -> dict:
    """
    Dado un ID de cuenta publicitaria (sin prefijo 'act_'), obtiene:
    - nombre_cliente (name)
    - account_status
    - anuncios_activos (número de campañas activas)
    """
    # 1. Info básica de la cuenta
    url_info = f"{BASE_URL}/act_{ad_account_id}"
    params_info = {
        "fields": "name,account_status",
        "access_token": TOKEN
    }
    try:
        data_info = _request_with_retry(url_info, params_info)
        nombre_cliente = data_info.get("name", "")
        account_status = data_info.get("account_status", None)
    except Exception as e:
        raise MetaAPIError(f"Error obteniendo info de cuenta: {e}")

    # 2. Número de campañas activas
    try:
        filtering = json.dumps([
            {"field": "effective_status", "operator": "IN", "value": ["ACTIVE"]}
        ])
        params_camp = {
            "fields": "id",
            "filtering": filtering,
            "access_token": TOKEN
        }
        url_camp = f"{BASE_URL}/act_{ad_account_id}/campaigns"
        data_camp = _request_with_retry(url_camp, params_camp).get("data", [])
        anuncios_activos = len(data_camp)
    except Exception:
        anuncios_activos = None

    # 3. Número de anuncios con entrega ACTIVA
    try:
        filtering_ads = json.dumps([
            {"field": "delivery_info", "operator": "IN", "value": ["ACTIVE"]}
        ])
        params_ads = {
            "fields": "id,delivery_info",
            "filtering": filtering_ads,
            "limit": 200,
            "access_token": TOKEN
        }
        url_ads = f"{BASE_URL}/act_{ad_account_id}/ads"
        data_ads = _request_with_retry(url_ads, params_ads).get("data", [])
        ads_activos = len(data_ads)
    except Exception:
        ads_activos = None

    return {
        "nombre_cliente": nombre_cliente,
        "account_status": account_status,
        "anuncios_activos": anuncios_activos,
        "ads_activos": ads_activos
    }

def listar_anuncios_activos(ad_account_id: str, limit: int = 200) -> list[dict]:
    """
    Devuelve anuncios activos para la cuenta dada.
    `ad_account_id` va SIN prefijo 'act_'.
    """
    import requests
    import json
    import os
    from clientes.aura.logger import logger
    
    token = os.getenv('META_ACCESS_TOKEN')
    if not token:
        logger.error("No se encontró token de acceso para Meta Ads")
        return []
        
    filtering = json.dumps([{
        "field": "effective_status",
        "operator": "IN",
        "value": ["ACTIVE"]
    }])
    
    params = {
        "fields": "id,name,status,adset_id,campaign_id,preview_shareable_link",
        "filtering": filtering,
        "limit": limit,
        "access_token": token
    }
    
    url = f"{BASE_URL}/act_{ad_account_id}/ads"
    try:
        res = requests.get(url, params=params, timeout=30)
        res.raise_for_status()
        return res.json().get("data", [])
    except Exception as e:
        logger.error(f"Error al obtener anuncios activos: {str(e)}")
        return []

from clientes.aura.utils.supabase_client import supabase

def obtener_ads_activos_cuenta(ad_account_id, access_token=None):
    """
    Consulta la API de Meta para obtener el número de anuncios activos (entrega activa) de una cuenta publicitaria.
    """
    BASE_URL = "https://graph.facebook.com/v19.0"
    token = access_token or os.getenv('META_ACCESS_TOKEN')
    url = f"{BASE_URL}/act_{ad_account_id}/ads"
    params = {
        "fields": "id,name,effective_status",
        "limit": 200,
        "access_token": token
    }
    activos = 0
    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json().get('data', [])
        activos = sum(1 for ad in data if ad.get('effective_status') == 'ACTIVE')
    except Exception as e:
        print(f"[MetaAds] Error al obtener ads activos para {ad_account_id}: {e}")
    return activos

def obtener_reporte_campanas(cuenta_id, fecha_inicio=None, fecha_fin=None):
    """
    Obtiene un reporte de campañas de Meta Ads para una cuenta específica.
    
    Args:
        cuenta_id (str): ID de la cuenta publicitaria de Meta.
        fecha_inicio (str, optional): Fecha de inicio del reporte en formato YYYY-MM-DD.
        fecha_fin (str, optional): Fecha de fin del reporte en formato YYYY-MM-DD.
        
    Returns:
        list: Lista de campañas con sus métricas de rendimiento.
    """
    import os
    import requests
    from datetime import datetime, timedelta
    from clientes.aura.logger import logger
    
    # Si no se proporcionan fechas, usar últimos 30 días
    if not fecha_inicio or not fecha_fin:
        fecha_fin = datetime.now().strftime('%Y-%m-%d')
        fecha_inicio = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Obtener token de acceso
    access_token = os.getenv('META_ACCESS_TOKEN')
    if not access_token:
        logger.error("No se encontró el token de acceso para Meta Ads")
        return []
        
    # Construir la URL para consultar la API de Meta
    url = f"https://graph.facebook.com/v19.0/act_{cuenta_id}/insights"
    params = {
        'access_token': access_token,
        'level': 'campaign',
        'fields': 'campaign_name,spend,impressions,clicks,ctr,cpc,reach,frequency',
        'time_range': {
            'since': fecha_inicio,
            'until': fecha_fin
        },
        'time_increment': 1,  # Datos diarios
        'limit': 1000
    }
    
    try:
        # Convertir el diccionario time_range a formato JSON
        import json
        params['time_range'] = json.dumps(params['time_range'])
        
        # Realizar la solicitud a la API
        response = requests.get(url, params=params)
        response.raise_for_status()  # Lanza excepción si hay error HTTP
        
        data = response.json()
        if 'data' not in data:
            logger.warning(f"No se encontraron datos para la cuenta {cuenta_id} en el período especificado")
            return []
        
        # Procesar y formatear los resultados
        campañas = []
        for item in data.get('data', []):
            campaña = {
                'id': item.get('campaign_id'),
                'nombre': item.get('campaign_name', 'Sin nombre'),
                'gasto': float(item.get('spend', 0)),
                'impresiones': int(item.get('impressions', 0)),
                'clicks': int(item.get('clicks', 0)),
                'ctr': float(item.get('ctr', 0)) * 100,  # Convertir a porcentaje
                'cpc': float(item.get('cpc', 0)),
                'alcance': int(item.get('reach', 0)),
                'frecuencia': float(item.get('frequency', 0)),
                'fecha': item.get('date_start')
            }
            campañas.append(campaña)
            
        logger.info(f"Reporte generado para cuenta {cuenta_id}: {len(campañas)} resultados")
        return campañas
        
    except Exception as e:
        logger.error(f"Error al obtener reporte de campañas para cuenta {cuenta_id}: {str(e)}")
        return []