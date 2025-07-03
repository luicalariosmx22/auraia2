from flask import Blueprint

# Blueprint de reportes_meta_ads
reportes_meta_ads_bp = Blueprint('reportes_meta_ads', __name__)

# Importar rutas básicas de forma segura
try:
    print("🔄 Cargando rutas básicas de reportes_meta_ads...")
    from . import vistas
    from . import carga_manual  
    from . import automatizaciones
    from . import diseno
    print("✅ Rutas básicas de reportes_meta_ads cargadas")
except Exception as e:
    print(f"❌ Error cargando rutas básicas de reportes_meta_ads: {e}")

# Variable global para estadísticas_ads_bp
estadisticas_ads_bp = None

def get_estadisticas_bp():
    """Obtiene el blueprint de estadísticas con carga lazy"""
    global estadisticas_ads_bp
    if estadisticas_ads_bp is None:
        try:
            print("🔄 Cargando estadísticas_ads_bp bajo demanda...")
            from .estadisticas import estadisticas_ads_bp as stats_bp
            estadisticas_ads_bp = stats_bp
            print("✅ estadisticas_ads_bp cargado exitosamente")
        except Exception as e:
            print(f"❌ Error cargando estadisticas_ads_bp: {e}")
            return None
    return estadisticas_ads_bp
