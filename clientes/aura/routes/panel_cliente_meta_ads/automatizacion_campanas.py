# 🗄️ CONTEXTO BD PARA GITHUB COPILOT
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas
# BD ACTUAL: meta_ads_anuncios_detalle(96), meta_ads_cuentas(15), meta_ads_audiencias(18)

"""
Módulo para automatización de campañas basada en publicaciones de Facebook/Instagram
"""
from flask import Blueprint, render_template, request, jsonify
from clientes.aura.utils.supabase_client import supabase
from datetime import datetime, timedelta
import os
import requests
import json
import re

# ============================================================================
# FUNCIONES PARA GESTIÓN DE AUTOMATIZACIONES
# ============================================================================

def obtener_automatizaciones(nombre_nora):
    """
    Obtiene todas las automatizaciones configuradas para una instancia Nora
    
    Args:
        nombre_nora (str): Nombre de la instancia Nora
        
    Returns:
        list: Lista de automatizaciones
    """
    try:
        resultado = supabase.table("meta_ads_automatizaciones") \
            .select("*, meta_ads_cuentas!inner(nombre_cliente, empresa_id)") \
            .eq("nombre_nora", nombre_nora) \
            .order("creada_en", desc=True) \
            .execute()
        
        automatizaciones = resultado.data or []
        
        # Enriquecer datos
        for auto in automatizaciones:
            # Formatear fecha
            if auto.get('creada_en'):
                try:
                    fecha = datetime.fromisoformat(auto['creada_en'].replace('Z', '+00:00'))
                    auto['creada_en_fmt'] = fecha.strftime('%d/%m/%Y %H:%M')
                except:
                    auto['creada_en_fmt'] = 'N/A'
            
            # Estado visual
            if auto.get('activa'):
                auto['estado_badge'] = {'text': 'Activa', 'class': 'bg-green-100 text-green-800'}
            else:
                auto['estado_badge'] = {'text': 'Inactiva', 'class': 'bg-gray-100 text-gray-800'}
            
            # Información de la cuenta
            cuenta_info = auto.get('meta_ads_cuentas', {})
            auto['nombre_cliente'] = cuenta_info.get('nombre_cliente', 'Sin cliente')
            
            # Parsear reglas JSON
            try:
                auto['reglas_parsed'] = json.loads(auto.get('reglas_json', '{}'))
            except:
                auto['reglas_parsed'] = {}
        
        return automatizaciones
        
    except Exception as e:
        print(f"Error obteniendo automatizaciones: {e}")
        return []

def crear_automatizacion(nombre_nora, datos_automatizacion):
    """
    Crea una nueva automatización
    
    Args:
        nombre_nora (str): Nombre de la instancia Nora
        datos_automatizacion (dict): Datos de la automatización
        
    Returns:
        dict: Resultado de la operación
    """
    try:
        # Validar campos requeridos
        campos_requeridos = ['nombre', 'page_id', 'ad_account_id', 'campaign_id', 'adset_id']
        for campo in campos_requeridos:
            if not datos_automatizacion.get(campo):
                return {'ok': False, 'error': f'Campo {campo} es requerido'}
        
        # Preparar datos para inserción
        automatizacion_data = {
            'nombre_nora': nombre_nora,
            'nombre': datos_automatizacion['nombre'],
            'descripcion': datos_automatizacion.get('descripcion', ''),
            'page_id': datos_automatizacion['page_id'],
            'ad_account_id': datos_automatizacion['ad_account_id'],
            'campaign_id': datos_automatizacion['campaign_id'],
            'adset_id': datos_automatizacion['adset_id'],
            'reglas_json': json.dumps({
                'filtros_contenido': datos_automatizacion.get('filtros_contenido', {}),
                'plantilla_anuncio': datos_automatizacion.get('plantilla_anuncio', {}),
                'programacion': datos_automatizacion.get('programacion', {})
            }),
            'activa': datos_automatizacion.get('activa', True),
            'creada_en': datetime.utcnow().isoformat()
        }
        
        # Insertar en base de datos
        resultado = supabase.table('meta_ads_automatizaciones').insert(automatizacion_data).execute()
        
        if resultado.data:
            return {
                'ok': True,
                'automatizacion_id': resultado.data[0]['id'],
                'message': f'Automatización "{datos_automatizacion["nombre"]}" creada exitosamente'
            }
        else:
            return {'ok': False, 'error': 'No se pudo crear la automatización'}
            
    except Exception as e:
        return {'ok': False, 'error': f'Error creando automatización: {str(e)}'}

