from flask import Blueprint

# Blueprint de reportes_meta_ads
reportes_meta_ads_bp = Blueprint('reportes_meta_ads', __name__)

# Importa rutas después de definir el blueprint para evitar ciclos
from .vistas import *
from .carga_manual import *
from .automatizaciones import *
from .diseno import *
from .estadisticas import estadisticas_ads_bp

# Asegura que estadisticas_ads_bp esté disponible para registrar en la app principal
