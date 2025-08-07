from flask import Blueprint, request, jsonify, g
from clientes.aura.utils.supabase_client import supabase

webhooks_api_bp = Blueprint(
    "webhooks_api_bp",
    __name__,
    url_prefix="/api/webhooks"
)

@webhooks_api_bp.route("/logs")
def api_logs_webhook(nombre_nora):
    try:
        registros = supabase.table("logs_webhooks_meta") \
            .select("*") \
            .order("timestamp", desc=True) \
            .limit(50) \
            .execute()
        return jsonify({'success': True, 'logs': registros.data or []})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@webhooks_api_bp.route("/publicaciones")
def api_publicaciones_webhook(nombre_nora):
    try:
        print(f"🔍 DEBUG: Llamada a /publicaciones para {nombre_nora}")
        
        # Obtener parámetros de filtrado y paginación
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        page_filter = request.args.get('page_id', '')
        date_filter = request.args.get('date', '')  # Formato: YYYY-MM-DD
        
        print(f"🔍 DEBUG: Parámetros - page: {page}, limit: {limit}, page_filter: {page_filter}, date_filter: {date_filter}")
        
        offset = (page - 1) * limit
        
        # Construir consulta base (sin JOIN debido a falta de relación FK)
        print("🔍 DEBUG: Construyendo consulta base...")
        query = supabase.table("meta_publicaciones_webhook") \
            .select("*") \
            .not_.in_("tipo_item", ["reaction", "comment", "like", "love", "wow", "haha", "sad", "angry"])
        
        # Aplicar filtros
        if page_filter:
            print(f"🔍 DEBUG: Aplicando filtro de página: {page_filter}")
            query = query.eq("page_id", page_filter)
            
        if date_filter:
            print(f"🔍 DEBUG: Aplicando filtro de fecha: {date_filter}")
            # Filtrar por día específico
            start_date = f"{date_filter} 00:00:00"
            end_date = f"{date_filter} 23:59:59"
            query = query.gte("creada_en", start_date).lte("creada_en", end_date)
        
        print("🔍 DEBUG: Ejecutando consulta...")
        # Aplicar paginación y ordenamiento
        response = query.order("created_time", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        print(f"🔍 DEBUG: Respuesta obtenida: {len(response.data or [])} registros")
        
        # Obtener nombres de páginas por separado
        print("🔍 DEBUG: Obteniendo nombres de páginas...")
        paginas_response = supabase.table("facebook_paginas") \
            .select("page_id, nombre_pagina") \
            .execute()
        
        # Crear diccionario de page_id -> nombre_pagina
        paginas_dict = {p['page_id']: p['nombre_pagina'] for p in paginas_response.data or []}
        print(f"🔍 DEBUG: Diccionario de páginas creado con {len(paginas_dict)} entradas")
        
        # Procesar los datos y agregar nombres de páginas
        data = []
        for pub in response.data or []:
            item = dict(pub)
            page_id = pub.get('page_id', '')
            item['nombre_pagina'] = paginas_dict.get(page_id, page_id)
            data.append(item)
        
        print(f"🔍 DEBUG: Datos procesados: {len(data)} registros")
        
        # Información de paginación
        total_count = len(data) if not hasattr(response, 'count') else response.count or 0
        total_pages = max(1, (total_count + limit - 1) // limit)
        
        result = {
            'success': True, 
            'publicaciones': data,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_count': total_count,
                'limit': limit,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
        
        print("🔍 DEBUG: Enviando respuesta exitosa")
        return jsonify(result)
    except Exception as e:
        print(f"❌ ERROR en api_publicaciones_webhook: {str(e)}")
        print(f"❌ ERROR tipo: {type(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e), 'error_type': str(type(e))}), 500


@webhooks_api_bp.route("/anuncios")
def api_anuncios_webhook(nombre_nora):
    try:
        print(f"🔍 DEBUG: Llamada a /anuncios para {nombre_nora}")
        
        print("🔍 DEBUG: Ejecutando consulta de anuncios...")
        anuncios = supabase.table("meta_anuncios_automatizados") \
            .select("*") \
            .order("creado_en", desc=True) \
            .limit(50) \
            .execute()
        
        print(f"🔍 DEBUG: Respuesta de anuncios obtenida: {len(anuncios.data or [])} registros")
        
        result = {'success': True, 'anuncios': anuncios.data or []}
        
        print("🔍 DEBUG: Enviando respuesta exitosa para anuncios")
        return jsonify(result)
    except Exception as e:
        print(f"❌ ERROR en api_anuncios_webhook: {str(e)}")
        print(f"❌ ERROR tipo: {type(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e), 'error_type': str(type(e))}), 500


@webhooks_api_bp.route("/comentarios")
def api_comentarios_webhook(nombre_nora):
    try:
        print(f"🔍 DEBUG: Llamada a /comentarios para {nombre_nora}")
        
        # Obtener parámetros de filtrado y paginación
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        page_filter = request.args.get('page_id', '')
        date_filter = request.args.get('date', '')  # Formato: YYYY-MM-DD
        
        print(f"🔍 DEBUG: Parámetros - page: {page}, limit: {limit}, page_filter: {page_filter}, date_filter: {date_filter}")
        
        offset = (page - 1) * limit
        
        # Construir consulta base (sin JOIN debido a falta de relación FK)
        print("🔍 DEBUG: Construyendo consulta base para comentarios...")
        query = supabase.table("meta_publicaciones_webhook") \
            .select("*") \
            .eq("tipo_item", "comment")
        
        # Aplicar filtros
        if page_filter:
            print(f"🔍 DEBUG: Aplicando filtro de página: {page_filter}")
            query = query.eq("page_id", page_filter)
            
        if date_filter:
            print(f"🔍 DEBUG: Aplicando filtro de fecha: {date_filter}")
            # Filtrar por día específico
            start_date = f"{date_filter} 00:00:00"
            end_date = f"{date_filter} 23:59:59"
            query = query.gte("creada_en", start_date).lte("creada_en", end_date)
        
        print("🔍 DEBUG: Ejecutando consulta de comentarios...")
        # Aplicar paginación y ordenamiento
        response = query.order("created_time", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        print(f"🔍 DEBUG: Respuesta obtenida: {len(response.data or [])} registros")
        
        # Obtener nombres de páginas por separado
        print("🔍 DEBUG: Obteniendo nombres de páginas...")
        paginas_response = supabase.table("facebook_paginas") \
            .select("page_id, nombre_pagina") \
            .execute()
        
        # Crear diccionario de page_id -> nombre_pagina
        paginas_dict = {p['page_id']: p['nombre_pagina'] for p in paginas_response.data or []}
        print(f"🔍 DEBUG: Diccionario de páginas creado con {len(paginas_dict)} entradas")
        
        # Procesar los datos y agregar nombres de páginas
        data = []
        for com in response.data or []:
            item = dict(com)
            page_id = com.get('page_id', '')
            item['nombre_pagina'] = paginas_dict.get(page_id, page_id)
            data.append(item)
        
        print(f"🔍 DEBUG: Datos procesados: {len(data)} registros")
        
        # Información de paginación
        total_count = len(data) if not hasattr(response, 'count') else response.count or 0
        total_pages = max(1, (total_count + limit - 1) // limit)
        
        result = {
            'success': True, 
            'comentarios': data,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_count': total_count,
                'limit': limit,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
        
        print("🔍 DEBUG: Enviando respuesta exitosa para comentarios")
        return jsonify(result)
    except Exception as e:
        print(f"❌ ERROR en api_comentarios_webhook: {str(e)}")
        print(f"❌ ERROR tipo: {type(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e), 'error_type': str(type(e))}), 500


@webhooks_api_bp.route("/paginas")
def api_paginas_webhook(nombre_nora):
    try:
        print(f"🔍 DEBUG: Llamada a /paginas para {nombre_nora}")
        
        print("🔍 DEBUG: Ejecutando consulta de páginas...")
        # Obtener lista de páginas para el filtro
        paginas = supabase.table("facebook_paginas") \
            .select("page_id, nombre_pagina") \
            .eq("activa", True) \
            .order("nombre_pagina") \
            .execute()
        
        print(f"🔍 DEBUG: Respuesta de páginas obtenida: {len(paginas.data or [])} registros")
        
        result = {'success': True, 'paginas': paginas.data or []}
        
        print("🔍 DEBUG: Enviando respuesta exitosa para páginas")
        return jsonify(result)
    except Exception as e:
        print(f"❌ ERROR en api_paginas_webhook: {str(e)}")
        print(f"❌ ERROR tipo: {type(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e), 'error_type': str(type(e))}), 500