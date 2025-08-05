# Estructura de Módulos en NORA

## 1. Estructura de Archivos

```
clientes/aura/routes/nombre_modulo/
├── __init__.py              # Definición principal del blueprint y registro
├── vistas.py               # Rutas principales del módulo
├── automatizaciones.py     # (opcional) Funcionalidades automatizadas
├── utils/                  # (opcional) Utilidades del módulo
│   └── helpers.py
└── templates/              # Templates específicos del módulo
    └── nombre_modulo/
        └── index.html
```

## 2. Definición del Blueprint (`__init__.py`)

```python
from flask import Blueprint

# Crear el blueprint principal
nombre_modulo_bp = Blueprint(
    "nombre_modulo",
    __name__,
    template_folder="../../templates/nombre_modulo"
)

# Importar submódulos después de crear el blueprint
from . import vistas
from . import automatizaciones  # opcional

# Función para registrar blueprints locales (si hay submódulos)
def register_module_blueprints(app):
    app.register_blueprint(submódulo1_bp)
    app.register_blueprint(submódulo2_bp)
```

## 3. Registro en `registro_dinamico.py`

```python
# Importar el blueprint al inicio del archivo
from clientes.aura.routes.nombre_modulo import nombre_modulo_bp

# En la función registrar_blueprints_por_nora:
if "nombre_modulo" in modulos:
    print(f"Registrando blueprint NOMBRE_MODULO para {nombre_nora}")
    safe_register_blueprint(
        app, 
        nombre_modulo_bp, 
        url_prefix=f"/panel_cliente/{nombre_nora}/nombre_modulo"
    )
```

## 4. Definición de Rutas (`vistas.py`)

```python
from . import nombre_modulo_bp
from flask import render_template, request, jsonify

@nombre_modulo_bp.route('/')
def index():
    nombre_nora = request.view_args.get('nombre_nora')
    return render_template('nombre_modulo/index.html', nombre_nora=nombre_nora)

@nombre_modulo_bp.route('/api/datos')
def get_datos():
    nombre_nora = request.view_args.get('nombre_nora')
    return jsonify({"status": "success"})
```

## 5. Gestión de Prefijos de URL

1. **Estructura de URLs**:
   ```
   /panel_cliente/{nombre_nora}/{modulo}/{submodulo}/
   ```
   Ejemplo para Meta Ads:
   ```
   /panel_cliente/aura/meta_ads/reportes/      # Módulo de reportes
   /panel_cliente/aura/meta_ads/campanas/      # Módulo de campañas
   ```

2. **Registro del Blueprint**:
   - NO incluir prefijos en la definición del blueprint:
     ```python
     # ✅ CORRECTO
     nombre_modulo_bp = Blueprint('nombre_modulo', __name__, template_folder='templates')

     # ❌ INCORRECTO - No incluir url_prefix aquí
     nombre_modulo_bp = Blueprint('nombre_modulo', __name__, url_prefix='/meta_ads/reportes')
     ```

   - Incluir el prefijo completo en registro_dinamico.py:
     ```python
     # ✅ CORRECTO
     safe_register_blueprint(
         app,
         reportes_meta_ads_bp,
         url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads/reportes"
     )

     # ❌ INCORRECTO - Prefijo incompleto
     safe_register_blueprint(
         app,
         reportes_meta_ads_bp,
         url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads"
     )
     ```

3. **Verificación de Rutas**:
   - Antes de desplegar, verificar que las rutas estén correctamente registradas:
     ```python
     print("\n🔍 Verificando rutas registradas:")
     for rule in app.url_map.iter_rules():
         if nombre_modulo in rule.rule:
             print(f"  {rule.rule} → {rule.endpoint}")
     ```

## 6. Buenas Prácticas

1. **Nombres Consistentes**:
   - Usar snake_case para nombres de archivos y variables
   - Usar nombres descriptivos que indiquen la función

2. **Estructura del Blueprint**:
   - Definir el blueprint en `__init__.py`
   - Importar las vistas después de crear el blueprint
   - Usar `template_folder` relativo al blueprint

3. **Manejo de nombre_nora**:
   - Obtener siempre de `request.view_args.get('nombre_nora')`
   - Pasar a todos los templates
   - Usar en consultas a Supabase

4. **Registro de Rutas**:
   - Las rutas base van en `vistas.py`
   - Submódulos en archivos separados
   - Prefijos de ruta consistentes

5. **Acceso a Datos**:
   - Usar `supabase_client` para todas las consultas
   - Filtrar siempre por `nombre_nora`
   - Manejar casos donde no hay datos (`... or []`)

## 6. Ejemplos de URLs Resultantes

```
/panel_cliente/{nombre_nora}/nombre_modulo/          # Vista principal
/panel_cliente/{nombre_nora}/nombre_modulo/api/datos # Endpoint API
```

## 7. Checklist de Implementación

