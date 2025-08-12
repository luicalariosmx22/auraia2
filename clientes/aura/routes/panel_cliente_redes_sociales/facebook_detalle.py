"""
🔍 DETALLE DE PÁGINA FACEBOOK - MÓDULO SEPARADO
Funciones optimizadas para el detalle completo de páginas de Facebook
"""

from flask import Blueprint, render_template, request, jsonify
from clientes.aura.utils.supabase_client import supabase
from datetime import datetime, timedelta
import json

facebook_detalle_bp = Blueprint("facebook_detalle_bp", __name__, url_prefix="/facebook")

@facebook_detalle_bp.route("/<page_id>/detalle")
def detalle_pagina_facebook_optimizado(page_id):
    """Detalle completo de una página específica de Facebook - ULTRA OPTIMIZADO"""
    # Obtener nombre_nora desde la URL del parent blueprint
    full_path = request.full_path
    path_parts = request.path.split('/')
    
    # Buscar 'aura' en el path (o el nombre de la nora)
    nombre_nora = 'aura'  # Default, pero lo extraemos del path
    for i, part in enumerate(path_parts):
        if part == 'panel_cliente' and i + 1 < len(path_parts):
            nombre_nora = path_parts[i + 1]
            break
    
    try:
        # 🚀 CONSULTA OPTIMIZADA USANDO SUPABASE DIRECTO
        # Obtener datos de la página
        page_result = supabase.table('facebook_paginas').select(
            'page_id, nombre_pagina, username, seguidores, likes, verificada, '
            'categoria, descripcion, website, telefono, email, foto_perfil_url, '
            'foto_portada_url, estado_webhook, ultima_sincronizacion, empresa_id, '
            'empresas(id, nombre, descripcion)'
        ).eq('page_id', page_id).execute()
        
        if not page_result.data:
            return jsonify({'error': 'Página no encontrada'}), 404
        
        pagina = page_result.data[0]
        
        # 📊 Obtener estadísticas básicas en paralelo
        try:
            # Conteo de publicaciones
            pub_count = supabase.table('publicaciones_facebook').select(
                'id'
            ).eq('page_id', page_id).execute()
            total_publicaciones = len(pub_count.data) if pub_count.data else 0
        except:
            total_publicaciones = 0
            
        try:
            # Conteo de comentarios
            com_count = supabase.table('comentarios_facebook').select(
                'id'
            ).eq('page_id', page_id).execute()
            total_comentarios = len(com_count.data) if com_count.data else 0
        except:
            total_comentarios = 0
        
        # 📈 DATOS BÁSICOS OPTIMIZADOS
        empresa_data = pagina.get('empresas', {}) if pagina.get('empresas') else {}
        
        page_data = {
            'page_id': pagina.get('page_id'),
            'nombre_pagina': pagina.get('nombre_pagina'),
            'username': pagina.get('username'),
            'seguidores': pagina.get('seguidores', 0),
            'likes': pagina.get('likes', 0),
            'verificada': pagina.get('verificada', False),
            'categoria': pagina.get('categoria'),
            'descripcion': pagina.get('descripcion'),
            'website': pagina.get('website'),
            'telefono': pagina.get('telefono'),
            'email': pagina.get('email'),
            'foto_perfil_url': pagina.get('foto_perfil_url'),
            'foto_portada_url': pagina.get('foto_portada_url'),
            'estado_webhook': pagina.get('estado_webhook', 'inactivo'),
            'ultima_sincronizacion': pagina.get('ultima_sincronizacion'),
            
            # Empresa vinculada
            'empresa_id': pagina.get('empresa_id'),
            'nombre_empresa': empresa_data.get('nombre') if empresa_data else None,
            'empresa_descripcion': empresa_data.get('descripcion') if empresa_data else None,
            
            # Estadísticas
            'total_publicaciones': total_publicaciones,
            'total_comentarios': total_comentarios,
            'total_reacciones': 0  # Calculamos después si es necesario
        }
        
        # 🎨 RENDERIZAR TEMPLATE OPTIMIZADO
        return render_template(
            "panel_cliente_redes_sociales/facebook_detalle.html", 
            nombre_nora=nombre_nora,
            pagina=page_data,
            # 📱 Datos mínimos para carga inicial - el resto por AJAX
            carga_inicial=True
        )
        
    except Exception as e:
        print(f"Error en detalle página Facebook: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@facebook_detalle_bp.route("/<page_id>/api/publicaciones")
def api_publicaciones_paginadas(page_id):
    """API para cargar publicaciones de forma paginada"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    offset = (page - 1) * limit
    
    try:
        # 📄 PAGINACIÓN EFICIENTE
        result = supabase.table('publicaciones_facebook').select(
            'id, mensaje, tipo_publicacion, likes, comentarios, compartidos, '
            'fecha_publicacion, url_publicacion, imagen_url'
        ).eq('page_id', page_id).order(
            'fecha_publicacion', desc=True
        ).range(offset, offset + limit - 1).execute()
        
        return jsonify({
            'publicaciones': result.data,
            'page': page,
            'has_more': len(result.data) == limit
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@facebook_detalle_bp.route("/<page_id>/api/comentarios")
def api_comentarios_paginados(page_id):
    """API para cargar comentarios de forma paginada"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    offset = (page - 1) * limit
    
    try:
        result = supabase.table('comentarios_facebook').select(
            'id, mensaje, autor_nombre, fecha_comentario, likes_comentario'
        ).eq('page_id', page_id).order(
            'fecha_comentario', desc=True
        ).range(offset, offset + limit - 1).execute()
        
        return jsonify({
            'comentarios': result.data,
            'page': page,
            'has_more': len(result.data) == limit
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@facebook_detalle_bp.route("/<page_id>/api/estadisticas")
def api_estadisticas_avanzadas(page_id):
    """API para estadísticas avanzadas (carga bajo demanda)"""
    try:
        # 📊 ESTADÍSTICAS COMPLEJAS - SOLO CUANDO SE SOLICITEN
        fecha_limite = datetime.now() - timedelta(days=30)
        fecha_limite_str = fecha_limite.isoformat()
        
        # Obtener publicaciones del último mes
        publicaciones_mes = supabase.table('publicaciones_facebook').select(
            'id, likes, comentarios, fecha_publicacion'
        ).eq('page_id', page_id).gte(
            'fecha_publicacion', fecha_limite_str
        ).execute()
        
        # Calcular estadísticas
        if publicaciones_mes.data:
            total_pubs = len(publicaciones_mes.data)
            total_likes = sum(pub.get('likes', 0) for pub in publicaciones_mes.data)
            total_comentarios = sum(pub.get('comentarios', 0) for pub in publicaciones_mes.data)
            promedio_likes = total_likes / total_pubs if total_pubs > 0 else 0
            promedio_comentarios = total_comentarios / total_pubs if total_pubs > 0 else 0
            
            # Última publicación
            ultima_pub = max(pub.get('fecha_publicacion', '') for pub in publicaciones_mes.data) if publicaciones_mes.data else None
        else:
            total_pubs = 0
            total_likes = 0
            promedio_likes = 0
            promedio_comentarios = 0
            ultima_pub = None
        
        estadisticas = {
            'publicaciones_ultimo_mes': total_pubs,
            'promedio_likes': round(promedio_likes, 2),
            'promedio_comentarios': round(promedio_comentarios, 2),
            'total_likes_mes': total_likes,
            'ultima_publicacion': ultima_pub
        }
        
        return jsonify(estadisticas)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@facebook_detalle_bp.route("/<page_id>/webhook/status")
def verificar_estado_webhook(page_id):
    """Verificar estado del webhook en tiempo real (API separada)"""
    try:
        # 🔍 VERIFICACIÓN LIGERA DEL WEBHOOK
        page_result = supabase.table('facebook_paginas').select(
            'estado_webhook, access_token, ultima_sincronizacion'
        ).eq('page_id', page_id).execute()
        
        if not page_result.data:
            return jsonify({'error': 'Página no encontrada'}), 404
        
        pagina = page_result.data[0]
        
        webhook_status = {
            'estado': pagina.get('estado_webhook', 'inactivo'),
            'activo': pagina.get('estado_webhook') == 'activa',
            'tiene_token': bool(pagina.get('access_token')),
            'ultima_sync': pagina.get('ultima_sincronizacion'),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(webhook_status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
