from flask import Blueprint, render_template, request, jsonify, abort
from datetime import datetime
import os
import requests
import random

# Importar cliente de Supabase
from clientes.aura.utils.supabase_client import supabase

try:
    from clientes.aura.utils.openai_client import generar_respuesta
except Exception:
    generar_respuesta = None

panel_cliente_contenidos_bp = Blueprint("panel_cliente_contenidos_bp", __name__, url_prefix="/panel_cliente/<nombre_nora>/contenidos")

# ==========================
#  FUNCIÓN PARA OBTENER NOMBRE_NORA
# ==========================
def get_nombre_nora():
    """Obtiene nombre_nora de forma robusta desde:
    - view_args del Blueprint
    - query string (?nombre_nora=...)
    - cabecera X-Nombre-Nora
    - body JSON {"nombre_nora": "..."}
    - ruta (segmento posterior a 'panel_cliente')
    """
    # 1) view_args del blueprint
    if hasattr(request, "view_args") and request.view_args and "nombre_nora" in request.view_args:
        return request.view_args["nombre_nora"]

    # 2) query string
    qn = request.args.get("nombre_nora") if hasattr(request, "args") else None
    if qn:
        return qn

    # 3) header explícito
    hn = request.headers.get("X-Nombre-Nora") if hasattr(request, "headers") else None
    if hn:
        return hn

    # 4) body JSON
    try:
        body = request.get_json(silent=True) or {}
        bn = body.get("nombre_nora")
        if bn:
            return bn
    except Exception:
        pass

    # 5) fallback por path: tomar el segmento que sigue a 'panel_cliente'
    try:
        parts = request.path.strip("/").split("/")
        if "panel_cliente" in parts:
            idx = parts.index("panel_cliente")
            # siguiente segmento debería ser <nombre_nora>
            if len(parts) > idx + 1:
                posible = parts[idx + 1]
                # evitar devolver 'api' o 'contenidos' si el patrón no incluye nombre
                if posible not in {"api", "contenidos"}:
                    return posible
        # sin coincidencia válida
        return None
    except Exception:
        return None

# ==========================
#  VISTAS (UI INTERNA)
# ==========================
@panel_cliente_contenidos_bp.route("/")
def vista_index_planeacion_contenido():
    nombre_nora = get_nombre_nora()
    
    # Obtener empresas para el selector
    empresas = []
    if supabase and nombre_nora:
        try:
            res = supabase.table("cliente_empresas").select("id, nombre_empresa").eq("nombre_nora", nombre_nora).order("nombre_empresa").execute()
            empresas = res.data if res.data else []
            print(f"✅ Empresas encontradas: {len(empresas)}")
        except Exception as e:
            print(f"❌ Error obteniendo empresas: {e}")
            empresas = []
    else:
        if not supabase:
            print("⚠️ Supabase no está inicializado al listar empresas en contenidos.")
        if not nombre_nora:
            print("⚠️ nombre_nora no detectado al listar empresas en contenidos.")
    
    # Obtener planeaciones reales
    planeaciones_recientes = []
    if supabase and nombre_nora:
        try:
            res = supabase.table("planeaciones_contenido").select("*").eq("nombre_nora", nombre_nora).order("created_at", desc=True).limit(5).execute()
            planeaciones_recientes = res.data if res.data else []
            print(f"📊 Planeaciones recientes encontradas: {len(planeaciones_recientes)}")
            print(f"📋 Datos planeaciones: {planeaciones_recientes}")
        except Exception as e:
            print(f"❌ Error obteniendo planeaciones: {e}")
            planeaciones_recientes = []
    else:
        if not supabase:
            print("⚠️ Supabase no está inicializado al listar planeaciones de contenidos.")
        if not nombre_nora:
            print("⚠️ nombre_nora no detectado al listar planeaciones de contenidos.")
    
    return render_template(
        "panel_cliente_contenidos/index.html",
        nombre_nora=nombre_nora,
        empresas=empresas,
        planeaciones=planeaciones_recientes
    )

@panel_cliente_contenidos_bp.route("/gestionar")
def vista_gestionar_planeaciones():
    nombre_nora = get_nombre_nora()
    return render_template(
        "panel_cliente_contenidos/gestionar.html",
        nombre_nora=nombre_nora
    )

