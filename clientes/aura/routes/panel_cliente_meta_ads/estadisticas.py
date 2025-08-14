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
        
        # Verificar que el reporte existe y está activo
        try:
            reporte = supabase.table('meta_ads_reportes_semanales').select('*').eq('id', reporte_id).eq('estatus', 'activo').single().execute().data
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

# ✅ Funciones de vista pública eliminadas - se usan las de reportes.py
