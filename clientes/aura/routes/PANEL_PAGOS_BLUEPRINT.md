## Configuración del Blueprint

```python
panel_cliente_pagos_bp = Blueprint(
    "panel_cliente_pagos_bp",
    __name__,
    url_prefix="/panel_cliente/<nombre_nora>/pagos"
)
```

## Detalles

- **Nombre del Blueprint**: `panel_cliente_pagos_bp`
- **URL Prefix**: `/panel_cliente/<nombre_nora>/pagos`
- **Parámetro Dinámico**: `nombre_nora` (incluido en la URL)

## Uso

Este Blueprint maneja todas las rutas relacionadas con el módulo de pagos para cada instancia de Nora. El parámetro `nombre_nora` se pasa automáticamente a todas las rutas dentro del Blueprint gracias al prefijo de URL.

### Ejemplo de Ruta

```python
@panel_cliente_pagos_bp.route('/')
def panel_pagos(nombre_nora):
    # nombre_nora está disponible automáticamente como parámetro
    # gracias al url_prefix
    return render_template('panel_cliente_pagos/index.html', nombre_nora=nombre_nora)
```

## Notas

- Todas las rutas dentro de este Blueprint heredan el prefijo `/panel_cliente/<nombre_nora>/pagos`
- El parámetro `nombre_nora` debe estar presente en todas las funciones de ruta
- Las plantillas relacionadas se encuentran en `templates/panel_cliente_pagos/`
