# 🗃️ Estructura de un módulo

## 📁 Estructura estándar:

```bash
clientes/
└── aura/
    ├── routes/
    │   └── panel_cliente_<modulo>/
    │       ├── __init__.py
    │       └── panel_cliente_<modulo>.py
    └── templates/
        └── panel_cliente_<modulo>/
            └── index.html
```

## 🎯 Ejemplo completo: módulo "meta_ads"

### 1. Archivo principal: `panel_cliente_meta_ads.py`

```python
from flask import Blueprint, render_template, request

# 🗄️ CONTEXTO BD PARA GITHUB COPILOT
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas
# BD ACTUAL: Esquemas actualizados automáticamente

"""
📊 TABLAS PRINCIPALES QUE USA ESTE MÓDULO:

• meta_ads_anuncios_detalle: Métricas detalladas de anuncios
  Campos: ad_id, campana_id, clicks, impresiones, costo, alcance
  
• meta_ads_cuentas: Cuentas publicitarias conectadas  
  Campos: id_cuenta_publicitaria, nombre_cliente, conectada
  
• meta_ads_reportes_semanales: Reportes consolidados por semana
  Campos: empresa_id, fecha_inicio, fecha_fin, importe_gastado_anuncios
  
• meta_plantillas_anuncios: Plantillas para automatización
  Campos: nombre, descripcion, plantilla_json, activa
  
• facebook_paginas: Páginas de Facebook conectadas
  Campos: page_id, nombre_pagina, access_token, activa
  
• configuracion_bot: Config general de cada Nora
  Campos: nombre_nora, modulos (para verificar si meta_ads está activo)
"""

panel_cliente_meta_ads_bp = Blueprint(
    "panel_cliente_meta_ads_bp", __name__,
    url_prefix="/panel_cliente/<nombre_nora>/meta_ads"
)

@panel_cliente_meta_ads_bp.route("/")
def panel_cliente_meta_ads():
    # ✅ Extraer nombre_nora de la URL de forma robusta
    nombre_nora = request.path.split("/")[2]
    return render_template("panel_cliente_meta_ads/index.html", 
                         nombre_nora=nombre_nora)

@panel_cliente_meta_ads_bp.route("/automatizacion")
def panel_automatizacion_campanas():
    nombre_nora = request.path.split("/")[2]
    return render_template("panel_cliente_meta_ads/automatizacion.html",
                         nombre_nora=nombre_nora)

@panel_cliente_meta_ads_bp.route("/reportes")
def reportes_meta_ads():
    nombre_nora = request.path.split("/")[2]
    return render_template("panel_cliente_meta_ads/reportes.html",
                         nombre_nora=nombre_nora)
```

### 2. Template: `index.html`

```html
{% extends "base_cliente.html" %}

{% block titulo %}� Meta Ads - {{ nombre_nora|title }}{% endblock %}

{% block contenido %}
<div class="max-w-4xl mx-auto py-8">
    <div class="bg-white rounded-lg shadow-sm p-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-4">
            � Meta Ads
        </h1>
        
        <p class="text-gray-600 mb-6">
            Gestiona campañas de Facebook e Instagram para {{ nombre_nora|title }}.
        </p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div class="bg-blue-50 rounded-lg p-4">
                <h3 class="font-semibold text-blue-900">� Campañas</h3>
                <p class="text-blue-700 text-sm">Gestiona tus campañas publicitarias</p>
            </div>
            
            <div class="bg-green-50 rounded-lg p-4">
                <h3 class="font-semibold text-green-900">� Reportes</h3>
                <p class="text-green-700 text-sm">Analiza el rendimiento de tus anuncios</p>
            </div>
            
            <div class="bg-purple-50 rounded-lg p-4">
                <h3 class="font-semibold text-purple-900">⚙️ Automatización</h3>
                <p class="text-purple-700 text-sm">Automatiza la creación de anuncios</p>
            </div>
        </div>
        
        <div class="mt-8">
            <a href="{{ url_for('panel_cliente_meta_ads_bp.panel_automatizacion_campanas', nombre_nora=nombre_nora) }}" 
               class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                ⚙️ Configurar Automatización
            </a>
        </div>
    </div>
</div>
{% endblock %}
```

