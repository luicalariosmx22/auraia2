from flask import Blueprint
from .vista_panel_cliente_pagos import panel_cliente_pagos_bp
from .vista_servicios import panel_cliente_pagos_servicios_bp
from .vista_recibo_nuevo import panel_cliente_pagos_nuevo_bp
from .vista_recibo_pago import panel_cliente_pagos_recibo_bp
from .vista_presupuestos import panel_cliente_pagos_presupuestos_bp
from .vista_presupuesto_nuevo import panel_cliente_pagos_presupuesto_nuevo_bp

__all__ = [
    "panel_cliente_pagos_bp",
    "panel_cliente_pagos_servicios_bp",
    "panel_cliente_pagos_nuevo_bp",
    "panel_cliente_pagos_recibo_bp",
    "panel_cliente_pagos_presupuestos_bp",
    "panel_cliente_pagos_presupuesto_nuevo_bp"
]
