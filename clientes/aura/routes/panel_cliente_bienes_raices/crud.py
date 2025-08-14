# ✅ Archivo: clientes/aura/routes/panel_cliente_bienes_raices/crud.py
# 👉 Lógica de catálogo, filtros, alta/edición y datos para mapa (Supabase)
from flask import Blueprint, request, jsonify
from datetime import datetime
from clientes.aura.utils.supabase_client import supabase  # ⚠️ Usa el cliente real
import math

# ⚠️ Necesito confirmar nombres de tablas/columnas. Pásame tu schema para ajustar filtros.
TABLE_PROPIEDADES = "bienes_raices_propiedades"            # id, titulo, descripcion, operacion, precio, recamaras, banos, ciudad, etiqueta, direccion, lat, lng, estatus, creado_en
TABLE_MEDIA = "bienes_raices_propiedades_media"            # id, propiedad_id, url, tipo
TABLE_SOCIAL_QUEUE = "social_publicaciones_pendientes"     # id, propiedad_id, plataformas[], estado, payload

br_crud_bp = Blueprint("br_crud_bp", __name__)

def _sb():
    return supabase

def _base_query(nombre_nora):
    # Si usas multi‑tenant por columna, agrega .eq("nombre_nora", nombre_nora)
    return _sb().table(TABLE_PROPIEDADES).select("*")

def _aplicar_filtros(q, filtros: dict):
    if not filtros:
        return q
    if filtros.get("operacion"):
        q = q.eq("operacion", filtros["operacion"])
    if filtros.get("ciudad"):
        q = q.ilike("ciudad", f"%{filtros['ciudad']}%")
    if filtros.get("precio_min") is not None:
        q = q.gte("precio", filtros["precio_min"])
    if filtros.get("precio_max") is not None:
        q = q.lte("precio", filtros["precio_max"])
    if filtros.get("recamaras") is not None:
        q = q.gte("recamaras", filtros["recamaras"])
    if filtros.get("banos") is not None:
        q = q.gte("banos", filtros["banos"])
    if filtros.get("etiqueta"):
        q = q.ilike("etiqueta", f"%{filtros['etiqueta']}%")
    if filtros.get("texto"):
        # Búsqueda simple en título/dirección/desc (ajusta a tu FT index si tienes)
        q = q.or_(f"titulo.ilike.%{filtros['texto']}%,direccion.ilike.%{filtros['texto']}%,descripcion.ilike.%{filtros['texto']}%")
    # Solo publicadas si tu schema lo maneja
    if filtros.get("solo_publicadas", True):
        try:
            q = q.eq("estatus", "publicada")
        except Exception:
            pass
    return q

@br_crud_bp.route("/propiedades", methods=["GET"])
def listar_propiedades(nombre_nora):
    filtros = {
        "operacion": request.args.get("operacion"),
        "precio_min": request.args.get("precio_min", type=float),
        "precio_max": request.args.get("precio_max", type=float),
        "recamaras": request.args.get("recamaras", type=int),
        "banos": request.args.get("banos", type=int),
        "ciudad": request.args.get("ciudad"),
        "etiqueta": request.args.get("etiqueta"),
        "texto": request.args.get("q"),
        "solo_publicadas": request.args.get("solo_publicadas", default="true").lower() != "false"
    }
    page = max(request.args.get("page", default=1, type=int), 1)
    size = min(max(request.args.get("size", default=20, type=int), 1), 100)

    try:
        q = _aplicar_filtros(_base_query(nombre_nora), filtros)
        # Paginado simple por rango
        start = (page - 1) * size
        end = start + size - 1
        res = q.range(start, end).order("creado_en", desc=True).execute()
        items = res.data or []

        # Conteo aproximado (si no tienes RPC count)
        total = len(items)
        has_more = len(items) == size

        return jsonify({"success": True, "items": items, "page": page, "size": size, "has_more": has_more, "approx_total": total})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@br_crud_bp.route("/panel_cliente/<nombre_nora>/bienes_raices/propiedades", methods=["POST"])
