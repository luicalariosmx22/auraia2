# 🧾 Buenas prácticas

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
---

## 🎨 **REGLA CRÍTICA**: Verificación de templates y bloques

### 🚨 **PROBLEMA REAL**: Templates con bloques inexistentes

**ANTES** de crear cualquier template, **VERIFICAR** qué bloques están disponibles en `base_cliente.html`:

```python
# 1. SIEMPRE leer base_cliente.html primero
read_file('clientes/aura/templates/base_cliente.html')

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

{% block titulo %}📅 Agenda - {{ nombre_nora|title }}{% endblock %}

<!-- ✅ CORRECTO: usar head_extra (existe en base_cliente.html) -->
{% block head_extra %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/modulos/agenda/main.css') }}">
{% endblock %}

{% block contenido %}
<!-- HTML del módulo aquí -->
{% endblock %}

<!-- ✅ CORRECTO: usar scripts (existe en base_cliente.html) -->
{% block scripts %}
<script src="{{ url_for('static', filename='js/modulos/agenda/main.js') }}"></script>
{% endblock %}
```

### ❌ **Template INCORRECTO** (bloques inventados):

```html
{% extends "base_cliente.html" %}

<!-- ❌ ERROR: estilos_adicionales NO existe en base_cliente.html -->
{% block estilos_adicionales %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/modulos/agenda/main.css') }}">
{% endblock %}

<!-- ❌ ERROR: scripts_adicionales NO existe en base_cliente.html -->
{% block scripts_adicionales %}
<script src="{{ url_for('static', filename='js/modulos/agenda/main.js') }}"></script>
{% endblock %}
```

### 🔍 **Proceso de verificación obligatorio**:

```powershell
# 1. Antes de crear template, verificar bloques disponibles en PowerShell
Select-String -Path "clientes\aura\templates\base_cliente.html" -Pattern "{% block"

# 2. Solo usar bloques que existen
# 3. Si necesitas bloques adicionales, modificar base_cliente.html primero
```

### 🎯 **Consecuencias de no verificar**:

- ❌ **CSS no carga** - El bloque no existe, CSS se ignora
- ❌ **JavaScript no funciona** - Scripts no se incluyen  
- ❌ **Tiempo perdido** - Debugging innecesario
- ❌ **Frustraciones** - "¿Por qué no funciona el CSS?"

### 💡 **Regla de oro**:

> **"No puedes poner ese tipo de cosas sin verificar que existe... si no viene en la biblia"**

**SIEMPRE verificar la estructura del template base antes de crear templates hijos.**

---

## �🐍 Python

### Convenciones de nombres
```python
# ✅ BIEN - snake_case
def calcular_engagement_promedio():
    nombre_usuario = "aura"
    total_interacciones = 150
    
# ❌ MAL - camelCase o mixto
def calcularEngagementPromedio():
    nombreUsuario = "aura"
    totalInteracciones = 150
```

### Manejo de errores
```python
# ✅ BIEN - try/except específico
try:
    result = supabase.table('usuarios').select('*').execute()
    return result.data
except Exception as e:
    print(f"Error obteniendo usuarios: {e}")
    return []

# ❌ MAL - sin manejo de errores
result = supabase.table('usuarios').select('*').execute()
return result.data  # Puede fallar sin control
```

### Variables de entorno
```python
# ✅ BIEN - siempre os.getenv()
import os
SUPABASE_URL = os.getenv("SUPABASE_URL")
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL no configurada")

# ❌ MAL - hardcodeado
SUPABASE_URL = "https://sylqljdiiyhtgtrghwjk.supabase.co"
```

### Docstrings
```python
# ✅ BIEN - documentar funciones importantes
def calcular_engagement_pagina(page_id, dias=7):
    """
    Calcula el engagement promedio de una página en los últimos días.
    
    Args:
        page_id (str): ID de la página de Facebook
        dias (int): Número de días a analizar (default: 7)
    
    Returns:
        dict: {
            'total_interacciones': int,
            'engagement_rate': float,
            'periodo': str
        }
    """
    # Lógica aquí
    pass
```

