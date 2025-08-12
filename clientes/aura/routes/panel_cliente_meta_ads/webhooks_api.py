from flask import Blueprint, request, jsonify, g
from clientes.aura.utils.supabase_client import supabase

webhooks_api_bp = Blueprint(
    "webhooks_api_bp",
    __name__,
    url_prefix="/api/webhooks"
)

def obtener_token_pagina(page_id):
    """
    Obtiene el token de acceso específico de una página desde la base de datos.
    
    Args:
        page_id (str): ID de la página de Facebook
        
    Returns:
        str: Token de acceso de la página o None si no se encuentra
    """
    try:
        print(f"🔍 DEBUG: Obteniendo token para página {page_id}")
        
        response = supabase.table("facebook_paginas") \
            .select("access_token, nombre_pagina, access_token_valido") \
            .eq("page_id", page_id) \
            .eq("activa", True) \
            .single() \
            .execute()
        
        if response.data:
            token_valido = response.data.get('access_token_valido', True)
            if not token_valido:
                print(f"⚠️ WARNING: Token marcado como inválido para página {page_id}")
                return None
            
            token = response.data.get('access_token')
            nombre_pagina = response.data.get('nombre_pagina', 'Desconocida')
            
            if token:
                print(f"✅ Token encontrado para página '{nombre_pagina}' ({page_id})")
                return token
            else:
                print(f"❌ No hay token guardado para página '{nombre_pagina}' ({page_id})")
                return None
        else:
            print(f"❌ Página {page_id} no encontrada en base de datos")
            return None
            
    except Exception as e:
        print(f"❌ ERROR obteniendo token para página {page_id}: {str(e)}")
        return None

def actualizar_estado_token_pagina(page_id, es_valido=True):
    """
    Actualiza el estado de validez del token de una página.
    
    Args:
        page_id (str): ID de la página de Facebook
        es_valido (bool): Si el token es válido o no
    """
    try:
        supabase.table("facebook_paginas") \
            .update({
                "access_token_valido": es_valido,
                "actualizado_en": "now()"
            }) \
            .eq("page_id", page_id) \
            .execute()
        
        print(f"✅ Estado de token actualizado para página {page_id}: {'válido' if es_valido else 'inválido'}")
    except Exception as e:
        print(f"❌ ERROR actualizando estado de token para página {page_id}: {str(e)}")

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
            .select("page_id, nombre_pagina, access_token_valido, ultima_sincronizacion") \
            .eq("activa", True) \
            .order("nombre_pagina") \
            .execute()
        
        print(f"🔍 DEBUG: Respuesta de páginas obtenida: {len(paginas.data or [])} registros")
        
        # Agregar información sobre el estado del token
        paginas_con_estado = []
        for pagina in paginas.data or []:
            pagina_info = dict(pagina)
            pagina_info['tiene_token'] = bool(obtener_token_pagina(pagina['page_id']))
            paginas_con_estado.append(pagina_info)
        
        result = {'success': True, 'paginas': paginas_con_estado}
        
        print("🔍 DEBUG: Enviando respuesta exitosa para páginas")
        return jsonify(result)
    except Exception as e:
        print(f"❌ ERROR en api_paginas_webhook: {str(e)}")
        print(f"❌ ERROR tipo: {type(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e), 'error_type': str(type(e))}), 500


@webhooks_api_bp.route("/pagina/<page_id>/token")
def api_token_pagina(nombre_nora, page_id):
    """
    Obtiene información del token de una página específica.
    """
    try:
        print(f"🔍 DEBUG: Solicitando token para página {page_id}")
        
        # Obtener información completa de la página
        response = supabase.table("facebook_paginas") \
            .select("page_id, nombre_pagina, access_token_valido, ultima_sincronizacion, creado_en") \
            .eq("page_id", page_id) \
            .eq("activa", True) \
            .single() \
            .execute()
        
        if not response.data:
            return jsonify({
                'success': False, 
                'message': f'Página {page_id} no encontrada o inactiva'
            }), 404
        
        pagina_data = response.data
        token = obtener_token_pagina(page_id)
        
        result = {
            'success': True,
            'page_id': page_id,
            'nombre_pagina': pagina_data.get('nombre_pagina'),
            'tiene_token': bool(token),
            'token_valido': pagina_data.get('access_token_valido', True),
            'ultima_sincronizacion': pagina_data.get('ultima_sincronizacion'),
            'creado_en': pagina_data.get('creado_en')
        }
        
        # Solo incluir el token si se solicita explícitamente y es para uso interno
        if request.args.get('include_token') == 'true' and token:
            result['access_token'] = token
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ ERROR obteniendo token para página {page_id}: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@webhooks_api_bp.route("/pagina/<page_id>/validar-token", methods=['POST'])
def api_validar_token_pagina(nombre_nora, page_id):
    """
    Valida el token de una página específica contra la API de Facebook.
    """
    try:
        import requests
        import os
        
        print(f"🔍 DEBUG: Validando token para página {page_id}")
        
        token = obtener_token_pagina(page_id)
        if not token:
            return jsonify({
                'success': False,
                'message': 'No hay token guardado para esta página'
            }), 400
        
        # Validar token con Facebook API
        url = f"https://graph.facebook.com/v18.0/{page_id}"
        params = {
            'access_token': token,
            'fields': 'id,name,access_token'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Actualizar estado como válido
            actualizar_estado_token_pagina(page_id, True)
            
            return jsonify({
                'success': True,
                'message': 'Token válido',
                'page_name': data.get('name'),
                'validado_en': 'now()'
            })
        else:
            # Token inválido
            actualizar_estado_token_pagina(page_id, False)
            
            return jsonify({
                'success': False,
                'message': f'Token inválido: {response.status_code}',
                'facebook_error': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }), 400
            
    except Exception as e:
        print(f"❌ ERROR validando token para página {page_id}: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500