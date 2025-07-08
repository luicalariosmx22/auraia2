from flask import Blueprint

panel_cliente_google_ads_bp = Blueprint(
    "panel_cliente_google_ads", __name__,
    template_folder="../../templates/panel_cliente_google_ads"
)

# Solo importa submódulos, sin rutas aquí
from . import vista_panel_google_ads
from . import vista_cuentas_google_ads
# from . import vista_asociar_empresas  # Comentado temporalmente
