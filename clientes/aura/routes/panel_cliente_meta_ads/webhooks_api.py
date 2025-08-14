from flask import Blueprint, request, jsonify, g
from clientes.aura.utils.supabase_client import supabase
import os
import requests
from datetime import datetime

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

def obtener_token_principal():
    """
    Obtiene el token principal de Meta desde las variables de entorno.
    
    Returns:
        str: Token principal de Meta o None si no se encuentra
    """
    token = os.getenv('META_ACCESS_TOKEN')
    if token:
        print("✅ Token principal META obtenido")
        return token
    else:
        print("❌ ERROR: META_ACCESS_TOKEN no encontrado en variables de entorno")
        return None

def verificar_webhook_registrado(id_cuenta, access_token):
    """
    Verifica si una cuenta publicitaria está suscrita al webhook.
    
    Método oficial según documentación de Meta:
    GET /{ad-account-id}/subscribed_apps
    
    Args:
        id_cuenta (str): ID de la cuenta publicitaria (sin prefijo act_)
        access_token (str): Token de acceso
        
    Returns:
        bool: True si la cuenta está suscrita, False en caso contrario
    """
    try:
        app_id = os.getenv('META_APP_ID')
        
        if not app_id:
            print(f"❌ META_APP_ID no configurado")
            return False
        
        # Verificar suscripción de la cuenta específica usando el método oficial
        url = f"https://graph.facebook.com/v18.0/act_{id_cuenta}/subscribed_apps"
        params = {'access_token': access_token}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            apps_suscritas = data.get('data', [])
            
            # Verificar si nuestra app está en la lista
            for app in apps_suscritas:
                if app.get('id') == app_id:
                    print(f"✅ Cuenta {id_cuenta} está suscrita a app {app_id}")
                    return True
            
            print(f"❌ Cuenta {id_cuenta} NO está suscrita a app {app_id}")
            print(f"📋 Apps suscritas: {[app.get('id') for app in apps_suscritas]}")
            return False
        else:
            print(f"❌ Error verificando suscripción cuenta {id_cuenta}: {response.status_code}")
            if response.status_code == 400:
                error_data = response.json()
                print(f"📋 Error details: {error_data}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando webhook para cuenta {id_cuenta}: {e}")
        return False

def registrar_webhook_nivel_app():
    """
    Registra webhook a nivel de aplicación para cuentas publicitarias.
    
    Método oficial según documentación Meta:
    POST /{app-id}/subscriptions con object=adaccount
    
    Esto permite recibir webhooks de TODAS las cuentas publicitarias
    asociadas a la aplicación de una sola vez.
    
    Returns:
        bool: True si el registro fue exitoso, False en caso contrario
    """
    try:
        import hmac
        import hashlib
        
        app_id = os.getenv('META_APP_ID')
        app_secret = os.getenv('META_APP_SECRET')
        webhook_url = f"{os.getenv('BASE_URL', 'https://app.soynoraai.com')}/meta/webhook"
        verify_token = os.getenv('META_WEBHOOK_VERIFY_TOKEN', 'nora123')
        
        if not all([app_id, app_secret]):
            print("❌ Variables de entorno faltantes para webhook nivel app (META_APP_ID, META_APP_SECRET)")
            return False
        
        # ✅ CORREGIDO: Crear App Access Token según documentación Meta
        # App Access Token format: {app-id}|{app-secret}
        app_access_token = f"{app_id}|{app_secret}"
            
        print(f"🔗 Registrando webhook a nivel de app {app_id}")
        print(f"📍 Webhook URL: {webhook_url}")
        print(f"📍 Usando App Access Token: {app_id}|{app_secret[:6]}...")
        
        # Endpoint oficial para webhooks de aplicación
        url = f"https://graph.facebook.com/v18.0/{app_id}/subscriptions"
        
        data = {
            'object': 'adaccount',  # Para cuentas publicitarias
            'callback_url': webhook_url,
            'fields': ['campaign', 'adset', 'ad', 'creative'],  # Campos que queremos recibir
            'verify_token': verify_token,
            'access_token': app_access_token,  # ✅ CORREGIDO: Usar App Access Token
        }
        
        response = requests.post(url, data=data, timeout=15)
        
        if response.status_code == 200:
            print(f"✅ Webhook app-level registrado exitosamente")
            print(f"📋 Respuesta: {response.json()}")
            
            # Marcar todas las cuentas activas como registradas
            supabase.table('meta_ads_cuentas') \
                .update({
                    'webhook_registrado': True,
                    'actualizada_en': datetime.now().isoformat()
                }) \
                .eq('estado_actual', 'ACTIVE') \
                .execute()
            
            print(f"✅ Todas las cuentas activas marcadas como registradas")
            return True
        else:
            print(f"❌ Error registrando webhook app-level: {response.status_code}")
            print(f"❌ Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción registrando webhook app-level: {e}")
        return False

