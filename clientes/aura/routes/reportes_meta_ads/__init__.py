from flask import Blueprint

# Blueprint de reportes_meta_ads
reportes_meta_ads_bp = Blueprint('reportes_meta_ads', __name__)

# Importa rutas después de definir el blueprint para evitar ciclos
# OPTIMIZACIÓN: Importaciones lazy para evitar cuelgues al arrancar
def lazy_import_routes():
    """Importa las rutas solo cuando sean necesarias para evitar cuelgues de inicialización"""
    try:
        from .vistas import *
        from .carga_manual import *
        from .automatizaciones import *
        from .diseno import *
        print("✅ Rutas básicas de reportes_meta_ads cargadas")
    except Exception as e:
        print(f"❌ Error cargando rutas básicas de reportes_meta_ads: {e}")

# Importar rutas básicas inmediatamente
lazy_import_routes()

# Importar rutas lazy para estadísticas
from .lazy_estadisticas import lazy_estadisticas_bp

# Estadísticas se carga bajo demanda para evitar cuelgues
estadisticas_ads_bp = None

def get_estadisticas_bp():
    """Obtiene el blueprint de estadísticas con carga lazy"""
    global estadisticas_ads_bp
    if estadisticas_ads_bp is None:
        try:
            print("[LAZY] Cargando módulo de estadísticas...")
            from .estadisticas import estadisticas_ads_bp
            print("✅ Módulo de estadísticas cargado correctamente")
        except Exception as e:
            print(f"❌ Error cargando módulo de estadísticas: {e}")
    return estadisticas_ads_bp
