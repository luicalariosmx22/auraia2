from flask import flash, request
from . import panel_cliente_meta_ads_bp

@panel_cliente_meta_ads_bp.route('/config', methods=['POST'])
def guardar_config_reportes():
    """Guarda la configuración de reportes"""
    try:
        # TODO: Implementar lógica de guardado de configuración
        flash('Configuración guardada exitosamente', 'success')
        return ('', 204)
    except Exception as e:
        flash(f'Error al guardar configuración: {str(e)}', 'error')
        return jsonify({'error': str(e)}), 500
