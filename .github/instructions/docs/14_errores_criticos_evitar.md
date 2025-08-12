# 🚨 Errores Críticos a Evitar

Esta guía documenta errores críticos encontrados en el desarrollo de Nora AI y cómo evitarlos.

---

## 🎨 Error #1: Usar bloques de template inexistentes

### 🔥 **CASO REAL**: Módulo Agenda - CSS no cargaba

**Problema identificado**: Template usando bloques que no existían en `base_cliente.html`

#### ❌ **Código problemático**:
```html
{% extends "base_cliente.html" %}

<!-- ERROR: estilos_adicionales NO existe -->
{% block estilos_adicionales %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/modulos/agenda/main.css') }}">
{% endblock %}

<!-- ERROR: scripts_adicionales NO existe -->
{% block scripts_adicionales %}
<script src="{{ url_for('static', filename='js/modulos/agenda/main.js') }}"></script>
{% endblock %}
```

#### ✅ **Solución aplicada**:
```html
{% extends "base_cliente.html" %}

<!-- CORRECTO: head_extra SÍ existe -->
{% block head_extra %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/modulos/agenda/main.css') }}">
{% endblock %}

<!-- CORRECTO: scripts SÍ existe -->
{% block scripts %}
<script src="{{ url_for('static', filename='js/modulos/agenda/main.js') }}"></script>
{% endblock %}
```

### 📋 **Bloques REALES disponibles en base_cliente.html**:
- ✅ `{% block head_extra %}` - Para CSS adicional
- ✅ `{% block titulo %}` - Para título de página
- ✅ `{% block contenido %}` - Para contenido principal
- ✅ `{% block scripts %}` - Para JavaScript adicional

### 🚫 **Bloques que NO existen** (no inventar):
- ❌ `{% block estilos_adicionales %}`
- ❌ `{% block scripts_adicionales %}`
- ❌ `{% block css_extra %}`
- ❌ `{% block js_extra %}`

### 🔍 **Proceso obligatorio de verificación**:

#### 1. **Antes de crear cualquier template**:
```powershell
# Verificar bloques disponibles
Select-String -Path "clientes\aura\templates\base_cliente.html" -Pattern "{% block"
```

#### 2. **Lectura obligatoria del template base**:
```python
# SIEMPRE hacer esto ANTES de crear templates
read_file('clientes/aura/templates/base_cliente.html')
```

#### 3. **Solo usar bloques verificados**:
```html
<!-- ✅ CORRECTO - Verificado que existe -->
{% block head_extra %}
<!-- CSS aquí -->
{% endblock %}

<!-- ❌ INCORRECTO - NO verificado -->
{% block estilos_personalizados %}
<!-- Este bloque NO existe -->
{% endblock %}
```

### 💡 **Regla de oro**:
> **"No puedes poner ese tipo de cosas sin verificar que existe... si no viene en la biblia"**

### 🎯 **Impacto del error**:
- ❌ CSS no se carga en el frontend
- ❌ JavaScript no funciona
- ❌ Tiempo perdido en debugging
- ❌ Frustraciones innecesarias

---

## 📊 Error #2: Asumir estructuras de BD sin verificar

### 🔥 **CASO POTENCIAL**: Usar tablas que no existen

#### ❌ **Código problemático**:
```python
# ERROR: Asumir que tabla existe
result = supabase.table('inventario_productos').select('*').execute()
```

#### ✅ **Solución obligatoria**:
```python
# CORRECTO: Verificar antes de usar
from clientes.aura.utils.quick_schemas import existe

if existe('inventario_productos'):
    result = supabase.table('inventario_productos').select('*').execute()
else:
    print("❌ Tabla 'inventario_productos' no existe")
    # Crear tabla o usar alternativa
```

### 🔍 **Herramientas de verificación**:
```python
from clientes.aura.utils.quick_schemas import existe, columnas

# Verificar tabla
if existe('mi_tabla'):
    campos = columnas('mi_tabla')
    print(f"Campos disponibles: {campos}")
```

---

## 🌐 Error #3: Rutas Flask sin nombre_nora

### 🔥 **CASO POTENCIAL**: Olvidar soporte multi-Nora