### 3. Archivo `__init__.py`

```python
# clientes/aura/routes/panel_cliente_meta_ads/__init__.py
from .panel_cliente_meta_ads import panel_cliente_meta_ads_bp
from .webhooks_meta import webhooks_meta_bp
from .automatizacion_routes import automatizacion_routes_bp
from .webhooks_api import webhooks_api_bp

__all__ = [
    'panel_cliente_meta_ads_bp',
    'webhooks_meta_bp',
    'automatizacion_routes_bp',
    'webhooks_api_bp'
]
```

---

## 🤖 Creación automática de módulos

**Nora AI incluye un creador automático de módulos** en `/admin/modulos/crear` que genera toda la estructura:

### Lo que genera automáticamente:
```python
# 1. Carpeta del módulo
clientes/aura/routes/panel_cliente_nuevo_modulo/

# 2. Archivo __init__.py con import
from .panel_cliente_nuevo_modulo import panel_cliente_nuevo_modulo_bp

# 3. Archivo Python principal con estructura completa
panel_cliente_nuevo_modulo_bp = Blueprint(
    "panel_cliente_nuevo_modulo_bp", __name__,
    url_prefix="/panel_cliente/<nombre_nora>/nuevo_modulo"
)

# 4. Template base
{% extends "base_cliente.html" %}
{% block contenido %}
<h1>🧩 Módulo: Nuevo Modulo</h1>
{% endblock %}

# 5. Registro en Supabase (modulos_disponibles)
# 6. Activación automática para una Nora específica
# 7. Actualización de esquemas de BD
```

### Proceso automático del creador (basado en creador_modulos.py):

```python
# 🤖 LÓGICA REAL DEL CREADOR AUTOMÁTICO

def crear_modulo_automatico():
    """Proceso completo basado en creador_modulos.py"""
    
    # 1. EXTRACCIÓN DE NOMBRE_NORA (patrón oficial)
    nombre_nora = request.path.split("/")[2]
    
    # 2. VALIDACIÓN DE MÓDULO
    if modulo_ya_existe(nombre_modulo):
        return {"error": "Módulo ya existe"}
    
    # 3. CREAR ESTRUCTURA DE ARCHIVOS
    crear_carpeta_modulo(nombre_modulo)
    crear_archivo_principal(nombre_modulo)
    crear_template_base(nombre_modulo)
    crear_init_py(nombre_modulo)
    
    # 4. REGISTRO EN SUPABASE
    insertar_modulo_disponible(nombre_modulo, descripcion, icono)
    
    # 5. ACTIVACIÓN AUTOMÁTICA
    activar_para_nora(nombre_modulo, nombre_nora)
    
    # 6. ACTUALIZAR ESQUEMAS
    ejecutar_generar_supabase_schema()
    
    return {"success": True, "modulo": nombre_modulo}
```

### Archivos generados automáticamente:

#### 1. **Estructura de carpetas**:
```bash
# El creador genera esta estructura completa:
clientes/aura/routes/panel_cliente_{nombre_modulo}/
├── __init__.py                 # ✅ Auto-generado
├── panel_cliente_{modulo}.py   # ✅ Con Blueprint completo
└── README.md                   # ✅ Documentación básica

clientes/aura/templates/panel_cliente_{nombre_modulo}/
└── index.html                  # ✅ Template base funcional
```