### Imports organizados
```python
# ✅ BIEN - imports ordenados
# Librerías estándar
import os
from datetime import datetime, timedelta

# Librerías externas
from flask import Blueprint, render_template, request
from supabase import create_client

# Imports locales
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.helpers import calcular_engagement
```

---

## 🌐 JavaScript

### Variables modernas
```javascript
// ✅ BIEN - let/const
const API_BASE_URL = '/panel_cliente/aura/api';
let currentPage = 1;

function cargarDatos() {
    const datos = obtenerDatos();
    // Lógica aquí
}

// ❌ MAL - var
var API_BASE_URL = '/panel_cliente/aura/api';
var currentPage = 1;
```

### Async/await
```javascript
// ✅ BIEN - async/await moderno
async function cargarPaginasFacebook() {
    try {
        const response = await fetch('/api/facebook/paginas');
        const datos = await response.json();
        mostrarPaginas(datos);
    } catch (error) {
        console.error('Error cargando páginas:', error);
        mostrarError('No se pudieron cargar las páginas');
    }
}

// ❌ MAL - callbacks anidados
function cargarPaginasFacebook() {
    fetch('/api/facebook/paginas')
        .then(response => response.json())
        .then(datos => mostrarPaginas(datos))
        .catch(error => console.error(error));
}
```

### Código modular
```javascript
// ✅ BIEN - módulos organizados
const FacebookModule = {
    init() {
        this.bindEvents();
        this.cargarDatos();
    },
    
    bindEvents() {
        document.querySelector('#refresh-btn').addEventListener('click', () => {
            this.cargarDatos();
        });
    },
    
    async cargarDatos() {
        // Lógica de carga
    }
};

// Inicializar cuando DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    FacebookModule.init();
});
```

### Evitar JavaScript inline
```html
<!-- ❌ MAL - JavaScript inline -->
<button onclick="eliminarTarea(123)">Eliminar</button>

<!-- ✅ BIEN - Event listeners separados -->
<button data-tarea-id="123" class="btn-eliminar">Eliminar</button>

<script>
document.querySelectorAll('.btn-eliminar').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const tareaId = e.target.dataset.tareaId;
        eliminarTarea(tareaId);
    });
});
</script>
```

---

## 🎨 CSS y Tailwind

### Organización de clases
```html
<!-- ✅ BIEN - clases organizadas -->
<div class="
    max-w-4xl mx-auto p-6
    bg-white rounded-lg shadow-sm
    border border-gray-200
    hover:shadow-md transition-shadow duration-200
">
    Contenido
</div>

<!-- ❌ MAL - clases desordenadas -->
<div class="bg-white p-6 max-w-4xl hover:shadow-md mx-auto rounded-lg border transition-shadow border-gray-200 shadow-sm duration-200">
    Contenido
</div>
```

### Componentes reutilizables
```html
<!-- ✅ BIEN - clases de componente -->
<style>
.tarjeta-modulo {
    @apply bg-white rounded-lg shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow;
}

.btn-primario {
    @apply bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors;
}
</style>

<div class="tarjeta-modulo">
    <h3>Título</h3>
    <button class="btn-primario">Acción</button>
</div>
```

---

## 🗂️ Templates y Jinja2

### ⚠️ **PROBLEMA CRÍTICO DETECTADO EN EL FRONTEND**

**INCONSISTENCIA**: Muchos templates NO usan `base_cliente.html` correctamente:

```html
<!-- ❌ MAL - Templates que usan DOCTYPE directamente -->
panel_cliente_ia.html
panel_cliente_meta_ads/automatizacion.html
panel_cliente_whatsapp_web.html
panel_cliente_respuestas.html
panel_cliente_envios.html
<!-- Y 10+ archivos más -->

<!-- ❌ MAL - Templates que usan layout.html en lugar de base_cliente.html -->
admin_debug_rutas.html → {% extends "layout.html" %}

<!-- ✅ BIEN - Templates que SÍ usan base_cliente.html correctamente -->
meta_ads_cuenta_ficha.html → {% extends "base_cliente.html" %}
panel_cliente_redes_sociales/index.html → {% extends "base_cliente.html" %}
```

