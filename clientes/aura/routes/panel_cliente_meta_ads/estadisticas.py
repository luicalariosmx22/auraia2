from flask import render_template, request, jsonify, abort
from datetime import datetime, timedelta
from clientes.aura.utils.supabase_client import supabase
import uuid
import os
import requests
import json
import threading
import hashlib
import secrets

from clientes.aura.routes.panel_cliente_meta_ads.utils.columnas_meta_ads import (
    limpiar_columnas_solicitadas, obtener_fields_para_meta, obtener_breakdowns, MAPEO_COLUMNAS_META_ADS
)
from clientes.aura.utils.meta_ads import obtener_reporte_campanas

from . import panel_cliente_meta_ads_bp

@panel_cliente_meta_ads_bp.route('/estadisticas', methods=['GET', 'POST'])
def vista_estadisticas_ads():
    """Vista principal para estadísticas de Meta Ads"""
    if request.method == 'POST':
        fecha_fin = datetime.utcnow().date()
        fecha_inicio = fecha_fin - timedelta(days=6)
        # Aquí debes obtener el ID de la cuenta publicitaria, por ejemplo desde el request o una variable
        cuenta_id = request.form.get('cuenta_id') or request.args.get('cuenta_id')
        if not cuenta_id:
            return jsonify({'ok': False, 'error': 'Falta cuenta_id'}), 400
        campañas = obtener_reporte_campanas(cuenta_id, str(fecha_inicio), str(fecha_fin))
        return jsonify({'ok': True, 'campañas': campañas})
    return render_template('panel_cliente_meta_ads/estadisticas_ads.html')

