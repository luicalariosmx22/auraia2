from flask import jsonify, request
from . import panel_cliente_meta_ads_bp
from .helpers import procesar_reporte
from clientes.aura.utils.supabase_client import supabase

@panel_cliente_meta_ads_bp.route('/reportes/<uuid>', methods=['GET'])
def descargar_reporte_semanal_panel(uuid):
    """Devuelve todos los datos de un reporte semanal por UUID en formato JSON"""
    try:
        reporte = supabase.table('meta_ads_reportes_semanales')\
            .select('*')\
            .eq('uuid', uuid)\
            .execute().data

        if not reporte:
            todos_reportes = supabase.table('meta_ads_reportes_semanales')\
                .select('uuid')\
                .execute().data
            print(f"[DEBUG] UUID {uuid} no encontrado. Reportes disponibles: {todos_reportes}")
            return jsonify({'error': 'Reporte no encontrado'}), 404

        return jsonify({
            'ok': True,
            'reporte': reporte[0] if reporte else None
        })
    except Exception as e:
        print(f"Error al obtener reporte {uuid}: {str(e)}")
        return jsonify({
            'error': 'Error interno al obtener el reporte',
            'details': str(e)
        }), 500