def actualizar_automatizacion(automatizacion_id, nombre_nora, datos_actualizacion):
    """
    Actualiza una automatización existente
    
    Args:
        automatizacion_id (int): ID de la automatización
        nombre_nora (str): Nombre de la instancia Nora
        datos_actualizacion (dict): Datos a actualizar
        
    Returns:
        dict: Resultado de la operación
    """
    try:
        # Preparar datos de actualización
        update_data = {}
        
        if 'nombre' in datos_actualizacion:
            update_data['nombre'] = datos_actualizacion['nombre']
        if 'descripcion' in datos_actualizacion:
            update_data['descripcion'] = datos_actualizacion['descripcion']
        if 'activa' in datos_actualizacion:
            update_data['activa'] = datos_actualizacion['activa']
        
        # Actualizar reglas si se proporcionan
        if any(k in datos_actualizacion for k in ['filtros_contenido', 'plantilla_anuncio', 'programacion']):
            # Obtener reglas actuales
            resultado_actual = supabase.table('meta_ads_automatizaciones') \
                .select('reglas_json') \
                .eq('id', automatizacion_id) \
                .eq('nombre_nora', nombre_nora) \
                .single() \
                .execute()
            
            if resultado_actual.data:
                try:
                    reglas_actuales = json.loads(resultado_actual.data.get('reglas_json', '{}'))
                except:
                    reglas_actuales = {}
                
                # Actualizar reglas
                if 'filtros_contenido' in datos_actualizacion:
                    reglas_actuales['filtros_contenido'] = datos_actualizacion['filtros_contenido']
                if 'plantilla_anuncio' in datos_actualizacion:
                    reglas_actuales['plantilla_anuncio'] = datos_actualizacion['plantilla_anuncio']
                if 'programacion' in datos_actualizacion:
                    reglas_actuales['programacion'] = datos_actualizacion['programacion']
                
                update_data['reglas_json'] = json.dumps(reglas_actuales)
        
        if update_data:
            update_data['actualizada_en'] = datetime.utcnow().isoformat()
            
            resultado = supabase.table('meta_ads_automatizaciones') \
                .update(update_data) \
                .eq('id', automatizacion_id) \
                .eq('nombre_nora', nombre_nora) \
                .execute()
            
            if resultado.data:
                return {'ok': True, 'message': 'Automatización actualizada exitosamente'}
            else:
                return {'ok': False, 'error': 'No se pudo actualizar la automatización'}
        else:
            return {'ok': False, 'error': 'No hay datos para actualizar'}
            
    except Exception as e:
        return {'ok': False, 'error': f'Error actualizando automatización: {str(e)}'}

def eliminar_automatizacion(automatizacion_id, nombre_nora):
    """
    Elimina una automatización
    
    Args:
        automatizacion_id (int): ID de la automatización
        nombre_nora (str): Nombre de la instancia Nora
        
    Returns:
        dict: Resultado de la operación
    """
    try:
        resultado = supabase.table('meta_ads_automatizaciones') \
            .delete() \
            .eq('id', automatizacion_id) \
            .eq('nombre_nora', nombre_nora) \
            .execute()
        
        return {'ok': True, 'message': 'Automatización eliminada exitosamente'}
        
    except Exception as e:
        return {'ok': False, 'error': f'Error eliminando automatización: {str(e)}'}

# ============================================================================
# FUNCIONES PARA PROCESAMIENTO DE PUBLICACIONES
# ============================================================================

