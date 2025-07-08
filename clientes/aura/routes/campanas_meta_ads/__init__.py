from flask import Blueprint

# Blueprint de campanas_meta_ads
campanas_meta_ads_bp = Blueprint('campanas_meta_ads', __name__)

# Importa rutas después de definir el blueprint para evitar ciclos
from .vistas import *
from .gestion import *

@campanas_meta_ads_bp.route('/ejemplo', methods=['GET'])
def ejemplo_campanas():
    return {'ok': True, 'msg': 'Blueprint de campañas Meta Ads funcionando!'}