# ==========================
#  ENDPOINTS CRUD PLANEACIÓN
# ==========================
@panel_cliente_contenidos_bp.route("/api/planeaciones", methods=["GET"])
def api_listar_planeaciones():
    """Lista todas las planeaciones para la Nora actual"""
    nombre_nora = get_nombre_nora()
    
    if not nombre_nora:
        return jsonify({"ok": False, "error": "nombre_nora requerido"}), 400
    
    try:
        # Paginación básica: limit y offset
        try:
            limit = int(request.args.get("limit", 20))
            if limit <= 0:
                limit = 20
            if limit > 100:
                limit = 100
        except Exception:
            limit = 20
        try:
            offset = int(request.args.get("offset", 0))
            if offset < 0:
                offset = 0
        except Exception:
            offset = 0

        # Para detectar has_more, pedimos limit+1 (range es inclusivo)
        start = offset
        end = offset + limit  # inclusivo, retorna hasta limit+1 registros

        query = supabase.table("planeaciones_contenido") \
            .select("*") \
            .eq("nombre_nora", nombre_nora) \
            .order("created_at", desc=True) \
            .range(start, end)

        res = query.execute()
        raw_list = res.data if res.data else []
        has_more = len(raw_list) > limit
        planeaciones = raw_list[:limit]
        
        print(f"📊 Planeaciones reales encontradas: {len(planeaciones)}")
        print(f"📋 Datos: {planeaciones}")
        
        # Agregar campos adicionales si no existen
        for planeacion in planeaciones:
            if "nombre_empresa" not in planeacion:
                planeacion["nombre_empresa"] = "Sin empresa"
            if "estado" not in planeacion:
                planeacion["estado"] = "draft"
            # Normalizar timestamp por compatibilidad en frontend
            if "created_at" not in planeacion and "fecha_creacion" in planeacion:
                planeacion["created_at"] = planeacion.get("fecha_creacion")

        return jsonify({
            "ok": True,
            "planeaciones": planeaciones,
            "has_more": has_more,
            "limit": limit,
            "offset": offset
        }), 200
    except Exception as e:
        print(f"❌ Error en api_listar_planeaciones: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@panel_cliente_contenidos_bp.route("/api/empresas", methods=["GET"])
def api_listar_empresas():
    """Lista todas las empresas cliente para la Nora actual"""
    nombre_nora = get_nombre_nora()
    
    if not nombre_nora:
        return jsonify({"ok": False, "error": "nombre_nora requerido"}), 400
    
    try:
        res = supabase.table("cliente_empresas") \
            .select("id, nombre_empresa") \
            .eq("nombre_nora", nombre_nora) \
            .order("nombre_empresa") \
            .execute()
        
        empresas = res.data if res.data else []
        
        print(f"🏢 Empresas reales encontradas: {len(empresas)}")
        print(f"📋 Datos empresas: {empresas}")
        
        return jsonify({"ok": True, "empresas": empresas}), 200
    except Exception as e:
        print(f"❌ Error en api_listar_empresas: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@panel_cliente_contenidos_bp.route("/api/planeaciones", methods=["POST"])
def api_crear_planeacion():
    nombre_nora = get_nombre_nora()
    data = request.get_json(silent=True) or {}
    
    if not nombre_nora:
        return jsonify({"ok": False, "error": "nombre_nora requerido en ruta, query, header o body"}), 400
    if not data.get("empresa_id") or not data.get("titulo"):
        return jsonify({"ok": False, "error": "Faltan campos: empresa_id, titulo"}), 400
    
    try:
        # Insertar en planeaciones_contenido
        insert_data = {
            "nombre_nora": nombre_nora,
            "empresa_id": data["empresa_id"],
            "titulo": data["titulo"],
            "objetivo": data.get("objetivo", "awareness"),
            "fecha_grabacion": data.get("fecha_grabacion"),
            "hora_inicio": data.get("hora_inicio"),
            "duracion_estimada_min": data.get("duracion_estimada_min"),
            "num_contenidos": data.get("num_contenidos", 5),
            "preproduccion": data.get("preproduccion"),
            "logistica": data.get("logistica"),
            "postproduccion": data.get("postproduccion")
        }

        if not supabase:
            raise RuntimeError("Supabase no está inicializado")

        res = supabase.table("planeaciones_contenido").insert(insert_data).execute()
        planeacion = res.data[0] if res.data else insert_data

        print(f"✅ Planeación creada: {planeacion.get('titulo')}")

        return jsonify({"ok": True, "planeacion": planeacion}), 200
    except Exception as e:
        print(f"❌ Error creando planeación: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@panel_cliente_contenidos_bp.route("/api/planeaciones/<planeacion_id>", methods=["GET"])
def api_detalle_planeacion(planeacion_id):
    try:
        res = supabase.table("planeaciones_contenido") \
            .select("*") \
            .eq("id", planeacion_id) \
            .single() \
            .execute()
        
        planeacion = res.data if res.data else None
        
        if not planeacion:
            return jsonify({"ok": False, "error": "Planeación no encontrada"}), 404
            
        return jsonify({"ok": True, "planeacion": planeacion}), 200
    except Exception as e:
        print(f"❌ Error obteniendo planeación: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@panel_cliente_contenidos_bp.route("/api/planeaciones/<planeacion_id>", methods=["PATCH"])
def api_actualizar_planeacion(planeacion_id):
    data = request.get_json(silent=True) or {}
    try:
        res = supabase.table("planeaciones_contenido").update(data).eq("id", planeacion_id).execute()
        return jsonify({"ok": True, "planeacion_id": planeacion_id, "changes": data}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@panel_cliente_contenidos_bp.route("/api/planeaciones/<planeacion_id>", methods=["DELETE"])
def api_eliminar_planeacion(planeacion_id):
    try:
        supabase.table("planeaciones_contenido").delete().eq("id", planeacion_id).execute()
        return jsonify({"ok": True, "planeacion_id": planeacion_id}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
# ==========================
#  ENDPOINTS CRUD PRODUCCION
# ==========================
@panel_cliente_contenidos_bp.route("/api/planeaciones/<planeacion_id>/produccion", methods=["POST"])
def api_crear_produccion(planeacion_id):
    data = request.get_json(silent=True) or {}
    try:
        insert_data = {"planeacion_id": planeacion_id, **data, "created_at": datetime.utcnow().isoformat()}
        res = supabase.table("planeaciones_produccion").insert(insert_data).execute()
        return jsonify({"ok": True, "produccion": res.data[0] if res.data else insert_data}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@panel_cliente_contenidos_bp.route("/api/produccion/<produccion_id>", methods=["PATCH"])
def api_actualizar_produccion(produccion_id):
    data = request.get_json(silent=True) or {}
    try:
        res = supabase.table("planeaciones_produccion").update(data).eq("id", produccion_id).execute()
        return jsonify({"ok": True, "produccion_id": produccion_id, "changes": data}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@panel_cliente_contenidos_bp.route("/api/produccion/<produccion_id>", methods=["DELETE"])
def api_eliminar_produccion(produccion_id):
    try:
        supabase.table("planeaciones_produccion").delete().eq("id", produccion_id).execute()
        return jsonify({"ok": True, "produccion_id": produccion_id}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
# ==========================
#  ENDPOINTS CRUD POSTPRODUCCION
# ==========================
@panel_cliente_contenidos_bp.route("/api/planeaciones/<planeacion_id>/postproduccion", methods=["POST"])
def api_crear_postproduccion(planeacion_id):
    data = request.get_json(silent=True) or {}
    try:
        insert_data = {"planeacion_id": planeacion_id, **data, "created_at": datetime.utcnow().isoformat()}
        res = supabase.table("planeaciones_postproduccion").insert(insert_data).execute()
        return jsonify({"ok": True, "postproduccion": res.data[0] if res.data else insert_data}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@panel_cliente_contenidos_bp.route("/api/postproduccion/<postproduccion_id>", methods=["PATCH"])
def api_actualizar_postproduccion(postproduccion_id):
    data = request.get_json(silent=True) or {}
    try:
        res = supabase.table("planeaciones_postproduccion").update(data).eq("id", postproduccion_id).execute()
        return jsonify({"ok": True, "postproduccion_id": postproduccion_id, "changes": data}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@panel_cliente_contenidos_bp.route("/api/postproduccion/<postproduccion_id>", methods=["DELETE"])
def api_eliminar_postproduccion(postproduccion_id):
    try:
        supabase.table("planeaciones_postproduccion").delete().eq("id", postproduccion_id).execute()
        return jsonify({"ok": True, "postproduccion_id": postproduccion_id}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
# ==========================
#  ENDPOINTS CRUD TEMAS
# ==========================
@panel_cliente_contenidos_bp.route("/api/planeaciones/<planeacion_id>/temas", methods=["POST"])
def api_crear_tema(planeacion_id):
    data = request.get_json(silent=True) or {}
    try:
        insert_data = {"planeacion_id": planeacion_id, **data, "created_at": datetime.utcnow().isoformat()}
        res = supabase.table("planeaciones_temas").insert(insert_data).execute()
        return jsonify({"ok": True, "tema": res.data[0] if res.data else insert_data}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@panel_cliente_contenidos_bp.route("/api/temas/<tema_id>", methods=["PATCH"])
def api_actualizar_tema(tema_id):
    data = request.get_json(silent=True) or {}
    try:
        res = supabase.table("planeaciones_temas").update(data).eq("id", tema_id).execute()
        return jsonify({"ok": True, "tema_id": tema_id, "changes": data}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@panel_cliente_contenidos_bp.route("/api/temas/<tema_id>", methods=["DELETE"])
def api_eliminar_tema(tema_id):
    try:
        supabase.table("planeaciones_temas").delete().eq("id", tema_id).execute()
        return jsonify({"ok": True, "tema_id": tema_id}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ==========================
#  ENDPOINTS CRUD CLIPS
# ==========================
@panel_cliente_contenidos_bp.route("/api/planeaciones/<planeacion_id>/clips", methods=["POST"])
def api_crear_clip(planeacion_id):
    data = request.get_json(silent=True) or {}
    if data.get("orden") is None or not data.get("tipo"):
        return jsonify({"ok": False, "error": "Faltan campos: orden, tipo"}), 400
    clip = {
        "id": f"clip_{int(datetime.utcnow().timestamp())}",
        "planeacion_id": planeacion_id,
        **data
    }
    return jsonify({"ok": True, "clip": clip}), 200

@panel_cliente_contenidos_bp.route("/api/clips/<clip_id>", methods=["PATCH"])
def api_actualizar_clip(clip_id):
    data = request.get_json(silent=True) or {}
    return jsonify({"ok": True, "clip_id": clip_id, "changes": data}), 200

@panel_cliente_contenidos_bp.route("/api/clips/<clip_id>", methods=["DELETE"])
def api_eliminar_clip(clip_id):
    return jsonify({"ok": True, "clip_id": clip_id}), 200

# ==========================
#  SHARING POR LINK
# ==========================
@panel_cliente_contenidos_bp.route("/compartir/<token>", methods=["GET"])
def vista_compartida(token):
    if not token:
        abort(404)
    return render_template("panel_cliente_contenidos/compartido.html", token=token)

# ==========================
#  HOOKS DE IA (placeholders)
# ==========================
@panel_cliente_contenidos_bp.route("/api/ia/preproduccion/sugerir", methods=["POST"])
def ia_sugerir_preproduccion():
    data = request.get_json(silent=True) or {}
    sugerencia = {
        "premisa": f"Idea base para {data.get('tema','tu tema')}",
        "entorno": "Set interior luminoso, micro de solapa",
        "formato": data.get("formato_preferido", "educativo")
    }
    return jsonify({"ok": True, "sugerencia": sugerencia}), 200

@panel_cliente_contenidos_bp.route("/api/ia/preproduccion/analizar", methods=["POST"])
def ia_analizar_brief():
    """Analiza un brief de preproducción usando datos de la empresa seleccionada.
    Para esta fase, usamos 'ubicación del contenido' (Instagram Reels o TikTok) y no usamos público objetivo.
    Espera JSON: { empresa_id, objetivo?, ideas_principales?, referencias?, ubicacion? }
    """
    nombre_nora = get_nombre_nora()
    data = request.get_json(silent=True) or {}
    empresa_id = data.get("empresa_id")
    if not nombre_nora:
        return jsonify({"ok": False, "error": "nombre_nora requerido"}), 400
    if not empresa_id:
        return jsonify({"ok": False, "error": "empresa_id requerido"}), 400

    try:
        # Validar empresa pertenezca a la Nora y obtener más contexto (giro/industria/sitio_web si existen)
        empresa = None
        if supabase:
            eres = (
                supabase.table("cliente_empresas")
                .select("*")
                .eq("id", empresa_id)
                .eq("nombre_nora", nombre_nora)
                .single()
                .execute()
            )
            empresa = eres.data if eres and eres.data else None
        if not empresa:
            return jsonify({"ok": False, "error": "Empresa no encontrada para esta Nora"}), 404

        objetivo = (data.get("objetivo") or "").strip()
        ideas = (data.get("ideas_principales") or "").strip()
        referencias = (data.get("referencias") or "").strip()
        ubicacion = (data.get("ubicacion") or "").strip().lower()

        # Para esta fase, mapeamos ubicaciones soportadas
        def label_ubicacion(code: str) -> str:
            mapping = {
                "reel": "Instagram Reels",
                "instagram_reels": "Instagram Reels",
                "tiktok": "TikTok",
            }
            return mapping.get(code, "Reel/TikTok")

        nombre_empresa = empresa.get("nombre_empresa") or "tu marca"
        # Inferir industria/giro desde campos comunes si existen
        industria = (
            (empresa.get("giro") or "").strip()
            or (empresa.get("industria") or "").strip()
            or (empresa.get("categoria") or "").strip()
        )
        ubic_label = label_ubicacion(ubicacion)
        objetivo_txt = objetivo if objetivo else f"{nombre_empresa}"

        # Normalizar ideas de usuario como semillas
        base_ideas = [s.strip(" -•\t") for s in ideas.split("\n") if s.strip()] if ideas else []

        # Generador simple de temas por industria + ubicación
        def generar_temas(ind: str, empresa_nombre: str, ubic: str, semillas: list[str]):
            ind_label = ind or "tu industria"
            seeds = semillas[:5]
            temas_loc = []
            idx = 1
            # Semillas del usuario primero
            for idea in seeds:
                titulo = f"{ubic}: {idea[:80]}"
                desc = f"Idea basada en tu brief para {empresa_nombre}."
                temas_loc.append({"id": idx, "titulo": titulo, "descripcion": desc})
                idx += 1
            # Plantillas por industria (genéricas si no hay)
            patrones = [
                (f"{ubic}: 5 tips de {ind_label} que tus clientes agradecen", "Consejos accionables y cortos."),
                (f"{ubic}: Errores comunes en {ind_label} y cómo evitarlos", "Educativo con soluciones claras."),
                (f"{ubic}: Detrás de cámaras en {empresa_nombre}", "Proceso, equipo y herramientas."),
                (f"{ubic}: Caso real: antes y después en {ind_label}", "Transformación visual con CTA."),
                (f"{ubic}: Mitos vs realidades sobre {ind_label}", "Desmentir creencias en 3 puntos."),
                (f"{ubic}: FAQ: 3 preguntas frecuentes de clientes", "Responde dudas habituales en 15s."),
                (f"{ubic}: Trend + {ind_label}", "Suma un audio/tendencia adaptado a tu giro."),
                (f"{ubic}: Testimonio breve de cliente", "Historia real con resultado concreto."),
                (f"{ubic}: Checklist express para {ind_label}", "3-5 puntos a revisar antes de comprar/contratar."),
            ]
            for tit, desc in patrones:
                temas_loc.append({"id": idx, "titulo": tit, "descripcion": desc})
                idx += 1
            return temas_loc[:10]

        temas = generar_temas(industria, nombre_empresa, ubic_label, base_ideas)

        # Responder solo con temas (mantener compatibilidad: analisis.temas)
        analisis = {"temas": temas}

        return jsonify(
            {
                "ok": True,
                "empresa": {"id": empresa["id"], "nombre_empresa": empresa.get("nombre_empresa")},
                "analisis": analisis,
                "temas": temas,
            }
        ), 200
    except Exception as e:
        print(f"❌ Error analizando brief: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@panel_cliente_contenidos_bp.route("/api/ia/estructura/generar", methods=["POST"])
def ia_generar_estructura():
    data = request.get_json(silent=True) or {}
    estructura = [
        {"orden":1,"tipo":"gancho","guion":"Hook potente..."},
        {"orden":2,"tipo":"desarrollo","guion":"Punto clave 1..."},
        {"orden":3,"tipo":"desarrollo","guion":"Punto clave 2..."},
        {"orden":4,"tipo":"remate","guion":"Cierre contundente..."},
        {"orden":5,"tipo":"cta","guion":"CTA claro..."}
    ]
    return jsonify({"ok": True, "estructura": estructura}), 200

@panel_cliente_contenidos_bp.route("/api/ia/checklist/post", methods=["POST"])
def ia_checklist_post():
    data = request.get_json(silent=True) or {}
    checklist = {
        "carpetas": ["01_raw","02_seleccion","03_sonido","04_color","05_export"],
        "nomenclatura": "NORA-<EMPRESA>-<FECHA>-C<ORDEN>-<TIPO>.mp4",
        "marcaje": data.get("flujo","claqueta"),
        "extras": ["respaldo_duro_externo","verificar_espacio","baterias_cargadas"]
    }
    return jsonify({"ok": True, "checklist": checklist}), 200

# ==========================
#  IA: GENERAR BRIEF POR EMPRESA
# ==========================
@panel_cliente_contenidos_bp.route("/api/generar-brief/<empresa_id>", methods=["POST"])
def api_generar_brief(empresa_id):
    """Genera temas/brief a partir de la empresa seleccionada.
    Respuesta esperada por el frontend: { success: True, temas: [{id,titulo,descripcion}, ...] }
    """
    try:
        nombre_nora = get_nombre_nora()
        if not supabase:
            return jsonify({"success": False, "error": "Supabase no disponible"}), 500
        if not nombre_nora:
            return jsonify({"success": False, "error": "nombre_nora requerido"}), 400

        # Buscar empresa y validar pertenencia a la Nora
        res_emp = supabase.table("cliente_empresas") \
            .select("id, nombre_empresa") \
            .eq("id", empresa_id) \
            .eq("nombre_nora", nombre_nora) \
            .single() \
            .execute()
        empresa = res_emp.data if res_emp and res_emp.data else None
        if not empresa:
            return jsonify({"success": False, "error": "Empresa no encontrada o no pertenece a esta Nora"}), 404

        nombre_empresa = empresa.get("nombre_empresa", "Tu Empresa")

        # Generar temas (placeholder); se puede integrar IA más adelante
        base_ts = int(datetime.utcnow().timestamp())
        temas = [
            {"id": f"t{base_ts}1", "titulo": f"3 ideas de contenido para {nombre_empresa} esta semana", "descripcion": "Calendario editorial con enfoques de valor, promo y comunidad."},
            {"id": f"t{base_ts}2", "titulo": f"Problemas comunes de clientes de {nombre_empresa}", "descripcion": "Guiones cortos resolviendo dudas frecuentes y objeciones."},
            {"id": f"t{base_ts}3", "titulo": f"Detrás de cámaras en {nombre_empresa}", "descripcion": "Mostrar proceso, equipo y valores para generar confianza."},
            {"id": f"t{base_ts}4", "titulo": f"Caso de éxito real de {nombre_empresa}", "descripcion": "Estructura: reto → solución → resultado → CTA."},
            {"id": f"t{base_ts}5", "titulo": f"Cómo elegir el mejor servicio/producto de {nombre_empresa}", "descripcion": "Checklist breve y comparativas claras."}
        ]

        return jsonify({"success": True, "temas": temas, "empresa": {"id": empresa_id, "nombre": nombre_empresa}}), 200
    except Exception as e:
        print(f"❌ Error generando brief: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
