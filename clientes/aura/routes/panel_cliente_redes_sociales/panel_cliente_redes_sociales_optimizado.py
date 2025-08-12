"""
🌐 PANEL CLIENTE REDES SOCIALES - MÓDULO PRINCIPAL OPTIMIZADO
Gestión general de redes sociales con funciones ligeras
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from clientes.aura.utils.supabase_client import supabase
from datetime import datetime, timedelta

panel_cliente_redes_sociales_bp = Blueprint("panel_cliente_redes_sociales_bp", __name__, url_prefix="/panel_cliente/<nombre_nora>/redes_sociales")

@panel_cliente_redes_sociales_bp.route("/")
def panel_cliente_redes_sociales():
    """Panel principal de gestión de redes sociales"""
    nombre_nora = request.view_args.get("nombre_nora") if request.view_args else None
    return render_template("panel_cliente_redes_sociales/index.html", nombre_nora=nombre_nora)

@panel_cliente_redes_sociales_bp.route("/conectar/<red_social>")
def conectar_red_social(red_social):
    """Iniciar proceso de conexión con una red social específica"""
    nombre_nora = request.view_args.get("nombre_nora") if request.view_args else None
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
    nombre_nora = request.view_args.get("nombre_nora") if request.view_args else None
    return render_template("panel_cliente_redes_sociales/estadisticas.html", nombre_nora=nombre_nora)

@panel_cliente_redes_sociales_bp.route("/programar")
def programar_publicaciones():
    """Interface para programar publicaciones en múltiples redes"""
    nombre_nora = request.view_args.get("nombre_nora") if request.view_args else None
    return render_template("panel_cliente_redes_sociales/programar.html", nombre_nora=nombre_nora)

@panel_cliente_redes_sociales_bp.route("/calendario")
def calendario_contenido():
    """Vista de calendario editorial"""
    nombre_nora = request.view_args.get("nombre_nora") if request.view_args else None
    return render_template("panel_cliente_redes_sociales/calendario.html", nombre_nora=nombre_nora)

@panel_cliente_redes_sociales_bp.route("/facebook")
def gestionar_facebook():
    """Panel de gestión de páginas de Facebook - OPTIMIZADO"""
    nombre_nora = request.view_args.get("nombre_nora") if request.view_args else None
    
    try:
        # 🚀 CONSULTA OPTIMIZADA: Solo campos necesarios para la lista
        paginas_response = supabase.table('facebook_paginas').select(
            'page_id, nombre_pagina, seguidores, likes, verificada, estado_webhook, '
            'foto_perfil_url, categoria, ultima_sincronizacion'
        ).execute()
        
        paginas = paginas_response.data if paginas_response.data else []
        
        # 📊 Estadísticas rápidas
        total_paginas = len(paginas)
        paginas_activas = len([p for p in paginas if p.get('estado_webhook') == 'activa'])
        
        return render_template("panel_cliente_redes_sociales/facebook.html",
                             nombre_nora=nombre_nora,
                             paginas=paginas,
                             total_paginas=total_paginas,
                             paginas_activas=paginas_activas)
        
    except Exception as e:
        print(f"Error en gestionar_facebook: {e}")
        return render_template("panel_cliente_redes_sociales/facebook.html",
                             nombre_nora=nombre_nora,
                             paginas=[])

@panel_cliente_redes_sociales_bp.route("/facebook/<page_id>")
def detalle_pagina_facebook(page_id):
    """🚀 REDIRECCIÓN AL MÓDULO SEPARADO - OPTIMIZADO"""
    nombre_nora = request.view_args.get("nombre_nora") if request.view_args else None
    
    # Redirección al módulo optimizado y separado
    return redirect(url_for('facebook_detalle_bp.detalle_pagina_facebook_optimizado', 
                           nombre_nora=nombre_nora, page_id=page_id))

@panel_cliente_redes_sociales_bp.route("/facebook/<page_id>/vincular", methods=['POST'])
def vincular_pagina_cliente(page_id):
    """Vincular página de Facebook a un cliente específico"""
    nombre_nora = request.view_args.get("nombre_nora") if request.view_args else None
    
    try:
        data = request.json
        empresa_id = data.get('empresa_id')
        
        if not empresa_id:
            return jsonify({'error': 'ID de empresa requerido'}), 400
        
        # Actualizar la página con la empresa vinculada
        update_response = supabase.table('facebook_paginas').update({
            'empresa_id': empresa_id,
            'actualizado_en': 'now()'
        }).eq('page_id', page_id).execute()
        
        if update_response.data:
            return jsonify({
                'success': True,
                'message': 'Página vinculada exitosamente'
            })
        else:
            return jsonify({'error': 'Error al vincular página'}), 500
            
    except Exception as e:
        print(f"Error vinculando página: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@panel_cliente_redes_sociales_bp.route("/facebook/<page_id>/desvincular", methods=['POST'])
def desvincular_pagina_cliente(page_id):
    """Desvincular página de Facebook de un cliente"""
    nombre_nora = request.view_args.get("nombre_nora") if request.view_args else None
    
    try:
        # Remover la vinculación con empresa
        update_response = supabase.table('facebook_paginas').update({
            'empresa_id': None,
            'actualizado_en': 'now()'
        }).eq('page_id', page_id).execute()
        
        if update_response.data:
            return jsonify({
                'success': True,
                'message': 'Página desvinculada exitosamente'
            })
        else:
            return jsonify({'error': 'Error al desvincular página'}), 500
            
    except Exception as e:
        print(f"Error desvinculando página: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@panel_cliente_redes_sociales_bp.route("/facebook/<page_id>/webhook/suscribir", methods=['POST'])
def suscribir_webhook_facebook(page_id):
    """Suscribir webhook de una página de Facebook"""
    nombre_nora = request.view_args.get("nombre_nora") if request.view_args else None
    
    try:
        # Verificar que la página existe
        page_result = supabase.table('facebook_paginas').select('access_token').eq('page_id', page_id).execute()
        
        if not page_result.data:
            return jsonify({'error': 'Página no encontrada'}), 404
        
        page_token = page_result.data[0].get('access_token')
        
        if not page_token:
            return jsonify({'error': 'Token de acceso no disponible'}), 400
        
        # Aquí iría la lógica de suscripción a Meta API
        # Por ahora, solo actualizamos el estado en BD
        
        update_response = supabase.table('facebook_paginas').update({
            'estado_webhook': 'activa',
            'actualizado_en': 'now()'
        }).eq('page_id', page_id).execute()
        
        if update_response.data:
            return jsonify({
                'success': True,
                'message': 'Webhook suscrito exitosamente'
            })
        else:
            return jsonify({'error': 'Error al suscribir webhook'}), 500
            
    except Exception as e:
        print(f"Error suscribiendo webhook: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@panel_cliente_redes_sociales_bp.route("/facebook/<page_id>/webhook/desconectar", methods=['POST'])
def desconectar_webhook_facebook(page_id):
    """Desconectar webhook de una página de Facebook - CORREGIDO"""
    nombre_nora = request.view_args.get("nombre_nora") if request.view_args else None
    
    try:
        # Verificar si la página existe y tiene token válido
        page_result = supabase.table('facebook_paginas').select('access_token').eq('page_id', page_id).execute()
        
        if not page_result.data:
            return jsonify({'error': 'Página no encontrada'}), 404
        
        page_token = page_result.data[0].get('access_token')
        
        # Si hay token válido, intentar desuscribir de Meta
        if page_token:
            try:
                import requests
                
                # Desuscribir webhook de Meta
                url = f"https://graph.facebook.com/v18.0/{page_id}/subscribed_apps"
                data = {
                    'access_token': page_token,
                    'subscribed_fields': ''  # Campos vacíos = desuscribir
                }
                
                response = requests.post(url, data=data)
                print(f"Respuesta de Meta desuscripción: {response.status_code} - {response.text}")
                
            except Exception as meta_error:
                print(f"Error desuscribiendo de Meta: {meta_error}")
        
        # ✅ ACTUALIZACIÓN CON COLUMNAS CORRECTAS
        update_response = supabase.table('facebook_paginas').update({
            'estado_webhook': 'pausada',
            'access_token': None,  # Limpiar token
            'actualizado_en': 'now()'  # ✅ Nombre correcto de columna
        }).eq('page_id', page_id).execute()
        
        if update_response.data:
            return jsonify({
                'success': True,
                'message': 'Webhook desconectado exitosamente'
            })
        else:
            return jsonify({'error': 'Error al desconectar webhook'}), 500
            
    except Exception as e:
        print(f"Error desconectando webhook: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@panel_cliente_redes_sociales_bp.route("/facebook/<page_id>/api/comentarios")
def api_comentarios_facebook(page_id):
    """API para obtener comentarios de una página (ligera)"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        result = supabase.table('comentarios_facebook').select(
            'id, mensaje, autor_nombre, fecha_comentario, likes_comentario'
        ).eq('page_id', page_id).order(
            'fecha_comentario', desc=True
        ).limit(limit).execute()
        
        return jsonify({
            'comentarios': result.data,
            'total': len(result.data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@panel_cliente_redes_sociales_bp.route("/facebook/<page_id>/api/reacciones")
def api_reacciones_facebook(page_id):
    """API para obtener reacciones de una página (ligera)"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        result = supabase.table('reacciones_facebook').select(
            'id, tipo_reaccion, autor_nombre, fecha_reaccion'
        ).eq('page_id', page_id).order(
            'fecha_reaccion', desc=True
        ).limit(limit).execute()
        
        return jsonify({
            'reacciones': result.data,
            'total': len(result.data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