### ✅ **SOLUCIÓN REQUERIDA**:

**TODOS los templates del panel cliente deben usar**:
```html
{% extends "base_cliente.html" %}
```

### Estructura clara correcta
```html
<!-- ✅ BIEN - estructura organizada -->
{% extends "base_cliente.html" %}

{% block titulo %}📊 Meta Ads - {{ nombre_nora|title }}{% endblock %}

{% block estilos_adicionales %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/modulos/meta_ads/dashboard.css') }}">
{% endblock %}

{% block contenido %}
<div class="dashboard-meta-ads">
    <header class="dashboard-header">
        <h1>Dashboard Meta Ads</h1>
    </header>
    
    <main class="dashboard-content">
        <!-- Contenido principal -->
    </main>
</div>
{% endblock %}

{% block scripts_adicionales %}
<script src="{{ url_for('static', filename='js/modulos/meta_ads/dashboard.js') }}"></script>
{% endblock %}
```

### ❌ **ERRORES CRÍTICOS A CORREGIR**:

```html
<!-- ❌ MAL - Template standalone sin base -->
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Control IA - Nora {{ nombre_nora | default("Desconocida") }}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/admin_dashboard.css') }}">
</head>
<body>
    <!-- Duplica header, nav, estilos, etc. -->
</body>
</html>

<!-- ✅ BIEN - Usar base_cliente.html -->
{% extends "base_cliente.html" %}

{% block titulo %}🤖 Control IA - {{ nombre_nora|title }}{% endblock %}

{% block contenido %}
<div class="ia-control">
    <!-- Solo el contenido específico -->
</div>
{% endblock %}
```

### 📋 **LISTA DE TEMPLATES QUE NECESITAN CORRECCIÓN**:

```bash
# ❌ Templates con DOCTYPE directo (requieren refactoring):
panel_cliente_ia.html
panel_cliente_meta_ads/automatizacion.html  
panel_cliente_whatsapp_web.html
panel_cliente_respuestas.html
panel_cliente_envios.html
panel_chat.html
whatsapp_integration.html
registro_usuarios.html
login.html

# ✅ Templates que YA usan base_cliente.html correctamente:
meta_ads_cuenta_ficha.html
panel_cliente_redes_sociales/index.html
panel_cliente_clientes.html
panel_cliente_encuestas/index.html
```

### 🔧 **PROCESO DE CORRECCIÓN**:

1. **Identificar template con DOCTYPE directo**
2. **Extraer solo el contenido del <body>**
3. **Reemplazar con estructura base_cliente.html**
4. **Mover CSS inline a archivos separados**
5. **Verificar que todas las variables se pasen correctamente**

```html
<!-- ANTES: Template completo -->
<!DOCTYPE html>
<html>
<head>
    <title>Mi Módulo</title>
    <style>
        .mi-clase { color: red; }
    </style>
</head>
<body>
    <h1>Contenido</h1>
</body>
</html>

<!-- DESPUÉS: Template con herencia -->
{% extends "base_cliente.html" %}

{% block titulo %}Mi Módulo{% endblock %}

{% block estilos_adicionales %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/modulos/mi_modulo.css') }}">
{% endblock %}

{% block contenido %}
<h1>Contenido</h1>
{% endblock %}
```

### Filtros útiles
```html
<!-- Formateo de números -->
<span>{{ seguidores|number_format }}</span>
<!-- Resultado: 1,234,567 -->

<!-- Formateo de fechas -->
<time>{{ fecha|strftime('%d/%m/%Y') }}</time>
<!-- Resultado: 08/08/2025 -->

<!-- Texto seguro -->
<p>{{ descripcion|safe }}</p>
<!-- Permite HTML en descripcion -->

<!-- Truncar texto -->
<p>{{ texto_largo|truncate(100) }}</p>
<!-- Corta a 100 caracteres -->
```