#### 2. **Blueprint auto-generado**:
```python
# panel_cliente_{modulo}.py (generado automáticamente)
from flask import Blueprint, render_template, request

"""
📊 SCHEMAS DE BD DISPONIBLES PARA ESTE MÓDULO:

💡 TIP: Usa SUPABASE_SCHEMAS['{tabla}'] para verificar campos disponibles
💡 Ejemplo: SUPABASE_SCHEMAS['configuracion_bot']['modulos'] -> 'json'

📋 TABLAS COMUNES POR MÓDULO:
• configuracion_bot: SIEMPRE - Config y módulos activos de cada Nora
• {modulo}_specific_tables: Según el módulo que estés creando
• logs_errores: Para logging de errores del módulo
• usuarios_clientes: Si el módulo maneja permisos de usuarios

🔍 VERIFICAR ANTES DE USAR:
from clientes.aura.utils.quick_schemas import existe, columnas
if existe('{tabla}'):
    campos = columnas('{tabla}')
    print(f"Campos disponibles: {campos}")
"""

panel_cliente_{modulo}_bp = Blueprint(
    "panel_cliente_{modulo}_bp", __name__,
    url_prefix="/panel_cliente/<nombre_nora>/{modulo}"
)

@panel_cliente_{modulo}_bp.route("/")
def panel_cliente_{modulo}():
    # 🎯 PATRÓN OFICIAL: extracción de nombre_nora
    nombre_nora = request.path.split("/")[2]
    
    # ✅ VALIDACIÓN BD: Verificar que la Nora existe
    from clientes.aura.utils.supabase_client import supabase
    config = supabase.table('configuracion_bot') \
        .select('modulos') \
        .eq('nombre_nora', nombre_nora) \
        .single() \
        .execute()
    
    if not config.data:
        return "Nora no encontrada", 404
    
    return render_template("panel_cliente_{modulo}/index.html", 
                         nombre_nora=nombre_nora)
```

#### 3. **Template auto-generado**:
```html
<!-- index.html (generado automáticamente) -->
{% extends "base_cliente.html" %}

{% block titulo %}{icono} {nombre_formateado} - {{ nombre_nora|title }}{% endblock %}

{% block contenido %}
<div class="max-w-4xl mx-auto py-8">
    <div class="bg-white rounded-lg shadow-sm p-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-4">
            {icono} {nombre_formateado}
        </h1>
        
        <p class="text-gray-600 mb-6">
            {descripcion} para {{ nombre_nora|title }}.
        </p>
        
        <!-- Contenido del módulo aquí -->
        <div class="text-center py-8">
            <p class="text-gray-500">
                ✨ Módulo creado automáticamente
            </p>
        </div>
    </div>
</div>
{% endblock %}
```

#### 4. **Registro Supabase automático**:
```sql
-- Auto-ejecutado por el creador
INSERT INTO modulos_disponibles (nombre, descripcion, icono, ruta) VALUES 
('{nombre_modulo}', '{descripcion}', '{icono}', 'panel_cliente_{modulo}.panel_cliente_{modulo}_bp');

-- Auto-activación para la Nora actual
UPDATE configuracion_bot 
SET modulos = jsonb_set(modulos, '{{"{modulo}"}}', 'true', true)
WHERE nombre_nora = '{nombre_nora}';
```

#### 5. **Actualización automática de esquemas**:
```python
# Auto-ejecutado al final del proceso
import subprocess
subprocess.run(['python', 'generar_supabase_schema.py'], check=True)
print("✅ Esquemas de BD actualizados automáticamente")
```

### 🎯 Ventajas de la creación automática:

1. **Consistencia total** - Todos los módulos siguen el mismo patrón
2. **Sin errores manuales** - Blueprint, templates y BD se configuran correctamente
3. **Inmediatamente funcional** - El módulo aparece activado en el panel
4. **Patrones oficiales** - Usa `request.path.split("/")[2]` para nombre_nora
5. **Actualización de esquemas** - BD schemas actualizados automáticamente

💡 **Resultado**: Módulo 100% funcional en segundos, sin intervención manual.

## � Schemas de BD como regla obligatoria

### 🎯 **REGLA OFICIAL**: Todo módulo debe documentar sus schemas

**En CADA archivo Python del módulo**, incluir este header:

```python
"""
📊 SCHEMAS DE BD QUE USA ESTE ARCHIVO:

📋 TABLAS PRINCIPALES:
• {tabla_principal}: {descripcion_breve}
  └ Campos clave: {campo1}, {campo2}, {campo3}
  
• {tabla_secundaria}: {descripcion_breve}  
  └ Campos clave: {campo1}, {campo2}

🔗 RELACIONES:
• {tabla_a} -> {tabla_b} via {campo_relacion}

💡 VERIFICAR SCHEMAS:
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas

if existe('mi_tabla'):
    campos = columnas('mi_tabla')
    tipo_campo = SUPABASE_SCHEMAS['mi_tabla']['mi_campo']
"""
```

