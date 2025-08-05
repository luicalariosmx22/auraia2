from flask import Blueprint, render_template, jsonify, request
from clientes.aura.utils.supabase_client import supabase
from datetime import datetime, timedelta

vista_sincronizacion_bp = Blueprint('vista_sincronizacion', __name__)

@vista_sincronizacion_bp.route('/vista_sincronizacion')
def vista_sincronizacion():
    return render_template('panel_cliente_meta_ads/vista_sincronizacion.html')

@vista_sincronizacion_bp.route('/obtener_estado')
def obtener_estado():
    try:
        ultima_sync = supabase.table('meta_ads_sync_log').select('*').order('created_at', desc=True).limit(1).execute()
        if ultima_sync.data:
            return jsonify({
                'ok': True,
                'estado': ultima_sync.data[0].get('estado', 'desconocido'),
                'ultima_actualizacion': ultima_sync.data[0].get('created_at')
            })
    except Exception as e:
        print(f"Error al obtener estado: {e}")
    return jsonify({'ok': False, 'error': 'No se pudo obtener el estado'})

@vista_sincronizacion_bp.route('/ultimas_sincronizaciones')
def ultimas_sincronizaciones():
    try:
        syncs = supabase.table('meta_ads_sync_log').select('*').order('created_at', desc=True).limit(10).execute()
        return jsonify({'ok': True, 'sincronizaciones': syncs.data})
    except Exception as e:
        print(f"Error al obtener sincronizaciones: {e}")
        return jsonify({'ok': False, 'error': str(e)})
