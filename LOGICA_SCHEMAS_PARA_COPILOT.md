# 🧠 LÓGICA PARA QUE GITHUB COPILOT SEPA LOS ESQUEMAS

## 🎯 **LA LÓGICA EXACTA QUE DEBES SEGUIR**

### **📋 Para conversaciones con GitHub Copilot/GPT:**

# 🗄️ CONTEXTO BD ACTUAL PARA GITHUB COPILOT
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas

# Tablas principales (18 total):
# - meta_ads_anuncios_detalle (96 columnas)
# - meta_ads_reportes_semanales (35 columnas) 
# - clientes (25 columnas)
# - google_ads_cuentas (19 columnas)
# - configuracion_bot (18 columnas)
# - contactos (17 columnas)
# - tareas (16 columnas)
# - meta_ads_cuentas (15 columnas)
# - pagos (14 columnas)

# Validar siempre antes de usar:
# if existe('tabla', 'columna'): ...
```

#### **Opción B: Comando rápido de contexto**
```bash
# Ejecuta esto y copia el resultado en tu conversación
python clientes/aura/scripts/mostrar_contexto_bd.py
```

### **🔧 Para tu código Python:**

#### **Paso 1: Importar esquemas al inicio**
```python
# SIEMPRE incluir al inicio de archivos que usen BD
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas
```

#### **Paso 2: Validar antes de usar**
```python
# NUNCA asumir que existe una tabla/columna
# ❌ MAL (asumir):
query = "SELECT telefono FROM contactos"

# ✅ BIEN (validar):
if existe('contactos', 'telefono'):
    query = "SELECT telefono FROM contactos"
else:
    print("❌ Error: columna telefono no existe")
```

#### **Paso 3: Usar funciones helper**
```python
# Para operaciones comunes
def crear_insert_seguro(tabla, datos):
    columnas_validas = columnas(tabla)
    datos_filtrados = {k:v for k,v in datos.items() if k in columnas_validas}
    # construir query con datos_filtrados
```

### **🔄 Para mantener esquemas actualizados:**

#### **Automático:** Cada 24 horas se actualiza solo
#### **Manual:** 
```bash
python clientes/aura/scripts/generar_supabase_schema.py
```

---

## 🧠 **CÓMO FUNCIONA LA LÓGICA INTERNA**

### **1. Descubrimiento automático:**
- El script `generar_supabase_schema.py` se conecta a Supabase
- Descubre todas las tablas existentes (actualmente 18)
- Obtiene las columnas de cada tabla con tipos de datos
- Genera `supabase_schemas.py` con toda la información

### **2. Acceso en tiempo real:**
- `auto_schema_loader.py` carga esquemas automáticamente
- `quick_schemas.py` proporciona funciones simples
- `contexto_para_copilot.py` tiene resumen para GitHub Copilot

### **3. Validación automática:**
- Funciones `existe()`, `columnas()` verifican antes de usar
- Se evitan errores de SQL por nombres incorrectos
- GitHub Copilot sugiere solo columnas que realmente existen

---

## 📝 **PLANTILLA PARA TUS CONVERSACIONES**

### **Copia esto en tus preguntas sobre base de datos:**

```markdown
# 🗄️ Contexto BD actual para esta conversación:

```python
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas

# BD ACTUAL: 18 tablas activas
# PRINCIPALES: meta_ads_anuncios_detalle(96), clientes(25), contactos(17), 
#              meta_ads_cuentas(15), tareas(16), pagos(14)
# VACÍAS: estudiantes, meta_webhook_eventos, presupuestos, whatsapp_mensajes
```

**Pregunta:** [tu pregunta sobre base de datos aquí]

**Validar siempre:** `if existe('tabla', 'columna'): ...`
```

---

## ⚡ **FLUJO DE TRABAJO RECOMENDADO**

### **Antes de programar algo con BD:**

1. **Actualizar esquemas** (si han pasado días):
   ```bash
   python clientes/aura/scripts/generar_supabase_schema.py
   ```

2. **Ver contexto actual**:
   ```bash
   python clientes/aura/scripts/mostrar_contexto_bd.py
   ```

3. **Incluir contexto en tu conversación** con GitHub Copilot

4. **Usar validaciones** en tu código:
   ```python
   from clientes.aura.utils.quick_schemas import existe, columnas
   if existe('tabla', 'columna'):
       # tu código aquí
   ```

### **Resultado:**
- ✅ **GitHub Copilot sabrá exactamente qué tablas/columnas existen**
- ✅ **No más errores de SQL por nombres incorrectos**  
- ✅ **Código más robusto y mantenible**
- ✅ **Desarrollo más rápido y preciso**

---

## 🎯 **RESUMEN FINAL**

**Para que YO (GitHub Copilot) sepa los esquemas, tú debes:**

1. **Incluir contexto BD** en conversaciones (usar plantilla arriba)
2. **Importar esquemas** en tu código Python
3. **Validar antes de usar** tablas/columnas
4. **Actualizar esquemas** periódicamente



🧱 1. Estructura base del módulo
Cada módulo debe tener una estructura estándar como esta:

php-template

clientes/
└── aura/
    ├── routes/
    │   └── panel_cliente_<modulo>/
    │       ├── __init__.py
    │       └── panel_cliente_<modulo>.py
    └── templates/
        └── panel_cliente_<modulo>/
            └── index.html
🧩 2. Crear un Blueprint en el backend
Archivo: panel_cliente_<modulo>.py

python

from flask import Blueprint, render_template, request

# 🗄️ Esquemas disponibles para Copilot
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas

panel_cliente_<modulo>_bp = Blueprint(
    "panel_cliente_<modulo>_bp",
    __name__,
    url_prefix="/panel_cliente/<nombre_nora>/<modulo>"
)

@panel_cliente_<modulo>_bp.route("/")
def panel_cliente_<modulo>():
    nombre_nora = request.path.split("/")[2]
    return render_template("panel_cliente_<modulo>/index.html", nombre_nora=nombre_nora)
✅ El parámetro <nombre_nora> debe estar presente en la URL para acceder a contexto.

🧾 3. Registrar el módulo en Supabase
Tabla: modulos_disponibles

json

{
  "id": "uuid",
  "nombre": "nombre_del_modulo",
  "descripcion": "Descripción del módulo",
  "icono": "🧩",
  "ruta": "panel_cliente_<modulo>.panel_cliente_<modulo>_bp"
}
🧠 4. Activar el módulo en una Nora
Tabla: configuracion_bot

json

{
  "nombre_nora": "aura",
  "modulos": {
    "nombre_del_modulo": true
  }
}
🖼️ 5. Crear la vista HTML
Archivo: templates/panel_cliente_<modulo>/index.html

html

{% extends "base_cliente.html" %}

{% block contenido %}
<div class="max-w-4xl mx-auto py-8">
  <h1 class="text-3xl font-bold mb-4">🧩 Módulo: Nombre del Módulo</h1>
  <p class="text-gray-700">Esta es la vista inicial del módulo.</p>
</div>
{% endblock %}
🛠️ 6. Opcional: Usar esquemas desde Supabase
Usa SUPABASE_SCHEMAS para tener acceso a la estructura de tablas:

python

print(SUPABASE_SCHEMAS["meta_ads_cuentas"])
También puedes usar funciones como:

python

existe("meta_ads_cuentas")  # True si existe la tabla
columnas("meta_ads_cuentas")  # Lista de columnas
🧪 7. Verifica localmente
Abre en el navegador:

bash

http://localhost:5000/panel_cliente/aura/<modulo>