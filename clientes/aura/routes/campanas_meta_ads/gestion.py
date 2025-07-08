# Endpoints de gestión de campañas, conjuntos y anuncios

from . import campanas_meta_ads_bp

@campanas_meta_ads_bp.route('/test_gestion', methods=['GET'])
def test_gestion():
    return {'ok': True, 'msg': 'Gestión de campañas funcionando!'}

# ...existing code...
