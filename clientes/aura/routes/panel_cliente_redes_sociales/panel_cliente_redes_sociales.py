# 🔥 TEST AUTO-RELOAD
from flask import Blueprint, render_template, request, jsonify
from clientes.aura.utils.supabase_client import supabase
from datetime import datetime, timedelta

def get_nombre_nora():
    """Helper para extraer nombre_nora de request.view_args o URL"""
    nombre_nora = request.view_args.get("nombre_nora") if request.view_args else None
    
    # Si nombre_nora es None, intentar extraerlo de la URL
    if not nombre_nora:
        path_parts = request.path.split('/')
        if len(path_parts) >= 3 and path_parts[1] == 'panel_cliente':
            nombre_nora = path_parts[2]
    
    return nombre_nora

panel_cliente_redes_sociales_bp = Blueprint("panel_cliente_redes_sociales_bp", __name__, url_prefix="/panel_cliente/<nombre_nora>/redes_sociales")

@panel_cliente_redes_sociales_bp.route("/")
def panel_cliente_redes_sociales():
    """Panel principal de gestión de redes sociales"""
    nombre_nora = get_nombre_nora()
    return render_template("panel_cliente_redes_sociales/index.html", nombre_nora=nombre_nora)

@panel_cliente_redes_sociales_bp.route("/conectar/<red_social>")
def conectar_red_social(red_social):
    """Iniciar proceso de conexión con una red social específica"""
    nombre_nora = get_nombre_nora()
    redes_disponibles = ['facebook', 'instagram', 'youtube', 'tiktok', 'x', 'threads', 'linkedin', 'pinterest']
    
    if red_social.lower() not in redes_disponibles:
        return jsonify({'error': 'Red social no soportada'}), 400
    
    # Por ahora, retornamos un mensaje de que la función está en desarrollo
    return jsonify({
        'message': f'Conexión con {red_social.title()} estará disponible próximamente',
        'red_social': red_social,
        'status': 'en_desarrollo'
    })

@panel_cliente_redes_sociales_bp.route("/estadisticas")
def estadisticas_redes_sociales():
    """Ver estadísticas consolidadas de todas las redes sociales"""
    nombre_nora = get_nombre_nora()
    return render_template("panel_cliente_redes_sociales/estadisticas.html", nombre_nora=nombre_nora)

@panel_cliente_redes_sociales_bp.route("/programar")
def programar_publicaciones():
    """Interface para programar publicaciones en múltiples redes"""
    nombre_nora = get_nombre_nora()
    return render_template("panel_cliente_redes_sociales/programar.html", nombre_nora=nombre_nora)

@panel_cliente_redes_sociales_bp.route("/calendario")
def calendario_contenido():
    """Vista de calendario editorial"""
    nombre_nora = get_nombre_nora()
    return render_template("panel_cliente_redes_sociales/calendario.html", nombre_nora=nombre_nora)

@panel_cliente_redes_sociales_bp.route("/facebook")
def gestionar_facebook():
    """Panel de gestión de páginas de Facebook"""
    nombre_nora = get_nombre_nora()
    
    try:
        # Obtener todas las páginas de Facebook de la base de datos
        response = supabase.table('facebook_paginas').select('*').eq('activa', True).order('nombre_pagina').execute()
        paginas_facebook = response.data if response.data else []
        
        # Verificar estado webhook para cada página
        for pagina in paginas_facebook:
            # Determinar estado webhook real basado en actividad reciente
            webhook_activo = pagina.get('estado_webhook') == 'activa'
            pagina['estado_webhook_real'] = 'activa' if webhook_activo else 'inactiva'
        
        return render_template("panel_cliente_redes_sociales/facebook.html", 
                             nombre_nora=nombre_nora, 
                             paginas=paginas_facebook)
    except Exception as e:
        print(f"Error en gestionar_facebook: {e}")
        return render_template("panel_cliente_redes_sociales/facebook.html",
                             nombre_nora=nombre_nora,
                             paginas=[])

