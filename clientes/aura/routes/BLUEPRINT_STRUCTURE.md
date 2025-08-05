# Estructura de Blueprints en AuraAI

## Configuración Básica de un Blueprint

```python
nombre_modulo_bp = Blueprint(
    "nombre_modulo_bp",    # Nombre único del blueprint
    __name__,             # Nombre del módulo Python
    url_prefix="/ruta/<parametro>"  # Prefijo de URL con parámetros dinámicos
)
```

## Patrones Comunes

### 1. Blueprint con Parámetro Nora
```python
# Ejemplo para módulos que necesitan acceso a una instancia específica de Nora
modulo_bp = Blueprint(
    "modulo_bp",
    __name__,
    url_prefix="/panel_cliente/<nombre_nora>/modulo"
)
```

### 2. Blueprint sin Parámetros
```python
# Ejemplo para módulos generales
admin_bp = Blueprint(
    "admin_bp",
    __name__,
    url_prefix="/admin"
)
```

## Registro del Blueprint

En `__init__.py`:
```python
from clientes.aura.routes.mi_modulo import modulo_bp
safe_register_blueprint(app, modulo_bp)
```

## Estructura de Rutas

### Con Parámetro Nora
```python
@modulo_bp.route('/')
def index(nombre_nora):
    return render_template('modulo/index.html', nombre_nora=nombre_nora)

@modulo_bp.route('/accion', methods=['POST'])
def accion(nombre_nora):
    # nombre_nora está disponible automáticamente
    return jsonify({"status": "ok"})
```

### Sin Parámetro Nora
```python
@admin_bp.route('/')
def admin_index():
    return render_template('admin/index.html')
```

## Mejores Prácticas

1. **Nombres Consistentes**:
   - Sufijo `_bp` para todos los blueprints
   - Nombres descriptivos que reflejen la funcionalidad

2. **Organización de Archivos**:
   - Un blueprint por archivo
   - Ubicación en `clientes/aura/routes/`
   - Templates correspondientes en `templates/nombre_modulo/`

3. **Parámetros URL**:
   - Usar `nombre_nora` para módulos específicos de cliente
   - Documentar parámetros adicionales

4. **Registro Seguro**:
   - Siempre usar `safe_register_blueprint()` para evitar duplicados
   - Agrupar registros por tipo de funcionalidad

## Ejemplo de Estructura de Archivos

```
clientes/aura/
├── routes/
│   ├── __init__.py
│   ├── modulo_bp.py
│   └── submodulo/
│       └── otro_modulo_bp.py
└── templates/
    └── modulo/
        ├── index.html
        └── componentes/
```

## Seguridad y Validación

- Validar `nombre_nora` en middleware o decoradores
- Implementar control de acceso por blueprint
- Manejar errores de forma consistente