---

## 🚀 Performance

### Consultas eficientes
```python
# ✅ BIEN - consulta específica
result = supabase.table('meta_publicaciones_webhook') \
    .select('tipo_item, created_time') \
    .eq('page_id', page_id) \
    .gte('created_time', timestamp_24h) \
    .limit(100) \
    .execute()

# ❌ MAL - consulta general
result = supabase.table('meta_publicaciones_webhook') \
    .select('*') \
    .execute()  # Trae TODOS los registros
```

### Caché cuando sea apropiado
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def obtener_configuracion_nora(nombre_nora):
    """Cache configuración por 5 minutos"""
    result = supabase.table('configuracion_bot') \
        .select('*') \
        .eq('nombre_nora', nombre_nora) \
        .execute()
    return result.data[0] if result.data else None
```

### Assets optimizados
```html
<!-- ✅ BIEN - recursos optimizados -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/panel_cliente.min.css') }}">
<script src="{{ url_for('static', filename='js/panel_cliente.min.js') }}" defer></script>

<!-- Imágenes optimizadas -->
<img src="{{ url_for('static', filename='images/logo_nora.webp') }}" 
     alt="Logo Nora" 
     width="100" 
     height="50" 
     loading="lazy">
```

---

## 🔒 Seguridad

### Validación de datos
```python
# ✅ BIEN - validar inputs
def actualizar_tarea(tarea_id, datos):
    # Validar ID
    if not tarea_id or not tarea_id.isdigit():
        return {"error": "ID inválido"}, 400
    
    # Validar datos requeridos
    if not datos.get('titulo'):
        return {"error": "Título requerido"}, 400
    
    # Procesar...
```

### Sanitización de outputs
```html
<!-- ✅ BIEN - escapar contenido del usuario -->
<h3>{{ titulo|e }}</h3>
<p>{{ descripcion|striptags|truncate(200) }}</p>

<!-- ❌ MAL - contenido sin escapar -->
<h3>{{ titulo|safe }}</h3>  <!-- Solo si confías 100% en el contenido -->
```

### Headers de seguridad
```python
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

---

## 🚨 Errores críticos encontrados en el proyecto

### ❌ **PROBLEMA REAL**: Templates sin herencia estándar

**Lista de templates que requieren corrección inmediata**:
```bash
# Templates con DOCTYPE directo (duplican estructura):
panel_cliente_ia.html
panel_cliente_meta_ads/automatizacion.html  
panel_cliente_whatsapp_web.html
panel_cliente_respuestas.html
panel_cliente_envios.html
panel_chat.html
whatsapp_integration.html
registro_usuarios.html
login.html
```

**Impacto del problema**:
- ❌ Inconsistencia visual entre módulos
- ❌ Duplicación de código CSS/HTML
- ❌ Dificulta mantenimiento global
- ❌ No reciben actualizaciones de `base_cliente.html`
- ❌ Navegación inconsistente

**Solución requerida**:
```html
<!-- ❌ ACTUAL (Problemático) -->
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Control IA</title>
    <link rel="stylesheet" href="...">
</head>
<body>
    <!-- HTML completo duplicado -->
</body>
</html>

<!-- ✅ CORREGIDO (Estándar) -->
{% extends "base_cliente.html" %}

{% block titulo %}🤖 Control IA{% endblock %}

{% block estilos_adicionales %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/modulos/ia_control.css') }}">
{% endblock %}

{% block contenido %}
<!-- Solo contenido específico del módulo -->
{% endblock %}
```

### ⚠️ **PRIORIDAD**: Estandarizar TODOS los templates del panel cliente

1. **Usar SIEMPRE**: `{% extends "base_cliente.html" %}`
2. **Mover CSS inline** a archivos separados
3. **Extraer JavaScript** a archivos modulares
4. **Verificar variables** se pasen correctamente