def procesar_publicacion_webhook(webhook_data):
    """
    Procesa una publicación recibida por webhook y aplica automatizaciones
    
    Args:
        webhook_data (dict): Datos del webhook de Meta
        
    Returns:
        dict: Resultado del procesamiento
    """
    try:
        print(f"🔄 Procesando publicación webhook: {webhook_data}")
        
        # Extraer información de la publicación
        entry = webhook_data.get('entry', [{}])[0]
        changes = entry.get('changes', [])
        page_id = entry.get('id')
        
        anuncios_creados = 0
        errores = []
        
        for change in changes:
            if change.get('field') == 'feed' and change.get('value', {}).get('verb') == 'add':
                valor = change.get('value', {})
                
                # Información de la publicación
                post_id = valor.get('post_id')
                message = valor.get('message', '')
                created_time = valor.get('created_time')
                item_type = valor.get('item')
                
                print(f"📝 Nueva publicación detectada:")
                print(f"   Page ID: {page_id}")
                print(f"   Post ID: {post_id}")
                print(f"   Mensaje: {message[:100]}...")
                print(f"   Tipo: {item_type}")
                
                # Guardar publicación en BD
                publicacion_data = {
                    'page_id': page_id,
                    'post_id': post_id,
                    'mensaje': message,
                    'tipo_item': item_type,
                    'created_time': created_time,
                    'webhook_data': json.dumps(valor),
                    'procesada': False,
                    'creada_en': datetime.utcnow().isoformat()
                }
                
                try:
                    supabase.table('meta_publicaciones_webhook').insert(publicacion_data).execute()
                    print(f"✅ Publicación guardada en BD")
                except Exception as e:
                    print(f"❌ Error guardando publicación: {e}")
                
                # Buscar automatizaciones para esta página
                automatizaciones = supabase.table('meta_ads_automatizaciones') \
                    .select('*') \
                    .eq('page_id', page_id) \
                    .eq('activa', True) \
                    .execute()
                
                print(f"🔍 Automatizaciones encontradas: {len(automatizaciones.data or [])}")
                
                for automatizacion in automatizaciones.data or []:
                    try:
                        # Procesar automatización
                        resultado = aplicar_automatizacion(automatizacion, post_id, message, valor)
                        
                        if resultado['ok']:
                            anuncios_creados += 1
                            print(f"✅ Anuncio creado por automatización {automatizacion['nombre']}")
                        else:
                            errores.append(f"Error en automatización {automatizacion['nombre']}: {resultado['error']}")
                            print(f"❌ {errores[-1]}")
                    
                    except Exception as e:
                        error_msg = f"Error procesando automatización {automatizacion.get('nombre', 'N/A')}: {str(e)}"
                        errores.append(error_msg)
                        print(f"❌ {error_msg}")
                
                # Marcar como procesada
                try:
                    supabase.table('meta_publicaciones_webhook') \
                        .update({'procesada': True, 'procesada_en': datetime.utcnow().isoformat()}) \
                        .eq('post_id', post_id) \
                        .execute()
                except Exception as e:
                    print(f"⚠️ Error marcando publicación como procesada: {e}")
        
        return {
            'ok': True,
            'anuncios_creados': anuncios_creados,
            'errores': errores,
            'message': f'Procesamiento completado: {anuncios_creados} anuncios creados'
        }
        
    except Exception as e:
        error_msg = f'Error general procesando webhook: {str(e)}'
        print(f"💥 {error_msg}")
        return {'ok': False, 'error': error_msg}