### ✅ Ejemplo real - Módulo Meta Ads:

```python
"""
📊 SCHEMAS DE BD QUE USA ESTE ARCHIVO:

📋 TABLAS PRINCIPALES:
• meta_ads_anuncios_detalle: Métricas detalladas de cada anuncio
  └ Campos clave: ad_id(string_numeric), clicks(integer), costo(numeric), alcance(integer)
  
• meta_ads_cuentas: Cuentas publicitarias conectadas
  └ Campos clave: id_cuenta_publicitaria(text), nombre_cliente(text), conectada(boolean)
  
• meta_ads_reportes_semanales: Reportes consolidados semanales
  └ Campos clave: empresa_id(text), fecha_inicio(date), importe_gastado_anuncios(numeric)
  
• facebook_paginas: Páginas de Facebook vinculadas
  └ Campos clave: page_id(string_numeric), nombre_pagina(text), activa(boolean)

🔗 RELACIONES:
• meta_ads_cuentas -> meta_ads_anuncios_detalle via id_cuenta_publicitaria
• facebook_paginas -> meta_publicaciones_webhook via page_id
• configuracion_bot -> TODOS via nombre_nora

💡 VERIFICAR SCHEMAS:
from clientes.aura.utils.quick_schemas import existe, columnas
if existe('meta_ads_anuncios_detalle'):
    campos = columnas('meta_ads_anuncios_detalle')
    # Resultado: ['ad_id', 'clicks', 'costo', 'alcance', ...]
"""
```

### 🛠️ Herramientas disponibles:

#### 1. **`supabase_schemas.py`** - Schema completo:
```python
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS

# Ver estructura completa de una tabla
print(SUPABASE_SCHEMAS['meta_ads_anuncios_detalle'])
# {'ad_id': 'string_numeric', 'clicks': 'integer', 'costo': 'numeric', ...}
```

#### 2. **`quick_schemas.py`** - Verificación rápida:
```python
from clientes.aura.utils.quick_schemas import existe, columnas

# Verificar si tabla existe
if existe('mi_tabla'):
    print("✅ Tabla existe")
    
# Ver solo nombres de columnas
campos = columnas('mi_tabla') 
print(f"Campos: {campos}")
```

### 🚫 **PROHIBIDO**: Inventar tablas

```python
# ❌ MAL - Tabla inventada
result = supabase.table('inventario_productos').select('*').execute()

# ✅ BIEN - Verificar primero
from clientes.aura.utils.quick_schemas import existe
if existe('inventario_productos'):
    result = supabase.table('inventario_productos').select('*').execute()
else:
    print("❌ Tabla 'inventario_productos' no existe")
    # Usar tabla alternativa o crear la tabla primero
```

### 📋 **Template para nuevos módulos**:

```python
# Al inicio de CADA archivo Python del módulo:

"""
📊 SCHEMAS DE BD QUE USA ESTE ARCHIVO:

📋 TABLAS PRINCIPALES:
• configuracion_bot: Config de cada Nora (OBLIGATORIO EN TODOS LOS MÓDULOS)
  └ Campos: nombre_nora(text), modulos(json), ia_activa(boolean)

• [AGREGAR TABLAS ESPECÍFICAS DEL MÓDULO AQUÍ]

🔗 RELACIONES:
• configuracion_bot es el centro - filtra por nombre_nora SIEMPRE

💡 VERIFICACIÓN OBLIGATORIA:
from clientes.aura.utils.quick_schemas import existe, columnas
# Verificar cada tabla antes de usar
"""

from flask import Blueprint, render_template, request
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas

# Resto del código...
```

### 🎯 **Ventajas de esta regla**:

