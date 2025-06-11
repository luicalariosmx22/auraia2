"""
Envoltura ligera para la Marketing API (Graph v23.0).

• _SOLO_ incluye lo necesario para listar campañas activas.  
• Si más adelante necesitas crear campañas, ad sets, creativos, etc.,
  simplemente añade más helpers siguiendo el mismo patrón.
"""

from __future__ import annotations

import os, json, requests
from dotenv import load_dotenv
load_dotenv()

API_VER   = "v23.0"
TOKEN     = os.getenv("META_ACCESS_TOKEN")          # token largo o System-User
BASE_URL  = f"https://graph.facebook.com/{API_VER}"

class MetaAPIError(RuntimeError):
    """Error simple para envolver las excepciones HTTP."""


def _request(edge: str, params: dict | None = None) -> dict:
    url    = f"{BASE_URL}/{edge.lstrip('/')}"
    params = params or {}
    params["access_token"] = TOKEN
    try:
        res = requests.get(url, params=params, timeout=30)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.HTTPError as e:
        # Adjuntamos el body completo para que sea más fácil depurar.
        raise MetaAPIError(f"{e} → {res.text}") from None

# ─────────────────────────────────────────────────────────────────────────────
#  API pública del helper
# ─────────────────────────────────────────────────────────────────────────────

def listar_campañas_activas(ad_account_id: str, access_token: str = None, *, limit: int = 25) -> list[dict]:
    """
    Devuelve las campañas (todas, no solo ACTIVE) para la cuenta dada.
    `ad_account_id` se pasa SIN el prefijo 'act_'.
    Usa el access_token de la cuenta si se provee, si no usa el global del .env.
    """
    token = access_token if (access_token and access_token.strip()) else TOKEN
    params = {
        "fields": "id,name,objective,effective_status,status,daily_budget,insights{impressions,clicks,reach,spend,objective}",
        "limit": limit,
        "access_token": token
    }
    url = f"{BASE_URL}/act_{ad_account_id}/campaigns"
    try:
        res = requests.get(url, params=params, timeout=30)
        res.raise_for_status()
        return res.json().get("data", [])
    except requests.exceptions.HTTPError as e:
        raise MetaAPIError(f"{e} → {res.text}") from None

def listar_campañas_activas(ad_account_id: str, limit: int = 25) -> list[dict]:
    """
    Devuelve campañas con effective_status = ACTIVE.
    `ad_account_id` va SIN prefijo 'act_' (ej. '16626756').
    """
    filtering = json.dumps([{
        "field": "effective_status",
        "operator": "IN",
        "value": ["ACTIVE"]
    }])
    params = {
        "fields": "id,name,objective,effective_status",
        "filtering": filtering,
        "limit": limit
    }
    return _request(f"act_{ad_account_id}/campaigns", params).get("data", [])

def get_token_status(token: str = None) -> dict:
    """
    Consulta el endpoint /debug_token de Meta para obtener la expiración y días restantes del token.
    Retorna un dict con expires_at (timestamp), expires_date (YYYY-MM-DD), y days_left.
    """
    import time
    token = token or TOKEN
    app_token = TOKEN  # El mismo token global sirve como app_token para debug_token
    url = f"https://graph.facebook.com/debug_token"
    params = {
        "input_token": token,
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
        res_info = requests.get(url_info, params=params_info, timeout=15)
        res_info.raise_for_status()
        data_info = res_info.json()
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
        res_camp = requests.get(url_camp, params=params_camp, timeout=15)
        res_camp.raise_for_status()
        data_camp = res_camp.json().get("data", [])
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
        res_ads = requests.get(url_ads, params=params_ads, timeout=15)
        res_ads.raise_for_status()
        data_ads = res_ads.json().get("data", [])
        ads_activos = len(data_ads)
    except Exception:
        ads_activos = None

    return {
        "nombre_cliente": nombre_cliente,
        "account_status": account_status,
        "anuncios_activos": anuncios_activos,
        "ads_activos": ads_activos
    }

def listar_anuncios_activos(ad_account_id: str) -> list:
    """
    Devuelve una lista de anuncios activos para la cuenta dada usando el endpoint /me?fields=adaccounts{ads{adset,name,status,preview_shareable_link,campaign}}.
    Cada anuncio incluye: ad_id, name, status, adset, preview_shareable_link, campaign.
    Imprime en consola los adaccounts y la cuenta encontrada para depuración.
    """
    import requests
    fields = "adaccounts{ads{adset,name,status,preview_shareable_link,campaign}}"
    params = {
        "fields": fields,
        "access_token": TOKEN
    }
    url = f"{BASE_URL}/me"
    res = requests.get(url, params=params, timeout=20)
    res.raise_for_status()
    data = res.json()
    adaccounts = data.get("adaccounts", {}).get("data", [])
    print("[MetaAds] adaccounts recibidos:", adaccounts)
    cuenta = next((c for c in adaccounts if c.get("id") == f"act_{ad_account_id}" or c.get("id") == ad_account_id), None)
    print(f"[MetaAds] Buscando cuenta_id={ad_account_id} → cuenta encontrada:", cuenta)
    if not cuenta:
        return []
    ads = cuenta.get("ads", {}).get("data", [])
    print(f"[MetaAds] Anuncios encontrados para la cuenta:", ads)
    return [
        {
            "ad_id": a.get("id"),
            "name": a.get("name"),
            "status": a.get("status"),
            "adset": a.get("adset"),
            "preview_shareable_link": a.get("preview_shareable_link"),
            "campaign": a.get("campaign")
        }
        for a in ads
    ]

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