@panel_cliente_meta_ads_bp.route('/estadisticas/compartir_reporte', methods=['POST'])
def compartir_reporte(nombre_nora):
    """
    Genera un link público para compartir un reporte específico con clientes.
    """
    try:
        data = request.get_json()
        reporte_id = data.get('reporte_id')
        empresa_nombre = data.get('empresa_nombre', '')
        periodo = data.get('periodo', '')
        usuario_compartir = data.get('nombre_nora', nombre_nora)  # Usar el de la URL o el enviado
        
        if not reporte_id:
            return jsonify({'ok': False, 'error': 'ID de reporte requerido'}), 400
        
        # Verificar que el reporte existe
        try:
            reporte = supabase.table('meta_ads_reportes_semanales').select('*').eq('id', reporte_id).single().execute().data
        except Exception as e:
            return jsonify({'ok': False, 'error': 'Reporte no encontrado'}), 404
        
        if not reporte:
            return jsonify({'ok': False, 'error': 'Reporte no encontrado'}), 404
        
        # Generar token único para compartir
        token_uuid = str(uuid.uuid4())
        token_seguridad = secrets.token_hex(16)
        
        # Construir URL pública
        base_url = "https://app.soynoraai.com"
        url_publico = f"{base_url}/panel_cliente/{usuario_compartir}/meta_ads/reporte_publico/{token_uuid}?token={token_seguridad}"
        
        # Guardar registro de compartir en base de datos
        try:
            supabase.table('meta_ads_reportes_compartidos').insert({
                'id': token_uuid,
                'reporte_id': reporte_id,
                'token': token_seguridad,
                'empresa_nombre': empresa_nombre,
                'periodo': periodo,
                'compartido_por': usuario_compartir,
                'created_at': datetime.utcnow().isoformat(),
                'activo': True
            }).execute()
        except Exception as e:
            print(f"[WARN] No se pudo guardar registro de compartir: {e}")
        
        return jsonify({
            'ok': True, 
            'url_publico': url_publico,
            'token': token_seguridad,
            'reporte_id': reporte_id,
            'token_uuid': token_uuid
        })
        
    except Exception as e:
        print(f"[ERROR] Error al compartir reporte: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

@panel_cliente_meta_ads_bp.route('/reporte_publico/<token_uuid>')
def vista_reporte_publico(nombre_nora, token_uuid):
    """
    Vista pública de un reporte compartido usando token de seguridad.
    URL: https://app.soynoraai.com/reporte_publico/<token_uuid>?token=<token_seguridad>
    """
    try:
        # Obtener token de seguridad de la query string
        token_seguridad = request.args.get('token')
        
        if not token_seguridad:
            abort(400, description="Token de seguridad requerido")
        
        # Verificar que el enlace compartido es válido
        try:
            enlace_compartido = supabase.table('meta_ads_reportes_compartidos').select('*').eq('id', token_uuid).eq('token', token_seguridad).eq('activo', True).single().execute().data
        except Exception as e:
            print(f"[ERROR] Error al buscar enlace compartido: {e}")
            abort(404, description="Enlace no encontrado o expirado")
        
        if not enlace_compartido:
            abort(404, description="Enlace no encontrado o expirado")
        
        # Obtener el reporte original
        reporte_id = enlace_compartido['reporte_id']
        try:
            reporte = supabase.table('meta_ads_reportes_semanales').select('*').eq('id', reporte_id).single().execute().data
        except Exception as e:
            print(f"[ERROR] Error al obtener reporte: {e}")
            abort(404, description="Reporte no encontrado")
        
        if not reporte:
            abort(404, description="Reporte no encontrado")
        
        # Obtener anuncios detallados del reporte
        try:
            anuncios = supabase.table('meta_ads_anuncios_detalle').select('*').eq('id_cuenta_publicitaria', reporte['id_cuenta_publicitaria']).gte('fecha_inicio', reporte['fecha_inicio']).lte('fecha_fin', reporte['fecha_fin']).execute().data
        except Exception as e:
            print(f"[ERROR] Error al obtener anuncios: {e}")
            anuncios = []
        
        # Obtener información de la empresa
        try:
            empresa = supabase.table('meta_ads_cuentas').select('*').eq('id_cuenta_publicitaria', reporte['id_cuenta_publicitaria']).single().execute().data
        except Exception as e:
            print(f"[ERROR] Error al obtener empresa: {e}")
            empresa = None
        
        # Preparar datos para el template
        datos_reporte = {
            'reporte': reporte,
            'anuncios': anuncios or [],
            'empresa': empresa,
            'enlace_compartido': enlace_compartido,
            'es_publico': True
        }
        
        return render_template('panel_cliente_meta_ads/detalle_reporte_publico.html', **datos_reporte)
        
    except Exception as e:
        print(f"[ERROR] Error en vista_reporte_publico: {e}")
        abort(500, description="Error interno del servidor")

@panel_cliente_meta_ads_bp.route('/api/reporte_publico/<token_uuid>/validar')
def validar_enlace_publico(nombre_nora, token_uuid):
    """
    API para validar si un enlace público es válido sin mostrar el reporte completo.
    """
    try:
        token_seguridad = request.args.get('token')
        
        if not token_seguridad:
            return jsonify({'valido': False, 'error': 'Token de seguridad requerido'}), 400
        
        # Verificar que el enlace compartido es válido
        try:
            enlace_compartido = supabase.table('meta_ads_reportes_compartidos').select('empresa_nombre,periodo,created_at').eq('id', token_uuid).eq('token', token_seguridad).eq('activo', True).single().execute().data
        except Exception:
            return jsonify({'valido': False, 'error': 'Enlace no encontrado o expirado'}), 404
        
        if not enlace_compartido:
            return jsonify({'valido': False, 'error': 'Enlace no encontrado o expirado'}), 404
        
        return jsonify({
            'valido': True,
            'empresa_nombre': enlace_compartido.get('empresa_nombre', ''),
            'periodo': enlace_compartido.get('periodo', ''),
            'fecha_creacion': enlace_compartido.get('created_at', '')
        })
        
    except Exception as e:
        print(f"[ERROR] Error en validar_enlace_publico: {e}")
        return jsonify({'valido': False, 'error': 'Error interno del servidor'}), 500