1. **No más errores** por tablas inexistentes
2. **Documentación automática** de dependencias  
3. **Onboarding rápido** para nuevos desarrolladores
4. **Refactoring seguro** - sabes qué tablas usa cada módulo
5. **GitHub Copilot inteligente** - entiende tu contexto de BD

Para módulos con mucha funcionalidad como `meta_ads`:

```bash
clientes/aura/routes/panel_cliente_meta_ads/
├── __init__.py
├── panel_cliente_meta_ads.py        # Blueprint principal
├── automatizaciones.py             # Sub-blueprint: automatizaciones
├── automatizacion_routes.py        # Sub-blueprint: rutas de automatización
├── campanas.py                     # Sub-blueprint: campañas
├── reportes.py                     # Sub-blueprint: reportes
├── estadisticas.py                 # Sub-blueprint: estadísticas
├── webhooks_meta.py                # Sub-blueprint: webhooks Meta
├── webhooks_api.py                 # Sub-blueprint: API webhooks
└── sincronizador.py                # Sub-blueprint: sincronización
```

## 🎨 Templates organizados:

```bash
clientes/aura/templates/panel_cliente_meta_ads/
├── index.html                      # Página principal
├── automatizacion.html             # Configuración automatización
├── reportes.html                   # Reportes de campañas
├── campanas_meta_ads.html          # Lista de campañas
├── audiencias_meta_ads.html        # Gestión de audiencias
├── estadisticas_ads.html           # Estadísticas detalladas
├── webhooks.html                   # Configuración webhooks
├── sincronizacion_manual.html      # Sincronización manual
└── lab.html                        # Laboratorio de pruebas
```

## 📁 Archivos estáticos separados:

**⚠️ IMPORTANTE**: Nunca meter JavaScript o CSS directamente en los templates HTML.

### Estructura de archivos estáticos:
```bash
static/
├── css/
│   ├── panel_cliente.css           # CSS general
│   └── modulos/
│       └── meta_ads/
│           ├── main.css           # CSS principal del módulo
│           ├── automatizacion.css # CSS específico de automatización
│           └── reportes.css       # CSS específico de reportes
└── js/
    ├── panel_cliente.js            # JS general
    └── modulos/
        └── meta_ads/
            ├── main.js            # JS principal del módulo
            ├── automatizacion.js  # JS específico de automatización
            └── reportes.js        # JS específico de reportes
```

### ⚠️ **REGLA CRÍTICA**: VERIFICAR BLOQUES DEL TEMPLATE BASE

**ANTES** de crear cualquier template, **VERIFICAR** qué bloques están disponibles en `base_cliente.html`:

```python
# 1. SIEMPRE leer base_cliente.html primero
from_file('clientes/aura/templates/base_cliente.html')

# 2. Identificar bloques disponibles
# BLOQUES REALES EN base_cliente.html:
# - {% block head_extra %}    ← Para CSS adicional
# - {% block contenido %}     ← Para contenido principal  
# - {% block scripts %}       ← Para JavaScript adicional

# 3. NO inventar bloques que no existen
```

### ✅ **Template CORRECTO** (bloques verificados):
```html
{% extends "base_cliente.html" %}

{% block titulo %}📊 Meta Ads - {{ nombre_nora|title }}{% endblock %}

<!-- ✅ CORRECTO: usar head_extra (existe en base_cliente.html) -->
{% block head_extra %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/modulos/meta_ads/main.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/modulos/meta_ads/automatizacion.css') }}">
{% endblock %}

{% block contenido %}
<!-- HTML aquí -->
{% endblock %}

<!-- ✅ CORRECTO: usar scripts (existe en base_cliente.html) -->
{% block scripts %}
<script src="{{ url_for('static', filename='js/modulos/meta_ads/main.js') }}"></script>
<script src="{{ url_for('static', filename='js/modulos/meta_ads/automatizacion.js') }}"></script>
{% endblock %}
```