def aplicar_automatizacion(automatizacion, post_id, mensaje, webhook_valor):
    """
    Aplica una automatización específica a una publicación
    
    Args:
        automatizacion (dict): Datos de la automatización
        post_id (str): ID de la publicación
        mensaje (str): Contenido de la publicación
        webhook_valor (dict): Datos completos del webhook
        
    Returns:
        dict: Resultado de la aplicación
    """
    try:
        print(f"🎯 Aplicando automatización: {automatizacion['nombre']}")
        
        # Parsear reglas
        try:
            reglas = json.loads(automatizacion.get('reglas_json', '{}'))
        except:
            reglas = {}
        
        filtros_contenido = reglas.get('filtros_contenido', {})
        plantilla_anuncio = reglas.get('plantilla_anuncio', {})
        
        # Aplicar filtros de contenido
        if not evaluar_filtros_contenido(mensaje, webhook_valor, filtros_contenido):
            return {'ok': False, 'error': 'Publicación no cumple filtros de contenido'}
        
        print(f"✅ Publicación cumple filtros de contenido")
        
        # Obtener detalles adicionales de la publicación desde Graph API
        detalles_publicacion = obtener_detalles_publicacion(post_id)
        
        if not detalles_publicacion:
            return {'ok': False, 'error': 'No se pudieron obtener detalles de la publicación'}
        
        # Crear anuncio basado en la publicación
        resultado_anuncio = crear_anuncio_desde_publicacion(
            automatizacion,
            post_id,
            mensaje,
            detalles_publicacion,
            plantilla_anuncio
        )
        
        return resultado_anuncio
        
    except Exception as e:
        return {'ok': False, 'error': f'Error aplicando automatización: {str(e)}'}

def evaluar_filtros_contenido(mensaje, webhook_valor, filtros):
    """
    Evalúa si una publicación cumple con los filtros de contenido
    
    Args:
        mensaje (str): Contenido de la publicación
        webhook_valor (dict): Datos del webhook
        filtros (dict): Filtros a aplicar
        
    Returns:
        bool: True si cumple los filtros
    """
    try:
        # Filtro por palabras clave
        palabras_clave = filtros.get('palabras_clave', [])
        if palabras_clave:
            mensaje_lower = mensaje.lower()
            if not any(palabra.lower() in mensaje_lower for palabra in palabras_clave):
                print(f"❌ No contiene palabras clave: {palabras_clave}")
                return False
        
        # Filtro por palabras excluidas
        palabras_excluidas = filtros.get('palabras_excluidas', [])
        if palabras_excluidas:
            mensaje_lower = mensaje.lower()
            if any(palabra.lower() in mensaje_lower for palabra in palabras_excluidas):
                print(f"❌ Contiene palabras excluidas: {palabras_excluidas}")
                return False
        
        # Filtro por tipo de contenido
        tipo_contenido = filtros.get('tipo_contenido', [])
        if tipo_contenido:
            # Detectar tipo basado en webhook_valor
            tiene_imagen = 'photo' in str(webhook_valor).lower()
            tiene_video = 'video' in str(webhook_valor).lower()
            es_texto = not tiene_imagen and not tiene_video
            
            contenido_detectado = []
            if tiene_imagen:
                contenido_detectado.append('imagen')
            if tiene_video:
                contenido_detectado.append('video')
            if es_texto:
                contenido_detectado.append('texto')
            
            if not any(tipo in contenido_detectado for tipo in tipo_contenido):
                print(f"❌ Tipo de contenido no coincide. Detectado: {contenido_detectado}, Requerido: {tipo_contenido}")
                return False
        
        # Filtro por hashtags
        hashtags_requeridos = filtros.get('hashtags_requeridos', [])
        if hashtags_requeridos:
            hashtags_en_mensaje = re.findall(r'#\w+', mensaje.lower())
            if not any(hashtag.lower() in hashtags_en_mensaje for hashtag in hashtags_requeridos):
                print(f"❌ No contiene hashtags requeridos: {hashtags_requeridos}")
                return False
        
        # Filtro por longitud mínima
        longitud_minima = filtros.get('longitud_minima', 0)
        if len(mensaje) < longitud_minima:
            print(f"❌ Mensaje muy corto. Longitud: {len(mensaje)}, Mínimo: {longitud_minima}")
            return False
        
        print(f"✅ Todos los filtros de contenido superados")
        return True
        
    except Exception as e:
        print(f"❌ Error evaluando filtros: {e}")
        return False

