# ✅ Archivo: clientes/aura/utils/verificar_http.py

import requests
from urllib.parse import urlparse, urljoin
from typing import Dict, Union

def verificar_respuesta_http(url: str) -> Dict[str, Union[bool, int, str, None]]:
    """
    Verifica si una URL responde correctamente y proporciona diagnóstico detallado.
    
    Args:
        url (str): URL a verificar (absoluta o relativa)
        
    Returns:
        dict: Diagnóstico con:
            - ok (bool): Si la ruta existe y responde
            - status (int | None): Código de estado HTTP
            - causa (str): Explicación en lenguaje natural
            - location (str | None): URL de redirección si aplica
    """
    try:
        # Validar y normalizar URL
        parsed = urlparse(url)
        if not parsed.scheme and not parsed.netloc:
            base_url = "http://localhost:5000"
            url = urljoin(base_url, url.lstrip('/'))
            parsed = urlparse(url)
            
        if not parsed.scheme or not parsed.netloc:
            return {
                "ok": False,
                "status": None,
                "causa": f"URL inválida o malformada: {url}",
                "location": None
            }

        # Realizar petición con timeout
        resp = requests.get(url, timeout=5, allow_redirects=False)
        status = resp.status_code
        location = resp.headers.get("Location", "")

        # Analizar respuesta según código HTTP
        if status == 200:
            return {
                "ok": True,
                "status": status,
                "causa": "✅ Ruta activa y respondiendo",
                "location": None
            }
            
        if status == 302:
            if "/login" in location or "/auth" in location:
                return {
                    "ok": True, 
                    "status": status,
                    "causa": "⚠️ Ruta protegida por autenticación",
                    "location": location
                }
            return {
                "ok": False,
                "status": status,
                "causa": f"⚠️ Redirección inesperada a: {location}",
                "location": location
            }
            
        if status == 404:
            return {
                "ok": False,
                "status": status,
                "causa": "❌ Ruta no encontrada en el servidor",
                "location": None
            }
            
        if status == 500:
            return {
                "ok": False,
                "status": status,
                "causa": "❌ Error interno del servidor",
                "location": None
            }

        # Otros códigos HTTP
        return {
            "ok": False,
            "status": status,
            "causa": f"❌ Código de estado no esperado: {status}",
            "location": location
        }

    except requests.exceptions.Timeout:
        return {
            "ok": False,
            "status": None,
            "causa": "⚠️ Tiempo de espera agotado",
            "location": None
        }
    except requests.exceptions.ConnectionError:
        return {
            "ok": False,
            "status": None,
            "causa": "❌ No se pudo conectar al servidor",
            "location": None
        }
    except Exception as e:
        return {
            "ok": False,
            "status": None,
            "causa": f"❌ Error inesperado: {str(e)}",
            "location": None
        }
