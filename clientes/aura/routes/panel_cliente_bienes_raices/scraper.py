# ✅ Archivo: clientes/aura/routes/panel_cliente_bienes_raices/scraper.py
# 👉 Scraper simple por selector CSS (pluggable); ejecutable bajo demanda
from flask import Blueprint, request, jsonify
from clientes.aura.utils.supabase_client import supabase
from .crud import TABLE_PROPIEDADES
from datetime import datetime

br_scraper_bp = Blueprint("br_scraper_bp", __name__)

try:
    import requests
    from bs4 import BeautifulSoup
    _SCRAPER_OK = True
except Exception:
    _SCRAPER_OK = False

@br_scraper_bp.route("/ejecutar", methods=["POST"])
def ejecutar_scraper(nombre_nora):
    """
    Body esperado:
    {
      "fuentes": [
        {"url":"https://ejemplo.site/listado", "item":".card", "titulo":".t", "precio":".p", "direccion":".d", "link":"a::attr(href)"}
      ],
      "operacion": "venta|renta",
      "ciudad": "Hermosillo",
      "etiqueta": "scrape",
      "limite_por_fuente": 30
    }
    """
    if not _SCRAPER_OK:
        return jsonify({"success": False, "message": "Instala requests y beautifulsoup4 para usar el scraper"}), 400

    body = request.get_json(silent=True) or {}
    fuentes = body.get("fuentes") or []
    if not fuentes:
        return jsonify({"success": False, "message": "Define al menos una fuente con selectores CSS"}), 400

    inserciones = []
    for f in fuentes:
        try:
            html = requests.get(f["url"], timeout=20).text
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select(f.get("item", ""))[: int(body.get("limite_por_fuente", 30))]
            for c in cards:
                def sel_text(sel):
                    return (c.select_one(sel).get_text(strip=True) if sel and c.select_one(sel) else None)
                titulo = sel_text(f.get("titulo"))
                precio_txt = sel_text(f.get("precio"))
                direccion = sel_text(f.get("direccion"))
                precio = _parse_precio(precio_txt)
                if not titulo:
                    continue
                inserciones.append({
                    "titulo": titulo,
                    "descripcion": None,
                    "operacion": body.get("operacion"),
                    "precio": precio,
                    "recamaras": None,
                    "banos": None,
                    "ciudad": body.get("ciudad"),
                    "etiqueta": body.get("etiqueta", "scrape"),
                    "direccion": direccion,
                    "lat": None,
                    "lng": None,
                    "estatus": "borrador",
                    "creado_en": datetime.utcnow().isoformat(),
                    "nombre_nora": nombre_nora,
                    "origen_url": f.get("url")
                })
        except Exception:
            continue

    if not inserciones:
        return jsonify({"success": True, "insertadas": 0, "items": []})

    try:
        sb = supabase
        # 0 Ideal: deduplicar por (titulo+direccion+precio) o hash antes de insertar
        res = sb.table(TABLE_PROPIEDADES).insert(inserciones).execute()
        return jsonify({"success": True, "insertadas": len(res.data or [])})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def _parse_precio(txt):
    if not txt:
        return None
    try:
        # Quita símbolos y comas
        dig = "".join(ch for ch in txt if ch.isdigit() or ch == ".")
        return float(dig) if dig else None
    except Exception:
        return None
