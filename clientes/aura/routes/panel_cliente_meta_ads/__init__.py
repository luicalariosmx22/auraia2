from .panel_cliente_meta_ads import panel_cliente_meta_ads_bp
from . import sincronizador_semanal
from . import sincronizador  # Agregar esta importación
from . import reportes
from . import estadisticas  # Importar estadísticas para registrar rutas públicas
from .webhooks_meta import webhooks_meta_bp

# Agrega aquí cualquier otro archivo que tenga rutas con @panel_cliente_meta_ads_bp.route

__all__ = ['panel_cliente_meta_ads_bp', 'webhooks_meta_bp']