@panel_cliente_redes_sociales_bp.route("/facebook/<page_id>")
def detalle_pagina_facebook(page_id):
    """Detalle completo de una página específica de Facebook"""
    nombre_nora = get_nombre_nora()
    
    # Debug para ver qué está pasando
    print(f"DEBUG - nombre_nora: {nombre_nora}")
    print(f"DEBUG - request.path: {request.path}")
    
    try:
        # Obtener datos de la página
        page_result = supabase.table('facebook_paginas').select('*').eq('page_id', page_id).execute()
        
        if not page_result.data:
            return jsonify({'error': 'Página no encontrada'}), 404
        
        pagina = page_result.data[0]
        
        # 🎯 ARREGLAR: Asegurar que todos los campos esperados por el template estén presentes
        # Estado webhook simplificado
        webhook_activo = pagina.get('estado_webhook') == 'activa'
        pagina['estado_webhook'] = 'activa' if webhook_activo else 'inactiva'
        
        # 📸 Mapear campos de imágenes CORRECTAMENTE según la BD
        pagina['picture'] = pagina.get('foto_perfil_url')  # BD: foto_perfil_url -> Template: picture
        pagina['cover_photo'] = pagina.get('foto_portada_url')  # BD: foto_portada_url -> Template: cover_photo
        
        # ✅ Mejorar descripción si está vacía
        descripcion_actual = pagina.get('descripcion', '') or ''
        if not descripcion_actual or descripcion_actual.strip() == '':
            if pagina.get('categoria'):
                pagina['descripcion'] = f"Página de {pagina.get('categoria')} con {pagina.get('seguidores', 0):,} seguidores."
            else:
                pagina['descripcion'] = f"Página de Facebook con {pagina.get('seguidores', 0):,} seguidores."
        
        # 📋 Los demás campos ya están con nombres correctos en la BD
        # descripcion, website, telefono, email, verificada, categoria, ciudad, pais, username ya están OK
        # seguidores, likes ya están OK
        
        # Obtener conteos adicionales para las estadísticas
        try:
            # 📊 Calcular métricas de engagement avanzadas
            pub_result = supabase.table('meta_publicaciones_webhook').select('*').eq('page_id', page_id).in_('tipo_item', ['status', 'photo', 'video', 'link']).execute()
            pagina['total_publicaciones'] = len(pub_result.data) if pub_result.data else 0
            
            # Contar comentarios de esta página (tipo comment)
            com_result = supabase.table('meta_publicaciones_webhook').select('*').eq('page_id', page_id).eq('tipo_item', 'comment').execute()
            pagina['total_comentarios'] = len(com_result.data) if com_result.data else 0
            
            # Contar reacciones (tipo reaction)
            reaction_result = supabase.table('meta_publicaciones_webhook').select('*').eq('page_id', page_id).eq('tipo_item', 'reaction').execute()
            pagina['total_reacciones'] = len(reaction_result.data) if reaction_result.data else 0
            
            # Calcular engagement rate
            total_interacciones = pagina['total_comentarios'] + pagina['total_reacciones']
            if pagina.get('seguidores', 0) > 0 and pagina['total_publicaciones'] > 0:
                engagement_rate = round((total_interacciones / pagina.get('seguidores', 1)) * 100, 2)
            else:
                engagement_rate = 0
            pagina['engagement_rate'] = engagement_rate
            pagina['total_interacciones'] = total_interacciones
        except Exception as stats_error:
            print(f"Error obteniendo estadísticas: {stats_error}")
            pagina['total_publicaciones'] = 0
            pagina['total_comentarios'] = 0
        
        # 🐛 DEBUG: Mostrar qué datos estamos enviando
        print(f"📸 DEBUG - Datos de página enviados al template:")
        print(f"  - picture: {pagina.get('picture')}")
        print(f"  - cover_photo: {pagina.get('cover_photo')}")
        print(f"  - nombre_pagina: {pagina.get('nombre_pagina')}")
        print(f"  - descripcion: {pagina.get('descripcion')}")
        print(f"  - estado_webhook: {pagina.get('estado_webhook')}")
        print(f"  - foto_perfil_url (BD): {pagina.get('foto_perfil_url')}")
        print(f"  - foto_portada_url (BD): {pagina.get('foto_portada_url')}")
        print(f"  - verificada: {pagina.get('verificada')}")
        print(f"  - categoria: {pagina.get('categoria')}")
        print(f"  - username: {pagina.get('username')}")
        print(f"  - website: {pagina.get('website')}")
        print(f"  - email: {pagina.get('email')}")
        print(f"  - telefono: {pagina.get('telefono')}")
        print(f"  - seguidores: {pagina.get('seguidores')}")
        print(f"  - likes: {pagina.get('likes')}")
        
        # 🔍 Verificar si las URLs de imagen son válidas
        picture_url = pagina.get('picture')
        if picture_url:
            print(f"✅ Foto de perfil encontrada: {len(picture_url)} caracteres")
        else:
            print(f"❌ No hay foto de perfil")
            
        cover_url = pagina.get('cover_photo')
        if cover_url:
            print(f"✅ Foto de portada encontrada: {len(cover_url)} caracteres")
        else:
            print(f"❌ No hay foto de portada")
        
        # Renderizar template con todos los datos
        return render_template("panel_cliente_redes_sociales/facebook_detalle.html", 
                             nombre_nora=nombre_nora,
                             pagina=pagina)
        
    except Exception as e:
        print(f"Error en detalle página Facebook: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@panel_cliente_redes_sociales_bp.route("/facebook/<page_id>/vincular", methods=['POST'])
def vincular_pagina_cliente(page_id):
    """Vincular una página de Facebook a un cliente específico"""
    nombre_nora = get_nombre_nora()
    
    try:
        data = request.get_json()
        empresa_id = data.get('empresa_id')
        
        if not empresa_id:
            return jsonify({'success': False, 'error': 'ID de empresa requerido'}), 400
        
        # Actualizar la página con la empresa vinculada
        update_result = supabase.table('facebook_paginas').update({
            'empresa_id': empresa_id,
            'actualizado_en': datetime.now().isoformat()
        }).eq('page_id', page_id).execute()
        
        if update_result.data:
            return jsonify({'success': True, 'message': 'Página vinculada exitosamente'})
        else:
            return jsonify({'success': False, 'error': 'No se pudo vincular la página'})
            
    except Exception as e:
        print(f"Error al vincular página: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@panel_cliente_redes_sociales_bp.route("/facebook/<page_id>/desvincular", methods=['POST'])
def desvincular_pagina_cliente(page_id):
    """Desvincular una página de Facebook de su cliente actual"""
    nombre_nora = get_nombre_nora()
    
    try:
        # Quitar la vinculación con la empresa
        update_result = supabase.table('facebook_paginas').update({
            'empresa_id': None,
            'actualizado_en': datetime.now().isoformat()
        }).eq('page_id', page_id).execute()
        
        if update_result.data:
            return jsonify({'success': True, 'message': 'Página desvinculada exitosamente'})
        else:
            return jsonify({'success': False, 'error': 'No se pudo desvincular la página'})
            
    except Exception as e:
        print(f"Error al desvincular página: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@panel_cliente_redes_sociales_bp.route("/facebook/<page_id>/webhook/suscribir", methods=['POST'])
def suscribir_webhook_facebook(page_id):
    """Suscribir webhook de una página de Facebook"""
    nombre_nora = get_nombre_nora()
    
    try:
        # Actualizar estado del webhook
        update_result = supabase.table('facebook_paginas').update({
            'estado_webhook': 'activa',
            'actualizado_en': datetime.now().isoformat()
        }).eq('page_id', page_id).execute()
        
        if update_result.data:
            return jsonify({'success': True, 'message': 'Webhook suscrito exitosamente'})
        else:
            return jsonify({'success': False, 'error': 'No se pudo suscribir el webhook'})
            
    except Exception as e:
        print(f"Error al suscribir webhook: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@panel_cliente_redes_sociales_bp.route("/facebook/<page_id>/webhook/desconectar", methods=['POST'])
def desconectar_webhook_facebook(page_id):
    """Desconectar webhook de una página de Facebook"""
    nombre_nora = get_nombre_nora()
    
    try:
        # Actualizar estado del webhook
        update_result = supabase.table('facebook_paginas').update({
            'estado_webhook': 'inactiva',
            'actualizado_en': datetime.now().isoformat()
        }).eq('page_id', page_id).execute()
        
        if update_result.data:
            return jsonify({'success': True, 'message': 'Webhook desconectado exitosamente'})
        else:
            return jsonify({'success': False, 'error': 'No se pudo desconectar el webhook'})
            
    except Exception as e:
        print(f"Error al desconectar webhook: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@panel_cliente_redes_sociales_bp.route("/facebook/<page_id>/api/estadisticas")
def api_estadisticas_facebook(page_id):
    """API para obtener estadísticas de una página de Facebook"""
    nombre_nora = get_nombre_nora()
    
    try:
        # Obtener estadísticas básicas
        response = supabase.table('facebook_paginas').select('*').eq('page_id', page_id).execute()
        
        if not response.data:
            return jsonify({'success': False, 'error': 'Página no encontrada'}), 404
            
        pagina = response.data[0]
        
        return jsonify({
            'success': True,
            'estadisticas': {
                'seguidores': pagina.get('seguidores', 0),
                'likes': pagina.get('likes', 0),
                'publicaciones': pagina.get('total_publicaciones', 0),
                'comentarios': pagina.get('total_comentarios', 0)
            }
        })
        
    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@panel_cliente_redes_sociales_bp.route("/facebook/<page_id>/api/publicaciones")
def api_publicaciones_facebook(page_id):
    """API para obtener publicaciones de una página de Facebook"""
    nombre_nora = get_nombre_nora()
    
    try:
        # Obtener publicaciones recientes (status, photo, video, link)
        response = supabase.table('meta_publicaciones_webhook').select('*').eq('page_id', page_id).in_('tipo_item', ['status', 'photo', 'video', 'link']).order('created_time', desc=True).limit(20).execute()
        publicaciones = response.data if response.data else []
        
        return jsonify({
            'success': True,
            'publicaciones': publicaciones,
            'total': len(publicaciones)
        })
        
    except Exception as e:
        print(f"Error al obtener publicaciones: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@panel_cliente_redes_sociales_bp.route("/facebook/<page_id>/api/comentarios")
def api_comentarios_facebook(page_id):
    """API para obtener comentarios de una página de Facebook"""
    nombre_nora = get_nombre_nora()
    
    try:
        # Obtener comentarios recientes (tipo comment)
        response = supabase.table('meta_publicaciones_webhook').select('*').eq('page_id', page_id).eq('tipo_item', 'comment').order('created_time', desc=True).limit(20).execute()
        comentarios = response.data if response.data else []
        
        return jsonify({
            'success': True,
            'comentarios': comentarios,
            'total': len(comentarios)
        })
        
    except Exception as e:
        print(f"Error al obtener comentarios: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@panel_cliente_redes_sociales_bp.route("/facebook/<page_id>/actividad")
def api_actividad_facebook(page_id):
    """API para obtener actividad reciente de una página de Facebook"""
    nombre_nora = get_nombre_nora()
    
    try:
        from datetime import datetime, timezone
        actividad = []
        
        # Obtener publicaciones recientes (status, photo, video, link) - últimas 5
        pub_response = supabase.table('meta_publicaciones_webhook').select('*').eq('page_id', page_id).in_('tipo_item', ['status', 'photo', 'video', 'link']).order('created_time', desc=True).limit(5).execute()
        if pub_response.data:
            for pub in pub_response.data:
                # 🕐 Formatear fecha correctamente
                fecha_formato = pub.get('created_time', '')
                try:
                    if fecha_formato:
                        # Convertir timestamp o ISO string a fecha legible
                        if fecha_formato.isdigit():
                            fecha_dt = datetime.fromtimestamp(int(fecha_formato), tz=timezone.utc)
                        else:
                            fecha_dt = datetime.fromisoformat(fecha_formato.replace('Z', '+00:00'))
                        fecha_formato = fecha_dt.strftime('%d %b %Y, %H:%M')
                    else:
                        fecha_formato = 'Fecha no disponible'
                except Exception as date_error:
                    print(f"Error procesando fecha {fecha_formato}: {date_error}")
                    fecha_formato = 'Fecha no disponible'
                
                tipo_publicacion = pub.get('tipo_item', 'post')
                tipo_map = {
                    'status': 'estado',
                    'photo': 'foto', 
                    'video': 'video',
                    'link': 'enlace'
                }
                tipo_humano = tipo_map.get(tipo_publicacion, tipo_publicacion)
                
                actividad.append({
                    'tipo': f'Nueva publicación ({tipo_humano})',
                    'descripcion': pub.get('mensaje', 'Sin mensaje')[:100] + '...' if pub.get('mensaje', '') else 'Publicación sin texto',
                    'fecha': fecha_formato
                })
        
        # Obtener comentarios recientes (tipo comment) - últimos 5
        com_response = supabase.table('meta_publicaciones_webhook').select('*').eq('page_id', page_id).eq('tipo_item', 'comment').order('created_time', desc=True).limit(5).execute()
        if com_response.data:
            for com in com_response.data:
                # 🕐 Formatear fecha correctamente
                fecha_formato = com.get('created_time', '')
                try:
                    if fecha_formato:
                        if fecha_formato.isdigit():
                            fecha_dt = datetime.fromtimestamp(int(fecha_formato), tz=timezone.utc)
                        else:
                            fecha_dt = datetime.fromisoformat(fecha_formato.replace('Z', '+00:00'))
                        fecha_formato = fecha_dt.strftime('%d %b %Y, %H:%M')
                    else:
                        fecha_formato = 'Fecha no disponible'
                except Exception as date_error:
                    print(f"Error procesando fecha comentario {fecha_formato}: {date_error}")
                    fecha_formato = 'Fecha no disponible'
                
                # Extraer nombre del autor desde webhook_data si existe
                autor_nombre = 'Usuario'
                if com.get('webhook_data') and isinstance(com.get('webhook_data'), dict):
                    autor_nombre = com['webhook_data'].get('from', {}).get('name', 'Usuario')
                    
                actividad.append({
                    'tipo': 'Nuevo comentario',
                    'descripcion': f"{autor_nombre}: {com.get('mensaje', 'Sin mensaje')[:100]}...",
                    'fecha': fecha_formato
                })
        
        # Obtener reacciones recientes (tipo reaction) si las hay
        reaction_response = supabase.table('meta_publicaciones_webhook').select('*').eq('page_id', page_id).eq('tipo_item', 'reaction').order('created_time', desc=True).limit(3).execute()
        if reaction_response.data:
            for reaction in reaction_response.data:
                # 🕐 Formatear fecha correctamente
                fecha_formato = reaction.get('created_time', '')
                try:
                    if fecha_formato:
                        if fecha_formato.isdigit():
                            fecha_dt = datetime.fromtimestamp(int(fecha_formato), tz=timezone.utc)
                        else:
                            fecha_dt = datetime.fromisoformat(fecha_formato.replace('Z', '+00:00'))
                        fecha_formato = fecha_dt.strftime('%d %b %Y, %H:%M')
                    else:
                        fecha_formato = 'Fecha no disponible'
                except Exception as date_error:
                    print(f"Error procesando fecha reacción {fecha_formato}: {date_error}")
                    fecha_formato = 'Fecha no disponible'
                
                actividad.append({
                    'tipo': 'Nueva reacción',
                    'descripcion': f"Reacción en publicación",
                    'fecha': fecha_formato
                })
        
        # Si no hay actividad, crear mensaje informativo
        if not actividad:
            actividad.append({
                'tipo': 'Sin actividad reciente',
                'descripcion': 'No se han registrado eventos recientes en esta página',
                'fecha': 'N/A'
            })
        
        # Ordenar por fecha descendente usando el timestamp original
        def fecha_sort_key(item):
            fecha_str = item.get('fecha', '')
            if fecha_str == 'N/A' or fecha_str == 'Fecha no disponible':
                return 0
            try:
                return datetime.strptime(fecha_str, '%d %b %Y, %H:%M').timestamp()
            except:
                return 0
        
        actividad.sort(key=fecha_sort_key, reverse=True)
        
        return jsonify({
            'success': True,
            'actividad': actividad[:10]  # Solo las 10 más recientes
        })
        
    except Exception as e:
        print(f"Error al obtener actividad: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@panel_cliente_redes_sociales_bp.route("/facebook/<page_id>/api/reacciones")
def api_reacciones_facebook(page_id):
    """API para obtener reacciones de una página de Facebook"""
    nombre_nora = get_nombre_nora()
    
    try:
        # Obtener reacciones recientes (tipo reaction)
        response = supabase.table('meta_publicaciones_webhook').select('*').eq('page_id', page_id).eq('tipo_item', 'reaction').order('created_time', desc=True).limit(20).execute()
        reacciones = response.data if response.data else []
        
        return jsonify({
            'success': True,
            'reacciones': reacciones,
            'total': len(reacciones)
        })
        
    except Exception as e:
        print(f"Error al obtener reacciones: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@panel_cliente_redes_sociales_bp.route("/facebook/<page_id>/webhook/activar", methods=['POST'])
def activar_webhook_facebook(page_id):
    """Activar webhook de una página de Facebook"""
    nombre_nora = get_nombre_nora()
    
    try:
        # Actualizar estado del webhook
        update_result = supabase.table('facebook_paginas').update({
            'estado_webhook': 'activa',
            'actualizado_en': datetime.now().isoformat()
        }).eq('page_id', page_id).execute()
        
        if update_result.data:
            return jsonify({'success': True, 'message': 'Webhook activado exitosamente'})
        else:
            return jsonify({'success': False, 'error': 'No se pudo activar el webhook'})
            
    except Exception as e:
        print(f"Error al activar webhook: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@panel_cliente_redes_sociales_bp.route("/facebook/<page_id>/webhook/desactivar", methods=['POST'])
def desactivar_webhook_facebook(page_id):
    """Desactivar webhook de una página de Facebook"""
    nombre_nora = get_nombre_nora()
    
    try:
        # Actualizar estado del webhook
        update_result = supabase.table('facebook_paginas').update({
            'estado_webhook': 'inactiva',
            'actualizado_en': datetime.now().isoformat()
        }).eq('page_id', page_id).execute()
        
        if update_result.data:
            return jsonify({'success': True, 'message': 'Webhook desactivado exitosamente'})
        else:
            return jsonify({'success': False, 'error': 'No se pudo desactivar el webhook'})
            
    except Exception as e:
        print(f"Error al desactivar webhook: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@panel_cliente_redes_sociales_bp.route("/facebook/<page_id>/estado")
def verificar_estado_facebook(page_id):
    """Verificar estado actual del webhook de una página"""
    nombre_nora = get_nombre_nora()
    
    try:
        # Obtener estado actual
        response = supabase.table('facebook_paginas').select('estado_webhook, actualizado_en').eq('page_id', page_id).execute()
        
        if response.data:
            pagina = response.data[0]
            return jsonify({
                'success': True,
                'estado': pagina.get('estado_webhook', 'inactiva'),
                'ultima_actualizacion': pagina.get('actualizado_en', '')
            })
        else:
            return jsonify({'success': False, 'error': 'Página no encontrada'})
            
    except Exception as e:
        print(f"Error al verificar estado: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