#### ❌ **Código problemático**:
```python
# ERROR: Ruta sin <nombre_nora>
Blueprint("mi_modulo_bp", __name__, url_prefix="/panel_cliente/mi_modulo")
```

#### ✅ **Solución obligatoria**:
```python
# CORRECTO: Incluir <nombre_nora>
Blueprint("panel_cliente_mi_modulo_bp", __name__, 
         url_prefix="/panel_cliente/<nombre_nora>/mi_modulo")
```

---

## 🔒 Error #4: Hardcodear variables sensibles

### 🔥 **CASO POTENCIAL**: Claves en código

#### ❌ **Código problemático**:
```python
# ERROR: Clave hardcodeada
META_ACCESS_TOKEN = "EAAPJAAprGjgBPCe4wJe1KWvePSX1Vg6nVx7j9..."
```

#### ✅ **Solución obligatoria**:
```python
# CORRECTO: Desde variables de entorno
import os
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
```

---

## 📁 Error #5: Archivos estáticos en lugar incorrecto

### 🔥 **CASO POTENCIAL**: CSS/JS en ubicación incorrecta

#### ❌ **Estructura problemática**:
```bash
static/
├── agenda.css          # ❌ MAL: No organizado
└── agenda.js           # ❌ MAL: No organizado
```

#### ✅ **Estructura correcta**:
```bash
static/
├── css/
│   └── modulos/
│       └── agenda/
│           └── main.css    # ✅ BIEN: Organizado
└── js/
    └── modulos/
        └── agenda/
            └── main.js     # ✅ BIEN: Organizado
```

---

## 🎯 Checklist anti-errores

### ✅ **Antes de crear templates**:
- [ ] Leer `base_cliente.html` completo
- [ ] Verificar qué bloques existen
- [ ] Solo usar bloques confirmados
- [ ] Probar que CSS/JS cargan

### ✅ **Antes de usar base de datos**:
- [ ] Verificar que tabla existe con `existe()`
- [ ] Ver campos disponibles con `columnas()`
- [ ] Documentar schemas en código
- [ ] Nunca asumir estructura

### ✅ **Antes de crear rutas**:
- [ ] Incluir `<nombre_nora>` en URL prefix
- [ ] Usar `request.view_args.get("nombre_nora")`
- [ ] Validar que nombre_nora existe
- [ ] Filtrar consultas BD por nombre_nora

### ✅ **Antes de usar APIs externas**:
- [ ] Variables desde `os.getenv()`
- [ ] Nunca hardcodear tokens
- [ ] Manejo de errores robusto
- [ ] Timeouts configurados

### ✅ **Antes de organizar archivos**:
- [ ] CSS en `static/css/modulos/{modulo}/`
- [ ] JS en `static/js/modulos/{modulo}/`
- [ ] Templates en `templates/panel_cliente_{modulo}/`
- [ ] Nunca inline CSS/JS

---

## 🎓 Lecciones aprendidas

### 📝 **Principio fundamental**:
> **SIEMPRE verificar antes de asumir**

### 🔍 **Metodología de verificación**:
1. **Leer documentación/código existente**
2. **Verificar con herramientas disponibles**
3. **Probar en entorno controlado**
4. **Solo entonces implementar**

### 💡 **Reglas de desarrollo defensivo**:
- ❌ **No asumir** que algo existe sin verificar
- ✅ **Verificar primero**, implementar después
- ✅ **Documentar** lo que encuentres para otros
- ✅ **Usar herramientas** de verificación disponibles

### 🎯 **Impacto de seguir estas reglas**:
- ✅ Menos tiempo perdido en debugging
- ✅ Código más robusto y confiable
- ✅ Experiencia de desarrollo más fluida
- ✅ Menos frustraciones y errores

---

## 📚 Referencias rápidas

- **Templates**: Solo `head_extra`, `contenido`, `scripts`
- **BD**: Usar `existe()` y `columnas()` antes de consultar
- **Rutas**: Siempre incluir `<nombre_nora>`
- **Variables**: Siempre `os.getenv()`
- **Archivos**: Organizar en `static/{tipo}/modulos/{modulo}/`

**Recuerda**: Estas reglas nacieron de errores reales. Seguirlas te ahorrará tiempo y frustraciones.