def obtener_detalles_publicacion(post_id):
    """
    Obtiene detalles adicionales de una publicación desde la Graph API
    
    Args:
        post_id (str): ID de la publicación
        
    Returns:
        dict: Detalles de la publicación o None
    """
    try:
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            print("❌ Token de acceso no encontrado")
            return None
        
        # Obtener detalles de la publicación
        url = f"https://graph.facebook.com/v19.0/{post_id}"
        params = {
            'access_token': access_token,
            'fields': 'id,message,description,picture,full_picture,source,type,attachments{media,media_type,subattachments},permalink_url,created_time'
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Detalles de publicación obtenidos: {data.get('type', 'unknown')}")
            return data
        else:
            print(f"❌ Error obteniendo detalles: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en obtener_detalles_publicacion: {e}")
        return None

def crear_anuncio_desde_publicacion(automatizacion, post_id, mensaje, detalles_publicacion, plantilla_anuncio):
    """
    Crea un anuncio de Meta Ads basado en una publicación
    
    Args:
        automatizacion (dict): Datos de la automatización
        post_id (str): ID de la publicación
        mensaje (str): Contenido de la publicación
        detalles_publicacion (dict): Detalles adicionales de la publicación
        plantilla_anuncio (dict): Plantilla para el anuncio
        
    Returns:
        dict: Resultado de la creación del anuncio
    """
    try:
        print(f"🎨 Creando anuncio desde publicación {post_id}")
        
        access_token = os.getenv('META_ACCESS_TOKEN')
        if not access_token:
            return {'ok': False, 'error': 'Token de acceso no encontrado'}
        
        # Preparar datos del anuncio
        ad_account_id = automatizacion['ad_account_id']
        adset_id = automatizacion['adset_id']
        
        # Generar nombre único para el anuncio
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ad_name = f"Auto_{automatizacion['nombre']}_{timestamp}"
        
        # Preparar creative basado en la publicación
        creative_data = preparar_creative_desde_publicacion(
            detalles_publicacion, 
            mensaje, 
            plantilla_anuncio,
            automatizacion['page_id']
        )
        
        if not creative_data:
            return {'ok': False, 'error': 'No se pudo preparar creative desde publicación'}
        
        # Crear creative en Meta
        creative_result = crear_creative_meta(ad_account_id, creative_data, access_token)
        
        if not creative_result['ok']:
            return {'ok': False, 'error': f'Error creando creative: {creative_result["error"]}'}
        
        creative_id = creative_result['creative_id']
        
        # Crear anuncio en Meta
        anuncio_result = crear_anuncio_meta(
            ad_account_id,
            adset_id,
            creative_id,
            ad_name,
            access_token
        )
        
        if not anuncio_result['ok']:
            return {'ok': False, 'error': f'Error creando anuncio: {anuncio_result["error"]}'}
        
        ad_id = anuncio_result['ad_id']
        
        # Guardar registro de anuncio automatizado
        registro_data = {
            'automatizacion_id': automatizacion['id'],
            'post_id': post_id,
            'ad_id': ad_id,
            'creative_id': creative_id,
            'nombre_anuncio': ad_name,
            'mensaje_original': mensaje,
            'detalles_publicacion': json.dumps(detalles_publicacion),
            'creado_en': datetime.utcnow().isoformat()
        }
        
        try:
            supabase.table('meta_anuncios_automatizados').insert(registro_data).execute()
            print(f"✅ Registro de anuncio automatizado guardado")
        except Exception as e:
            print(f"⚠️ Error guardando registro: {e}")
        
        return {
            'ok': True,
            'ad_id': ad_id,
            'creative_id': creative_id,
            'message': f'Anuncio "{ad_name}" creado exitosamente desde publicación {post_id}'
        }
        
    except Exception as e:
        return {'ok': False, 'error': f'Error creando anuncio desde publicación: {str(e)}'}

def preparar_creative_desde_publicacion(detalles_publicacion, mensaje, plantilla_anuncio, page_id):
    """
    Prepara los datos del creative basado en la publicación
    
    Args:
        detalles_publicacion (dict): Detalles de la publicación
        mensaje (str): Mensaje de la publicación
        plantilla_anuncio (dict): Plantilla del anuncio
        page_id (str): ID de la página
        
    Returns:
        dict: Datos del creative preparados
    """
    try:
        # Obtener imagen principal
        imagen_url = detalles_publicacion.get('full_picture') or detalles_publicacion.get('picture')
        
        # Preparar texto del anuncio
        texto_anuncio = plantilla_anuncio.get('texto_personalizado', mensaje)
        if not texto_anuncio:
            texto_anuncio = mensaje
        
        # Preparar headline
        headline = plantilla_anuncio.get('headline', '')
        if not headline:
            # Generar headline automático (primeras palabras del mensaje)
            palabras = mensaje.split()[:5]
            headline = ' '.join(palabras) + ('...' if len(palabras) >= 5 else '')
        
        # Preparar descripción
        description = plantilla_anuncio.get('description', '')
        
        # Preparar call to action
        call_to_action_type = plantilla_anuncio.get('call_to_action', 'LEARN_MORE')
        
        # Preparar link
        link_url = plantilla_anuncio.get('link_url') or detalles_publicacion.get('permalink_url')
        
        creative_data = {
            'page_id': page_id,
            'imagen_url': imagen_url,
            'texto_anuncio': texto_anuncio,
            'headline': headline,
            'description': description,
            'call_to_action_type': call_to_action_type,
            'link_url': link_url,
            'tipo_publicacion': detalles_publicacion.get('type', 'status')
        }
        
        print(f"🎨 Creative preparado: {creative_data}")
        return creative_data
        
    except Exception as e:
        print(f"❌ Error preparando creative: {e}")
        return None

def crear_creative_meta(ad_account_id, creative_data, access_token):
    """
    Crea un creative en Meta Ads
    
    Args:
        ad_account_id (str): ID de la cuenta publicitaria
        creative_data (dict): Datos del creative
        access_token (str): Token de acceso
        
    Returns:
        dict: Resultado de la creación
    """
    try:
        url = f"https://graph.facebook.com/v19.0/act_{ad_account_id}/adcreatives"
        
        # Preparar objeto story
        object_story_spec = {
            'page_id': creative_data['page_id'],
            'link_data': {
                'message': creative_data['texto_anuncio'],
                'link': creative_data['link_url'],
                'name': creative_data['headline'],
                'description': creative_data['description'],
                'call_to_action': {
                    'type': creative_data['call_to_action_type']
                }
            }
        }
        
        # Agregar imagen si está disponible
        if creative_data.get('imagen_url'):
            object_story_spec['link_data']['picture'] = creative_data['imagen_url']
        
        params = {
            'access_token': access_token,
            'name': f"Creative_Auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'object_story_spec': json.dumps(object_story_spec)
        }
        
        response = requests.post(url, data=params, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            creative_id = result.get('id')
            print(f"✅ Creative creado: {creative_id}")
            return {'ok': True, 'creative_id': creative_id}
        else:
            print(f"❌ Error creando creative: {response.status_code} - {response.text}")
            return {'ok': False, 'error': f'HTTP {response.status_code}: {response.text}'}
            
    except Exception as e:
        return {'ok': False, 'error': f'Error en crear_creative_meta: {str(e)}'}

def crear_anuncio_meta(ad_account_id, adset_id, creative_id, ad_name, access_token):
    """
    Crea un anuncio en Meta Ads
    
    Args:
        ad_account_id (str): ID de la cuenta publicitaria
        adset_id (str): ID del conjunto de anuncios
        creative_id (str): ID del creative
        ad_name (str): Nombre del anuncio
        access_token (str): Token de acceso
        
    Returns:
        dict: Resultado de la creación
    """
    try:
        url = f"https://graph.facebook.com/v19.0/act_{ad_account_id}/ads"
        
        params = {
            'access_token': access_token,
            'name': ad_name,
            'adset_id': adset_id,
            'creative': json.dumps({'creative_id': creative_id}),
            'status': 'ACTIVE'
        }
        
        response = requests.post(url, data=params, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            ad_id = result.get('id')
            print(f"✅ Anuncio creado: {ad_id}")
            return {'ok': True, 'ad_id': ad_id}
        else:
            print(f"❌ Error creando anuncio: {response.status_code} - {response.text}")
            return {'ok': False, 'error': f'HTTP {response.status_code}: {response.text}'}
            
    except Exception as e:
        return {'ok': False, 'error': f'Error en crear_anuncio_meta: {str(e)}'}

# ============================================================================
# FUNCIONES DE ESTADÍSTICAS Y MONITOREO
# ============================================================================

def obtener_estadisticas_automatizaciones(nombre_nora):
    """
    Obtiene estadísticas de las automatizaciones
    
    Args:
        nombre_nora (str): Nombre de la instancia Nora
        
    Returns:
        dict: Estadísticas
    """
    try:
        # Estadísticas de automatizaciones
        automatizaciones = supabase.table('meta_ads_automatizaciones') \
            .select('*') \
            .eq('nombre_nora', nombre_nora) \
            .execute()
        
        total_automatizaciones = len(automatizaciones.data or [])
        automatizaciones_activas = len([a for a in automatizaciones.data or [] if a.get('activa')])
        
        # Estadísticas de anuncios automatizados (últimos 30 días)
        fecha_limite = (datetime.now() - timedelta(days=30)).isoformat()
        
        anuncios_automatizados = supabase.table('meta_anuncios_automatizados') \
            .select('*, meta_ads_automatizaciones!inner(nombre_nora)') \
            .eq('meta_ads_automatizaciones.nombre_nora', nombre_nora) \
            .gte('creado_en', fecha_limite) \
            .execute()
        
        anuncios_creados_30d = len(anuncios_automatizados.data or [])
        
        # Estadísticas de publicaciones procesadas
        publicaciones_procesadas = supabase.table('meta_publicaciones_webhook') \
            .select('*') \
            .eq('procesada', True) \
            .gte('creada_en', fecha_limite) \
            .execute()
        
        publicaciones_procesadas_30d = len(publicaciones_procesadas.data or [])
        
        return {
            'total_automatizaciones': total_automatizaciones,
            'automatizaciones_activas': automatizaciones_activas,
            'anuncios_creados_30d': anuncios_creados_30d,
            'publicaciones_procesadas_30d': publicaciones_procesadas_30d
        }
        
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        return {
            'total_automatizaciones': 0,
            'automatizaciones_activas': 0,
            'anuncios_creados_30d': 0,
            'publicaciones_procesadas_30d': 0
        }

def obtener_historial_anuncios_automatizados(nombre_nora, limite=50):
    """
    Obtiene el historial de anuncios creados automáticamente
    
    Args:
        nombre_nora (str): Nombre de la instancia Nora
        limite (int): Número máximo de registros
        
    Returns:
        list: Lista de anuncios automatizados
    """
    try:
        resultado = supabase.table('meta_anuncios_automatizados') \
            .select('*, meta_ads_automatizaciones!inner(nombre, nombre_nora)') \
            .eq('meta_ads_automatizaciones.nombre_nora', nombre_nora) \
            .order('creado_en', desc=True) \
            .limit(limite) \
            .execute()
        
        anuncios = resultado.data or []
        
        # Enriquecer datos
        for anuncio in anuncios:
            # Formatear fecha
            if anuncio.get('creado_en'):
                try:
                    fecha = datetime.fromisoformat(anuncio['creado_en'].replace('Z', '+00:00'))
                    anuncio['creado_en_fmt'] = fecha.strftime('%d/%m/%Y %H:%M')
                except:
                    anuncio['creado_en_fmt'] = 'N/A'
            
            # Información de la automatización
            auto_info = anuncio.get('meta_ads_automatizaciones', {})
            anuncio['nombre_automatizacion'] = auto_info.get('nombre', 'N/A')
            
            # Truncar mensaje original
            mensaje_original = anuncio.get('mensaje_original', '')
            anuncio['mensaje_truncado'] = mensaje_original[:100] + ('...' if len(mensaje_original) > 100 else '')
        
        return anuncios
        
    except Exception as e:
        print(f"Error obteniendo historial: {e}")
        return []
