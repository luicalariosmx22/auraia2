from flask import Blueprint

# Blueprint de reportes_meta_ads
reportes_meta_ads_bp = Blueprint('reportes_meta_ads', __name__,
    template_folder='../../templates',
    static_folder='../../static/panel_cliente_meta_ads',
    static_url_path='/static/panel_cliente_meta_ads')

# Importar vistas después para evitar ciclos
from clientes.aura.routes.panel_cliente_meta_ads import panel_cliente_meta_ads_bp

print(f"✅ Blueprint reportes_meta_ads inicializado con url_prefix='/reportes'")

# Variable global para estadísticas_ads_bp
estadisticas_ads_bp = None

def get_estadisticas_bp():
    """Obtiene el blueprint de estadísticas con carga lazy"""
    global estadisticas_ads_bp
    if estadisticas_ads_bp is None:
        try:
            print("🔄 Cargando estadísticas_ads_bp bajo demanda...")
            from clientes.aura.routes.panel_cliente_meta_ads import panel_cliente_meta_ads_bp
            estadisticas_ads_bp = Blueprint('estadisticas_ads_bp', __name__)
            print("✅ estadisticas_ads_bp cargado exitosamente")
        except Exception as e:
            print(f"❌ Error cargando estadisticas_ads_bp: {e}")
            return None
    return estadisticas_ads_bp

print("✅ Rutas básicas de reportes_meta_ads cargadas")