def crear_propiedad(nombre_nora):
    payload = request.get_json(silent=True) or {}
    requerido = ["titulo", "operacion", "precio", "direccion"]
    faltan = [c for c in requerido if payload.get(c) in (None, "", [])]
    if faltan:
        return jsonify({"success": False, "message": f"Faltan campos: {', '.join(faltan)}"}), 400

    # Normaliza
    nuevo = {
        "titulo": payload.get("titulo").strip(),
        "descripcion": (payload.get("descripcion") or "").strip(),
        "operacion": payload.get("operacion"),  # venta|renta
        "precio": float(payload.get("precio")),
        "recamaras": payload.get("recamaras"),
        "banos": payload.get("banos"),
        "ciudad": payload.get("ciudad"),
        "etiqueta": payload.get("etiqueta"),
        "direccion": payload.get("direccion"),
        "lat": payload.get("lat"),
        "lng": payload.get("lng"),
        "estatus": payload.get("estatus", "borrador"),
        "creado_en": datetime.utcnow().isoformat(),
        "nombre_nora": nombre_nora  # si tu schema lo usa
    }

    try:
        ins = _sb().table(TABLE_PROPIEDADES).insert(nuevo).execute()
        prop = (ins.data or [None])[0]
        if not prop:
            return jsonify({"success": False, "message": "No se pudo insertar"}), 500

        # Media opcional
        media = payload.get("media") or []
        if media:
            registros = [{"propiedad_id": prop["id"], "url": m.get("url"), "tipo": m.get("tipo", "imagen")} for m in media if m.get("url")]
            if registros:
                _sb().table(TABLE_MEDIA).insert(registros).execute()

        # ¿Publicar en redes?
        if payload.get("publicar_en_redes"):
            try:
                _sb().table(TABLE_SOCIAL_QUEUE).insert({
                    "propiedad_id": prop["id"],
                    "plataformas": payload.get("plataformas", ["facebook", "instagram"]),
                    "estado": "pendiente",
                    "payload": {
                        "copy": generar_copy_social(prop),  # función abajo
                        "imagenes": [m["url"] for m in media if m.get("url")]
                    }
                }).execute()
            except Exception:
                pass

        return jsonify({"success": True, "id": prop["id"], "item": prop}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def generar_copy_social(prop: dict) -> str:
    # Texto simple; puedes moverlo a social.py si prefieres
    partes = [
        f"🏠 {prop.get('titulo','Propiedad')}",
        f"• Operación: {prop.get('operacion','')}",
        f"• Precio: ${int(prop.get('precio',0)):,}",
    ]
    if prop.get("ciudad"): partes.append(f"• Ciudad: {prop['ciudad']}")
    if prop.get("recamaras"): partes.append(f"• Recámaras: {prop['recamaras']}")
    if prop.get("banos"): partes.append(f"• Baños: {prop['banos']}")
    if prop.get("direccion"): partes.append(f"• Ubicación: {prop['direccion']}")
    partes.append("ℹ️ Más info por DM o en el catálogo.")
    return "\n".join(partes)

def get_geojson_propiedades(nombre_nora, filtros: dict):
    try:
        q = _aplicar_filtros(_base_query(nombre_nora), filtros or {})
        q = q.not_.is_("lat", "null").not_.is_("lng", "null")
        res = q.limit(500).execute()
        feats = []
        for p in (res.data or []):
            try:
                lat, lng = float(p["lat"]), float(p["lng"])
            except Exception:
                continue
            feats.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lng, lat]},
                "properties": {
                    "id": p["id"],
                    "titulo": p.get("titulo"),
                    "precio": p.get("precio"),
                    "operacion": p.get("operacion"),
                    "direccion": p.get("direccion")
                }
            })
        return {"type": "FeatureCollection", "features": feats}
    except Exception as e:
        return {"type": "FeatureCollection", "features": [], "error": str(e)}