### ❌ **Template INCORRECTO** (bloques inventados):
```html
{% extends "base_cliente.html" %}

<!-- ❌ ERROR: estilos_adicionales NO existe en base_cliente.html -->
{% block estilos_adicionales %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/modulos/meta_ads/main.css') }}">
{% endblock %}

<!-- ❌ ERROR: scripts_adicionales NO existe en base_cliente.html -->
{% block scripts_adicionales %}
<script src="{{ url_for('static', filename='js/modulos/meta_ads/main.js') }}"></script>
{% endblock %}
```

### 🔍 **Proceso de verificación obligatorio**:

```bash
# 1. Antes de crear template, verificar bloques disponibles
grep -n "{% block" clientes/aura/templates/base_cliente.html

# 2. Solo usar bloques que existen
# 3. Si necesitas bloques adicionales, modificar base_cliente.html primero
```

### ❌ **NO hacer esto** (JavaScript inline):
```html
<!-- ❌ MAL - JavaScript en el HTML -->
<script>
function cargarDatos() {
    fetch('/api/datos')
        .then(response => response.json())
        .then(data => console.log(data));
}
</script>
```

### ✅ **SÍ hacer esto** (JavaScript separado):
```html
<!-- ✅ BIEN - JavaScript externo -->
<script src="{{ url_for('static', filename='js/modulos/meta_ads/main.js') }}"></script>
```

Y en `static/js/modulos/meta_ads/main.js`:
```javascript
// Funciones del módulo Meta Ads
function cargarDatos() {
    fetch('/api/datos')
        .then(response => response.json())
        .then(data => console.log(data));
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    cargarDatos();
});
```

## 🔗 Enlaces entre templates:

```html
<!-- Navegación dentro del módulo -->
<nav class="mb-6">
    <a href="{{ url_for('panel_cliente_meta_ads_bp.panel_cliente_meta_ads', nombre_nora=nombre_nora) }}"
       class="text-blue-600 hover:text-blue-800">
        🏠 Inicio
    </a>
    |
    <a href="{{ url_for('panel_cliente_meta_ads_bp.panel_automatizacion_campanas', nombre_nora=nombre_nora) }}"
       class="text-blue-600 hover:text-blue-800">
        ⚙️ Automatización
    </a>
    |
    <a href="{{ url_for('panel_cliente_meta_ads_bp.reportes_meta_ads', nombre_nora=nombre_nora) }}"
       class="text-blue-600 hover:text-blue-800">
        📊 Reportes
    </a>
</nav>
```

## ⚠️ Errores comunes:

1. **Nombre inconsistente**:
   ```python
   # ❌ MAL - Nombres no coinciden
   Blueprint("meta_ads_bp", __name__, ...)  # nombre diferente
   
   # ✅ BIEN - Nombres consistentes
   Blueprint("panel_cliente_meta_ads_bp", __name__, ...)
   ```

2. **Templates en lugar incorrecto**:
   ```bash
   # ❌ MAL
   templates/meta_ads/index.html
   
   # ✅ BIEN
   templates/panel_cliente_meta_ads/index.html
   ```

3. **Import incorrecto en __init__.py**:
   ```python
   # ❌ MAL - Import directo del archivo
   from panel_cliente_meta_ads import panel_cliente_meta_ads_bp
   
   # ✅ BIEN - Import relativo
   from .panel_cliente_meta_ads import panel_cliente_meta_ads_bp
   ```

4. **JavaScript/CSS inline en templates**:
   ```html
   <!-- ❌ MAL - JavaScript inline -->
   <script>
   function miFuncion() { ... }
   </script>
   
   <!-- ❌ MAL - CSS inline -->
   <style>
   .mi-clase { color: red; }
   </style>
   ```
   
   ```html
   <!-- ✅ BIEN - Archivos externos -->
   <link rel="stylesheet" href="{{ url_for('static', filename='css/modulos/meta_ads/main.css') }}">
   <script src="{{ url_for('static', filename='js/modulos/meta_ads/main.js') }}"></script>
   ```

5. **Archivos estáticos en lugar incorrecto**:
   ```bash
   # ❌ MAL
   static/meta_ads.js
   static/meta_ads.css
   
   # ✅ BIEN
   static/js/modulos/meta_ads/main.js
   static/css/modulos/meta_ads/main.css
   ```