- [ ] Blueprint creado en `__init__.py`
- [ ] Blueprint registrado en `registro_dinamico.py`
- [ ] Rutas definidas en `vistas.py`
- [ ] Templates en la carpeta correcta
- [ ] Manejo de `nombre_nora` en todas las rutas
- [ ] Filtrado por `nombre_nora` en consultas Supabase
- [ ] Submódulos registrados (si existen)
- [ ] Permisos y autenticación configurados

## 8. Solución de Problemas Comunes

1. **404 Not Found**:
   - Verificar registro en `registro_dinamico.py`:
     ```python
     # Imprimir todas las rutas relacionadas con el módulo
     for rule in app.url_map.iter_rules():
         if 'meta_ads' in rule.rule:
             print(f"Ruta: {rule.rule} → {rule.endpoint}")
     ```
   - Confirmar que el prefijo de URL está completo:
     ```python
     # ✅ CORRECTO: Incluye la ruta completa
     url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads/reportes"
     
     # ❌ INCORRECTO: Falta parte de la ruta
     url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads"
     ```
   - Verificar que NO hay url_prefix en el blueprint:
     ```python
     # ✅ CORRECTO
     bp = Blueprint('modulo', __name__, template_folder='templates')
     
     # ❌ INCORRECTO
     bp = Blueprint('modulo', __name__, url_prefix='/ruta')
     ```
   - Revisar que el módulo esté activo en la base de datos:
     ```sql
     SELECT modulos FROM configuracion_bot WHERE nombre_nora = 'nombre_nora';
     ```
   - Verificar que las rutas en `vistas.py` son relativas:
     ```python
     # ✅ CORRECTO
     @bp.route('/')
     @bp.route('/generar')
     
     # ❌ INCORRECTO
     @bp.route('/meta_ads/reportes/')
     @bp.route('/meta_ads/reportes/generar')
     ```

2. **500 Internal Server Error**:
   - Verificar imports circulares
   - Confirmar estructura de datos en Supabase
   - Revisar manejo de `nombre_nora`

3. **Templates no encontrados**:
   - Verificar `template_folder` en blueprint
   - Confirmar estructura de carpetas
   - Revisar nombres de archivos

## 9. Tips de Desarrollo

1. Usar prints estratégicos para debug:
```python
print(f"🔵 nombre_nora recibido: {nombre_nora}")
print(f"🔵 datos obtenidos: {len(datos)}")
```

2. Validar módulo activo:
```python
modulos = obtener_modulos_activos(nombre_nora)
if "nombre_modulo" not in modulos:
    return "Módulo no disponible", 404
```

3. Mantener consistencia en respuestas JSON:
```python
return jsonify({
    "success": True,
    "message": "Operación exitosa",
    "data": datos
})
```

## 10. Manejo de Campos en Base de Datos

1. **Campos de Tiempo**:
   - Para fechas de creación usar `fecha_generacion` o `fecha_creacion`
   - Para fechas de actualización usar `fecha_actualizacion`
   - Para rangos de fecha usar `fecha_desde` y `fecha_hasta`
   - Para timestamps usar formato ISO: `datetime.now().isoformat()`

2. **Campos de Estado**:
   ```python
   # En la tabla
   estado = 'completado' | 'pendiente' | 'error'
   tipo_reporte = 'especifico' | 'general' | 'automatico'
   ```

3. **Campos de Identificación**:
   - Usar siempre `nombre_nora` para filtrar por instancia
   - Mantener `nombre_visible` por compatibilidad si existe
   - Para IDs externos usar prefijo descriptivo: `id_cuenta_publicitaria`

4. **Validación de Campos**:
   ```python
   # Verificar que los campos existen antes de usar
   campos_requeridos = ['nombre_nora', 'fecha_generacion', 'estado']
   if not all(campo in data for campo in campos_requeridos):
       raise ValueError(f"Faltan campos requeridos: {campos_requeridos}")
   
   # Al ordenar, verificar nombre de columna
   try:
       resultados = supabase.table('tabla').order('campo', desc=True)
   except Exception as e:
       if '42703' in str(e):  # Código PostgreSQL para columna no existe
           print(f"❌ Error: La columna no existe en la tabla")
       raise
   ```

5. **Convenciones de Nombrado**:
   - Usar snake_case para nombres de tablas y columnas
   - Evitar palabras reservadas de SQL
   - Ser consistente con los tipos de datos
   - Documentar estructura de tablas importantes

6. **Manejo de Errores de BD**:
   ```python
   try:
       result = supabase.table('tabla').select('*').execute()
   except APIError as e:
       if e.code == '42703':  # Columna no existe
           print(f"❌ Error: Columna no encontrada: {e.message}")
       elif e.code == '42P01':  # Tabla no existe
           print(f"❌ Error: Tabla no encontrada: {e.message}")
       else:
           print(f"❌ Error de base de datos: {e.message}")
       raise
   ```
