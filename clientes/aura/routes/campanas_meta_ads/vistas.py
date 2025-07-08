# Vistas de campañas activas, detalles, etc.

from . import campanas_meta_ads_bp

@campanas_meta_ads_bp.route('/test_vista', methods=['GET'])
def test_vista():
    return {'ok': True, 'msg': 'Vista de campañas funcionando!'}