def registrar_webhook_en_cuenta(id_cuenta, access_token):
    """
    MÉTODO LEGACY: Para cuentas publicitarias, se recomienda usar webhook a nivel de app.
    
    Este método mantiene compatibilidad pero redirige al método app-level
    que es más eficiente y el recomendado por Meta.
    
    Args:
        id_cuenta (str): ID de la cuenta publicitaria (sin prefijo act_)
        access_token (str): Token de acceso
        
    Returns:
        bool: True si el registro fue exitoso, False en caso contrario
    """
    print(f"ℹ️ NOTA: Para cuentas publicitarias se recomienda webhook a nivel de app")
    print(f"ℹ️ Cuenta {id_cuenta} se beneficiará del webhook app-level existente")
    
    # Marcar como registrado en BD (el webhook app-level cubre todas las cuentas)
    try:
        supabase.table('meta_ads_cuentas') \
            .update({
                'webhook_registrado': True,
                'actualizada_en': datetime.now().isoformat()
            }) \
            .eq('id_cuenta_publicitaria', id_cuenta) \
            .execute()
        
        print(f"✅ Estado webhook actualizado para cuenta {id_cuenta}")
        return True
    except Exception as e:
        print(f"❌ Error actualizando estado: {e}")
        return False

def registrar_webhooks_en_cuentas_activas():
    """
    Registra webhooks en todas las cuentas publicitarias activas.
    
    Returns:
        dict: Resultado del proceso con estadísticas
    """
    try:
        access_token = obtener_token_principal()
        if not access_token:
            return {
                'success': False,
                'message': 'Token de acceso no disponible'
            }
        
        # Obtener cuentas activas
        response = supabase.table('meta_ads_cuentas') \
            .select('id_cuenta_publicitaria, nombre_cliente, estado_actual') \
            .eq('estado_actual', 'ACTIVE') \
            .execute()
        
        cuentas = response.data or []
        
        if not cuentas:
            return {
                'success': True,
                'message': 'No se encontraron cuentas activas',
                'registrados': 0,
                'errores': 0
            }
        
        registrados = 0
        errores = 0
        detalles = []
        
        for cuenta in cuentas:
            id_cuenta = cuenta['id_cuenta_publicitaria']
            nombre_cliente = cuenta['nombre_cliente']
            
            try:
                # Verificar si ya está registrado
                ya_registrado = verificar_webhook_registrado(id_cuenta, access_token)
                
                if ya_registrado:
                    print(f"✅ Webhook ya registrado para {nombre_cliente} ({id_cuenta})")
                    # Actualizar estado en BD
                    supabase.table('meta_ads_cuentas') \
                        .update({'webhook_registrado': True}) \
                        .eq('id_cuenta_publicitaria', id_cuenta) \
                        .execute()
                    registrados += 1
                    detalles.append({
                        'cuenta': nombre_cliente,
                        'id_cuenta': id_cuenta,
                        'estado': 'Ya registrado'
                    })
                else:
                    # Intentar registrar
                    if registrar_webhook_en_cuenta(id_cuenta, access_token):
                        registrados += 1
                        detalles.append({
                            'cuenta': nombre_cliente,
                            'id_cuenta': id_cuenta,
                            'estado': 'Registrado exitosamente'
                        })
                    else:
                        errores += 1
                        detalles.append({
                            'cuenta': nombre_cliente,
                            'id_cuenta': id_cuenta,
                            'estado': 'Error al registrar'
                        })
                        
            except Exception as e:
                errores += 1
                detalles.append({
                    'cuenta': nombre_cliente,
                    'id_cuenta': id_cuenta,
                    'estado': f'Error: {str(e)}'
                })
                print(f"❌ Error procesando cuenta {nombre_cliente}: {e}")
        
        return {
            'success': True,
            'total_cuentas': len(cuentas),
            'registrados': registrados,
            'errores': errores,
            'detalles': detalles
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

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


# ================================
# APIs para suscripciones de webhooks en cuentas publicitarias
# ================================

@webhooks_api_bp.route("/cuentas")
def api_cuentas_webhook(nombre_nora):
    """
    Obtiene el estado de todas las cuentas publicitarias y su suscripción al webhook.
    """
    try:
        print(f"🔍 DEBUG: Obteniendo estado de cuentas para {nombre_nora}")
        
        access_token = obtener_token_principal()
        if not access_token:
            print("❌ DEBUG: No se pudo obtener token principal")
            return jsonify({
                'success': False,
                'message': 'Token de acceso no configurado'
            }), 500
        
        print("✅ DEBUG: Token obtenido, consultando BD...")
        
        # Obtener cuentas desde la base de datos
        response = supabase.table('meta_ads_cuentas') \
            .select('id_cuenta_publicitaria, nombre_cliente, estado_actual, webhook_registrado, actualizada_en') \
            .order('nombre_cliente') \
            .execute()
        
        if not response.data:
            print("⚠️ DEBUG: No se encontraron cuentas en BD")
            return jsonify({
                'success': True,
                'cuentas': [],
                'estadisticas': {
                    'total_cuentas': 0,
                    'con_webhook': 0,
                    'sin_webhook': 0,
                    'cuentas_activas': 0
                }
            })
        
        print(f"✅ DEBUG: {len(response.data)} cuentas encontradas en BD")
        
        cuentas_con_estado = []
        webhooks_verificados = 0
        errores_verificacion = 0
        
        for i, cuenta in enumerate(response.data or []):
            try:
                id_cuenta = cuenta['id_cuenta_publicitaria']
                print(f"🔍 DEBUG: Procesando cuenta {i+1}/{len(response.data)}: {id_cuenta}")
                
                # Verificar estado actual del webhook con manejo de errores
                webhook_registrado = False
                try:
                    webhook_registrado = verificar_webhook_registrado(id_cuenta, access_token)
                    webhooks_verificados += 1
                    print(f"✅ DEBUG: Webhook verificado para {id_cuenta}: {webhook_registrado}")
                except Exception as webhook_error:
                    errores_verificacion += 1
                    print(f"⚠️ DEBUG: Error verificando webhook para {id_cuenta}: {webhook_error}")
                    webhook_registrado = False
                
                # Si el estado en BD no coincide, actualizarlo
                if webhook_registrado != cuenta.get('webhook_registrado', False):
                    try:
                        supabase.table('meta_ads_cuentas') \
                            .update({'webhook_registrado': webhook_registrado}) \
                            .eq('id_cuenta_publicitaria', id_cuenta) \
                            .execute()
                        print(f"✅ DEBUG: Estado actualizado en BD para {id_cuenta}")
                    except Exception as update_error:
                        print(f"⚠️ DEBUG: Error actualizando BD para {id_cuenta}: {update_error}")
                
                cuentas_con_estado.append({
                    'id_cuenta_publicitaria': id_cuenta,
                    'nombre_cliente': cuenta['nombre_cliente'],
                    'estado_actual': cuenta['estado_actual'],
                    'webhook_registrado': webhook_registrado,
                    'ultima_actualizacion': cuenta.get('actualizada_en')
                })
                
            except Exception as cuenta_error:
                print(f"❌ DEBUG: Error procesando cuenta {cuenta}: {cuenta_error}")
                continue
        
        # Estadísticas
        total_cuentas = len(cuentas_con_estado)
        con_webhook = len([c for c in cuentas_con_estado if c['webhook_registrado']])
        activas = len([c for c in cuentas_con_estado if c['estado_actual'] == 'ACTIVE'])
        
        estadisticas = {
            'total_cuentas': total_cuentas,
            'con_webhook': con_webhook,
            'sin_webhook': total_cuentas - con_webhook,
            'cuentas_activas': activas,
            'webhooks_verificados': webhooks_verificados,
            'errores_verificacion': errores_verificacion
        }
        
        print(f"✅ DEBUG: Estadísticas calculadas: {estadisticas}")
        
        return jsonify({
            'success': True,
            'cuentas': cuentas_con_estado,
            'estadisticas': estadisticas
        })
        
    except Exception as e:
        print(f"❌ DEBUG: ERROR general obteniendo estado de cuentas: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@webhooks_api_bp.route("/cuentas/registrar-webhook", methods=['POST'])
def api_registrar_webhook_cuenta(nombre_nora):
    """
    Registra webhook para una cuenta específica.
    """
    try:
        data = request.get_json()
        id_cuenta = data.get('id_cuenta')
        
        if not id_cuenta:
            return jsonify({
                'success': False,
                'message': 'ID de cuenta requerido'
            }), 400
        
        access_token = obtener_token_principal()
        if not access_token:
            return jsonify({
                'success': False,
                'message': 'Token de acceso no disponible'
            }), 500
        
        # Verificar si ya está registrado
        ya_registrado = verificar_webhook_registrado(id_cuenta, access_token)
        
        if ya_registrado:
            return jsonify({
                'success': True,
                'message': f'Webhook ya está registrado para cuenta {id_cuenta}',
                'ya_registrado': True
            })
        
        # Intentar registrar
        if registrar_webhook_en_cuenta(id_cuenta, access_token):
            return jsonify({
                'success': True,
                'message': f'Webhook registrado exitosamente para cuenta {id_cuenta}'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Error registrando webhook para cuenta {id_cuenta}'
            }), 500
            
    except Exception as e:
        print(f"❌ ERROR registrando webhook individual: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@webhooks_api_bp.route("/cuentas/registrar-todas", methods=['POST'])
def api_registrar_webhooks_todas_cuentas(nombre_nora):
    """
    Registra webhooks en todas las cuentas publicitarias activas.
    """
    try:
        print(f"🔄 Iniciando registro masivo de webhooks para {nombre_nora}")
        
        resultado = registrar_webhooks_en_cuentas_activas()
        
        if resultado.get('success', False):
            return jsonify({
                'success': True,
                'message': 'Proceso de registro completado',
                'estadisticas': {
                    'total_cuentas': resultado.get('total_cuentas', 0),
                    'registrados': resultado.get('registrados', 0),
                    'errores': resultado.get('errores', 0)
                },
                'detalles': resultado.get('detalles', [])
            })
        else:
            return jsonify({
                'success': False,
                'message': resultado.get('message', 'Error desconocido en registro masivo')
            }), 500
            
    except Exception as e:
        print(f"❌ ERROR en registro masivo: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@webhooks_api_bp.route("/cuentas/verificar-webhook/<id_cuenta>", methods=['GET'])
def api_verificar_webhook_cuenta(nombre_nora, id_cuenta):
    """
    Verifica el estado del webhook para una cuenta específica.
    """
    try:
        access_token = obtener_token_principal()
        if not access_token:
            return jsonify({
                'success': False,
                'message': 'Token de acceso no disponible'
            }), 500
        
        webhook_registrado = verificar_webhook_registrado(id_cuenta, access_token)
        
        # Actualizar estado en BD
        supabase.table('meta_ads_cuentas') \
            .update({
                'webhook_registrado': webhook_registrado,
                'actualizada_en': datetime.now().isoformat()
            }) \
            .eq('id_cuenta_publicitaria', id_cuenta) \
            .execute()
        
        return jsonify({
            'success': True,
            'id_cuenta': id_cuenta,
            'webhook_registrado': webhook_registrado,
            'verificado_en': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ ERROR verificando webhook para cuenta {id_cuenta}: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@webhooks_api_bp.route("/cuentas/eliminar-webhook/<id_cuenta>", methods=['DELETE'])
def api_eliminar_webhook_cuenta(nombre_nora, id_cuenta):
    """
    Elimina la suscripción de webhook para una cuenta específica.
    """
    try:
        access_token = obtener_token_principal()
        if not access_token:
            return jsonify({
                'success': False,
                'message': 'Token de acceso no disponible'
            }), 500
        
        # Obtener suscripciones actuales
        url = f"https://graph.facebook.com/v18.0/act_{id_cuenta}/subscriptions"
        params = {'access_token': access_token}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            webhooks = data.get('data', [])
            
            eliminados = 0
            for webhook in webhooks:
                webhook_id = webhook.get('id')
                if webhook_id:
                    # Eliminar webhook
                    delete_url = f"https://graph.facebook.com/v18.0/{webhook_id}"
                    delete_response = requests.delete(delete_url, params=params, timeout=10)
                    
                    if delete_response.status_code == 200:
                        eliminados += 1
                        print(f"✅ Webhook {webhook_id} eliminado para cuenta {id_cuenta}")
                    else:
                        print(f"❌ Error eliminando webhook {webhook_id}: {delete_response.status_code}")
            
            # Actualizar estado en BD
            supabase.table('meta_ads_cuentas') \
                .update({
                    'webhook_registrado': False,
                    'actualizada_en': datetime.now().isoformat()
                }) \
                .eq('id_cuenta_publicitaria', id_cuenta) \
                .execute()
            
            return jsonify({
                'success': True,
                'message': f'Se eliminaron {eliminados} suscripciones de webhook',
                'webhooks_eliminados': eliminados
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Error obteniendo suscripciones: {response.status_code}'
            }), 500
            
    except Exception as e:
        print(f"❌ ERROR eliminando webhook para cuenta {id_cuenta}: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@webhooks_api_bp.route("/estadisticas")
def api_estadisticas_webhooks(nombre_nora):
    """
    Obtiene estadísticas generales de webhooks y eventos.
    """
    try:
        from datetime import timedelta
        
        # Estadísticas de cuentas
        cuentas = supabase.table('meta_ads_cuentas') \
            .select('webhook_registrado, estado_actual') \
            .execute()
        
        total_cuentas = len(cuentas.data or [])
        con_webhook = len([c for c in cuentas.data or [] if c.get('webhook_registrado')])
        activas = len([c for c in cuentas.data or [] if c.get('estado_actual') == 'ACTIVE'])
        
        # Estadísticas de eventos (últimos 7 días)
        hace_7_dias = (datetime.now() - timedelta(days=7)).isoformat()
        
        eventos_logs = supabase.table('logs_webhooks_meta') \
            .select('id') \
            .gte('timestamp', hace_7_dias) \
            .execute()
        
        eventos_publicaciones = supabase.table('meta_publicaciones_webhook') \
            .select('id') \
            .gte('creada_en', hace_7_dias) \
            .execute()
        
        # Estadísticas de páginas
        paginas = supabase.table('facebook_paginas') \
            .select('access_token_valido, activa') \
            .execute()
        
        total_paginas = len(paginas.data or [])
        paginas_activas = len([p for p in paginas.data or [] if p.get('activa')])
        tokens_validos = len([p for p in paginas.data or [] if p.get('access_token_valido')])
        
        return jsonify({
            'success': True,
            'estadisticas': {
                'cuentas': {
                    'total': total_cuentas,
                    'con_webhook': con_webhook,
                    'sin_webhook': total_cuentas - con_webhook,
                    'activas': activas
                },
                'eventos_7_dias': {
                    'logs_webhook': len(eventos_logs.data or []),
                    'publicaciones': len(eventos_publicaciones.data or []),
                    'total': len(eventos_logs.data or []) + len(eventos_publicaciones.data or [])
                },
                'paginas': {
                    'total': total_paginas,
                    'activas': paginas_activas,
                    'tokens_validos': tokens_validos
                }
            },
            'generado_en': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ ERROR obteniendo estadísticas: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ================================
# APIs de gestión masiva para producción
# ================================

@webhooks_api_bp.route("/suscribir-todas-cuentas", methods=['POST'])  
def suscribir_todas_cuentas(nombre_nora):
    """
    Suscribe TODAS las cuentas activas a webhooks usando el mecanismo oficial de Meta.
    
    Basado en documentación oficial:
    - POST /act_<AD_ACCOUNT_ID>/subscribed_apps
    - App debe estar configurada en Facebook Developer Console
    """
    try:
        print(f"🚀 INICIANDO SUSCRIPCIÓN MASIVA DE WEBHOOKS")
        print(f"📋 Para Nora: {nombre_nora}")
        
        # Verificar configuración
        access_token = os.getenv('META_ACCESS_TOKEN')
        app_id = os.getenv('META_APP_ID')
        
        if not access_token or not app_id:
            return jsonify({
                'success': False,
                'error': 'META_ACCESS_TOKEN o META_APP_ID no configurados'
            }), 500
        
        print(f"✅ Configuración verificada - APP_ID: {app_id}")
        
        # Obtener todas las cuentas ACTIVAS
        response = supabase.table('meta_ads_cuentas') \
            .select('id_cuenta_publicitaria, nombre_cliente, webhook_registrado') \
            .eq('estado_actual', 'ACTIVE') \
            .execute()
        
        if not response.data:
            return jsonify({
                'success': True,
                'message': 'No hay cuentas activas para suscribir',
                'total_cuentas': 0,
                'suscripciones_exitosas': 0,
                'errores': 0
            })
        
        cuentas = response.data
        print(f"📊 {len(cuentas)} cuentas activas encontradas")
        
        # Estadísticas de proceso
        suscripciones_exitosas = 0
        errores = 0
        detalles = []
        ya_suscritas = 0
        
        for i, cuenta in enumerate(cuentas, 1):
            id_cuenta = cuenta['id_cuenta_publicitaria']
            nombre_cliente = cuenta['nombre_cliente']
            ya_registrado = cuenta.get('webhook_registrado', False)
            
            print(f"\n🔄 [{i}/{len(cuentas)}] Procesando: {nombre_cliente} ({id_cuenta})")
            
            try:
                # URL según documentación oficial de Meta
                url = f"https://graph.facebook.com/v18.0/act_{id_cuenta}/subscribed_apps"
                
                # Datos de suscripción oficial
                data = {
                    'subscribed_fields': [
                        'with_issues_ad_objects',
                        'in_process_ad_objects', 
                        'ad_recommendations',
                        'creative_fatigue',
                        'product_set_issue'
                    ],
                    'access_token': access_token
                }
                
                print(f"📡 POST {url}")
                response = requests.post(url, data=data, timeout=15)
                response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                
                if response.status_code == 200:
                    # Verificar respuesta exitosa
                    success_val = response_data.get('success')
                    is_success = success_val is True or success_val == 'true' or success_val == True
                    
                    if is_success:
                        print(f"✅ Suscripción exitosa para {id_cuenta}")
                        suscripciones_exitosas += 1
                        
                        # Actualizar BD
                        supabase.table('meta_ads_cuentas') \
                            .update({
                                'webhook_registrado': True,
                                'actualizada_en': datetime.now().isoformat()
                            }) \
                            .eq('id_cuenta_publicitaria', id_cuenta) \
                            .execute()
                        
                        detalles.append({
                            'cuenta': nombre_cliente,
                            'id': id_cuenta,
                            'status': 'Suscrito exitosamente',
                            'ya_registrado': ya_registrado
                        })
                    else:
                        print(f"⚠️ Respuesta ambigua para {id_cuenta}: {response_data}")
                        errores += 1
                        detalles.append({
                            'cuenta': nombre_cliente,
                            'id': id_cuenta,
                            'status': f'Respuesta ambigua: {response_data}',
                            'ya_registrado': ya_registrado
                        })
                else:
                    error_msg = response_data.get('error', {}).get('message', 'Error desconocido')
                    print(f"❌ Error {response.status_code} para {id_cuenta}: {error_msg}")
                    errores += 1
                    
                    detalles.append({
                        'cuenta': nombre_cliente,
                        'id': id_cuenta,
                        'status': f'Error {response.status_code}: {error_msg}',
                        'ya_registrado': ya_registrado
                    })
                    
            except Exception as e:
                print(f"❌ Excepción procesando {id_cuenta}: {str(e)}")
                errores += 1
                detalles.append({
                    'cuenta': nombre_cliente,
                    'id': id_cuenta,
                    'status': f'Excepción: {str(e)}',
                    'ya_registrado': ya_registrado
                })
        
        # Resultado final
        resultado = {
            'success': True,
            'message': 'Proceso de suscripción masiva completado',
            'total_cuentas': len(cuentas),
            'suscripciones_exitosas': suscripciones_exitosas,
            'errores': errores,
            'ya_suscritas': ya_suscritas,
            'porcentaje_exito': round((suscripciones_exitosas / len(cuentas)) * 100, 1) if cuentas else 0,
            'detalles': detalles,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\n🎯 RESULTADO FINAL:")
        print(f"   ✅ Exitosas: {suscripciones_exitosas}/{len(cuentas)}")
        print(f"   ❌ Errores: {errores}")
        print(f"   📈 Porcentaje éxito: {resultado['porcentaje_exito']}%")
        
        return jsonify(resultado)
        
    except Exception as e:
        print(f"❌ ERROR GENERAL en suscripción masiva: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@webhooks_api_bp.route("/verificar-suscripciones-cuentas", methods=['GET'])
def verificar_suscripciones_cuentas(nombre_nora):
    """
    Verifica el estado real de suscripciones de webhooks vs BD para sync.
    """
    try:
        print(f"🔍 VERIFICANDO SINCRONIZACIÓN DE SUSCRIPCIONES")
        
        # Verificar configuración
        access_token = os.getenv('META_ACCESS_TOKEN')
        app_id = os.getenv('META_APP_ID')
        
        if not access_token or not app_id:
            return jsonify({
                'success': False,
                'error': 'META_ACCESS_TOKEN o META_APP_ID no configurados'
            }), 500
        
        # Obtener cuentas activas de BD
        response = supabase.table('meta_ads_cuentas') \
            .select('id_cuenta_publicitaria, nombre_cliente, webhook_registrado') \
            .eq('estado_actual', 'ACTIVE') \
            .execute()
        
        if not response.data:
            return jsonify({
                'success': True,
                'message': 'No hay cuentas activas para verificar',
                'cuentas_verificadas': []
            })
        
        cuentas = response.data
        print(f"📊 Verificando {len(cuentas)} cuentas activas")
        
        cuentas_verificadas = []
        discrepancias = []
        errores_verificacion = 0
        
        for i, cuenta in enumerate(cuentas, 1):
            id_cuenta = cuenta['id_cuenta_publicitaria']
            nombre_cliente = cuenta['nombre_cliente']
            webhook_en_bd = cuenta.get('webhook_registrado', False)
            
            print(f"\n🔍 [{i}/{len(cuentas)}] Verificando: {nombre_cliente}")
            
            try:
                # Verificar suscripciones reales en Meta
                url = f"https://graph.facebook.com/v18.0/act_{id_cuenta}/subscribed_apps"
                params = {'access_token': access_token}
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    apps_suscritas = data.get('data', [])
                    
                    # Buscar nuestra app
                    nuestra_app_suscrita = False
                    for app in apps_suscritas:
                        if str(app.get('id')) == str(app_id):
                            nuestra_app_suscrita = True
                            break
                    
                    # Comparar con BD
                    estado_sincronizado = webhook_en_bd == nuestra_app_suscrita
                    
                    if not estado_sincronizado:
                        discrepancias.append({
                            'cuenta': nombre_cliente,
                            'id': id_cuenta,
                            'bd_dice': webhook_en_bd,
                            'meta_dice': nuestra_app_suscrita
                        })
                        
                        # Actualizar BD para sincronizar
                        supabase.table('meta_ads_cuentas') \
                            .update({
                                'webhook_registrado': nuestra_app_suscrita,
                                'actualizada_en': datetime.now().isoformat()
                            }) \
                            .eq('id_cuenta_publicitaria', id_cuenta) \
                            .execute()
                        
                        print(f"🔄 BD sincronizada: {webhook_en_bd} → {nuestra_app_suscrita}")
                    
                    cuentas_verificadas.append({
                        'cuenta': nombre_cliente,
                        'id': id_cuenta,
                        'webhook_activo': nuestra_app_suscrita,
                        'estaba_sincronizado': estado_sincronizado,
                        'apps_suscritas_total': len(apps_suscritas)
                    })
                    
                    print(f"✅ {id_cuenta}: {'Suscrita' if nuestra_app_suscrita else 'No suscrita'}")
                    
                else:
                    errores_verificacion += 1
                    print(f"❌ Error verificando {id_cuenta}: {response.status_code}")
                    cuentas_verificadas.append({
                        'cuenta': nombre_cliente,
                        'id': id_cuenta,
                        'webhook_activo': None,
                        'error': f'HTTP {response.status_code}',
                        'estaba_sincronizado': False
                    })
                    
            except Exception as e:
                errores_verificacion += 1
                print(f"❌ Excepción verificando {id_cuenta}: {str(e)}")
                cuentas_verificadas.append({
                    'cuenta': nombre_cliente,
                    'id': id_cuenta,
                    'webhook_activo': None,
                    'error': str(e),
                    'estaba_sincronizado': False
                })
        
        # Estadísticas finales
        cuentas_con_webhook = len([c for c in cuentas_verificadas if c.get('webhook_activo') == True])
        cuentas_sin_webhook = len([c for c in cuentas_verificadas if c.get('webhook_activo') == False])
        
        resultado = {
            'success': True,
            'total_verificadas': len(cuentas_verificadas),
            'con_webhook': cuentas_con_webhook,
            'sin_webhook': cuentas_sin_webhook,
            'errores_verificacion': errores_verificacion,
            'discrepancias_encontradas': len(discrepancias),
            'discrepancias': discrepancias,
            'cuentas_verificadas': cuentas_verificadas,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\n📊 RESUMEN VERIFICACIÓN:")
        print(f"   ✅ Con webhook: {cuentas_con_webhook}")
        print(f"   ❌ Sin webhook: {cuentas_sin_webhook}")
        print(f"   🔄 Discrepancias: {len(discrepancias)}")
        print(f"   💥 Errores: {errores_verificacion}")
        
        return jsonify(resultado)
        
    except Exception as e:
        print(f"❌ ERROR GENERAL en verificación: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@webhooks_api_bp.route('/registrar-webhook-nivel-app', methods=['POST'])
def api_registrar_webhook_nivel_app(nombre_nora):
    """Registra webhook a nivel de aplicación para adaccounts (método oficial Meta)"""
    try:
        print("\n🚀 REGISTRO WEBHOOK NIVEL APLICACIÓN")
        print("=" * 60)
        print("📋 Usando método oficial Meta para adaccounts")
        print("🔗 POST /{app-id}/subscriptions con object=adaccount")
        
        access_token = os.getenv('META_ACCESS_TOKEN')
        app_id = os.getenv('META_APP_ID')
        
        if not access_token:
            return jsonify({
                'success': False,
                'error': 'META_ACCESS_TOKEN no configurado'
            }), 500
            
        if not app_id:
            return jsonify({
                'success': False,
                'error': 'META_APP_ID no configurado'
            }), 500
        
        # Llamar función de registro
        resultado = registrar_webhook_nivel_app()
        
        if resultado:
            print("✅ Webhook a nivel de app registrado exitosamente")
            return jsonify({
                'success': True,
                'message': 'Webhook registrado a nivel de aplicación',
                'metodo': 'app-level',
                'objeto': 'adaccount',
                'timestamp': datetime.now().isoformat()
            })
        else:
            print(f"❌ Error registrando webhook a nivel de app")
            return jsonify({
                'success': False,
                'error': 'Error en registro de webhook a nivel de aplicación',
                'timestamp': datetime.now().isoformat()
            }), 400
        
    except Exception as e:
        print(f"❌ ERROR GENERAL en registro nivel app: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@webhooks_api_bp.route('/status-webhook-app', methods=['GET'])
def api_status_webhook_app(nombre_nora):
    """Verifica status del webhook a nivel de aplicación"""
    try:
        print("\n🔍 VERIFICANDO STATUS WEBHOOK NIVEL APP")
        print("=" * 50)
        
        access_token = os.getenv('META_ACCESS_TOKEN')
        app_id = os.getenv('META_APP_ID')
        
        if not access_token or not app_id:
            return jsonify({
                'success': False,
                'error': 'META_ACCESS_TOKEN o META_APP_ID no configurados'
            }), 500
        
        # Verificar suscripciones del app
        url = f"https://graph.facebook.com/v18.0/{app_id}/subscriptions"
        params = {'access_token': access_token}
        
        print(f"📡 GET {url}")
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            subscriptions = data.get('data', [])
            
            print(f"📊 Encontradas {len(subscriptions)} suscripciones")
            
            # Buscar suscripción adaccount
            adaccount_sub = None
            for sub in subscriptions:
                if sub.get('object') == 'adaccount':
                    adaccount_sub = sub
                    break
            
            if adaccount_sub:
                print("✅ Webhook adaccount encontrado")
                return jsonify({
                    'success': True,
                    'webhook_registrado': True,
                    'subscription': adaccount_sub,
                    'callback_url': adaccount_sub.get('callback_url'),
                    'fields': adaccount_sub.get('fields', []),
                    'active': adaccount_sub.get('active', False),
                    'timestamp': datetime.now().isoformat()
                })
            else:
                print("❌ No se encontró webhook adaccount")
                return jsonify({
                    'success': True,
                    'webhook_registrado': False,
                    'total_subscriptions': len(subscriptions),
                    'subscriptions': subscriptions,
                    'timestamp': datetime.now().isoformat()
                })
        else:
            error_msg = f"Error {response.status_code}: {response.text}"
            print(f"❌ {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            }), response.status_code
        
    except Exception as e:
        print(f"❌ ERROR verificando status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500