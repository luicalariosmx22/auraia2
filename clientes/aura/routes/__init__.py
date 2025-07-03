from .reportes_meta_ads import reportes_meta_ads_bp
# from .reportes_meta_ads import estadisticas_ads_bp  # Ahora se carga de forma lazy
from .sincronizar_meta_ads import panel_cliente_meta_ads_bp
from clientes.aura.routes.reportes_meta_ads.vista_sincronizacion import panel_cliente_meta_ads_sincronizacion_bp

__all__ = [
    "panel_cliente_meta_ads_bp",
    "panel_cliente_meta_ads_sincronizacion_bp",
    "reportes_meta_ads_bp",
    # "estadisticas_ads_bp"  # Carga lazy, usar get_estadisticas_bp()
]