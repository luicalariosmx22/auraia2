from flask import flash, request
from . import reportes_meta_ads_bp

@reportes_meta_ads_bp.route('/reportes/config', methods=['POST'])
def guardar_config_reportes():
    flash('Configuración guardada (lógica pendiente de implementar)', 'success')
    return ('', 204)
