# 🌐 Multi-Nora y `nombre_nora`

## 📌 Regla oficial nombre_nora en Nora AI

**Objetivo**: Mantener la compatibilidad Multi-Nora en todo el backend y evitar errores como `duplicate argument` o `NoneType` en `nombre_nora`.

---

## 1️⃣ Definición en el backend principal del módulo

Cuando declaras el blueprint principal de un módulo, **SIEMPRE** incluye `<nombre_nora>` en el `url_prefix`:

```python
# panel_cliente_meta_ads.py
panel_cliente_meta_ads_bp = Blueprint(
    "panel_cliente_meta_ads_bp", __name__,
    url_prefix="/panel_cliente/<nombre_nora>/meta_ads"
)
```

💡 Esto garantiza que **TODAS** las rutas de ese blueprint reciban `nombre_nora` de forma automática.

---

## 2️⃣ Uso dentro del archivo principal

**Convención Nora**: No poner `nombre_nora` como parámetro directo de la función, sino obtenerlo de `request.view_args`:

```python
@panel_cliente_meta_ads_bp.route("/")
def index():
    nombre_nora = request.view_args.get("nombre_nora")
    return render_template("panel_cliente_meta_ads/index.html", nombre_nora=nombre_nora)
```

✅ Flask permite usarlo como parámetro en la función, pero en Nora lo evitamos para mantener consistencia y prevenir errores al pasar valores entre submódulos.

---

## 3️⃣ Submódulos o archivos separados dentro del módulo

Cuando creas rutas en archivos aparte (submódulos), mantén la misma convención:

```python
# campañas.py dentro de panel_cliente_meta_ads/
from flask import Blueprint, request, render_template

campañas_bp = Blueprint(
    "campañas_bp", __name__,
    url_prefix="/panel_cliente/<nombre_nora>/meta_ads/campañas"
)

@campañas_bp.route("/")
def listado_campañas():
    nombre_nora = request.view_args.get("nombre_nora")
    # ...
```

### 💡 Helper para compartir nombre_nora entre submódulos

Si quieres compartir `nombre_nora` entre submódulos sin repetir código:

**Opción 1**: Usa un helper en utils:
```python
def get_nombre_nora():
    return request.view_args.get("nombre_nora")
```

**Opción 2**: Usa `url_value_preprocessor` en el blueprint principal para guardarlo en `g.nombre_nora`.

---

## 4️⃣ Llamadas entre funciones y submódulos

Si llamas desde un submódulo a una función en otro archivo que necesita `nombre_nora`, pásalo siempre como argumento explícito:

```python
# En campañas.py
procesar_campañas(nombre_nora, datos)
```

Y en la función receptora:
```python
def procesar_campañas(nombre_nora, datos):
    # ...
```

⚠️ **No dependas de variables globales o parsing de URL.**

---

## 5️⃣ Ejemplo completo

### Estructura de módulo con submódulos:
```bash
panel_cliente_meta_ads/
├── __init__.py
├── panel_cliente_meta_ads.py   # ← blueprint principal
├── campañas.py                 # ← submódulo con su propio blueprint
└── reportes.py                 # ← otro submódulo
```

### Registro en `__init__.py`:
```python
from .panel_cliente_meta_ads import panel_cliente_meta_ads_bp
from .campañas import campañas_bp
from .reportes import reportes_bp
```

### Registro en `registro_dinamico.py`:
```python
if "meta_ads" in modulos:
    from clientes.aura.routes.panel_cliente_meta_ads import panel_cliente_meta_ads_bp
    from clientes.aura.routes.panel_cliente_meta_ads.campañas import campañas_bp
    from clientes.aura.routes.panel_cliente_meta_ads.reportes import reportes_bp

    safe_register_blueprint(app, panel_cliente_meta_ads_bp, 
                          url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads")
    safe_register_blueprint(app, campañas_bp, 
                          url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads/campañas")
    safe_register_blueprint(app, reportes_bp, 
                          url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads/reportes")
```

---

## 6️⃣ Errores prohibidos

### ❌ No parsear request.path:
```python
# ❌ PROHIBIDO
nombre_nora = request.path.split("/")[2]
```

### ❌ No hardcodear:
```python
# ❌ PROHIBIDO
nombre_nora = "aura"
```

### ❌ No registrar blueprints sin `<nombre_nora>` si son del panel cliente:
```python
# ❌ PROHIBIDO para panel cliente
Blueprint("panel_cliente_meta_ads_bp", __name__,
         url_prefix="/panel_cliente/meta_ads")  # Falta <nombre_nora>
```

---

## 🎯 URLs resultantes:

```
/panel_cliente/aura/meta_ads/
/panel_cliente/aura/meta_ads/campañas/
/panel_cliente/aura/meta_ads/reportes/
/panel_cliente/aura/redes_sociales/
/panel_cliente/nora2/contactos/
```

---

## 📌 Regla oficial: Validación de nombre_nora en Supabase

**Objetivo**: Evitar consultas inválidas y proteger datos entre distintas Noras.

### 1️⃣ Siempre validar que nombre_nora existe en Supabase antes de usarlo

**Tabla de referencia**: `configuracion_bot` → contiene todas las Noras activas.

**Campos clave**:
- `nombre_nora` (string, único)
- `modulos` (json con módulos activos)

**Ejemplo seguro**:
```python
from clientes.aura.utils.supabase_client import supabase

def validar_nombre_nora(nombre_nora):
    if not nombre_nora:
        return False
    
    result = supabase.table("configuracion_bot") \
        .select("nombre_nora") \
        .eq("nombre_nora", nombre_nora) \
        .execute()
    
    return bool(result.data)
```

**Uso en vista**:
```python
nombre_nora = request.view_args.get("nombre_nora")
if not validar_nombre_nora(nombre_nora):
    return "Error: Nora no encontrada", 404
```

### 2️⃣ Filtrar siempre por nombre_nora en todas las consultas

**❌ Mal**:
```python
# Esto puede devolver datos de otra Nora
result = supabase.table("tareas").select("*").execute()
```

**✅ Bien**:
```python
result = supabase.table("tareas") \
    .select("*") \
    .eq("nombre_nora", nombre_nora) \
    .execute()
```

### 3️⃣ En submódulos, pasar nombre_nora validado

Si tienes un submódulo que recibe `nombre_nora` por parámetro, no lo vuelvas a leer sin validarlo. Pásalo desde el backend principal ya validado.

### 4️⃣ En scripts o tareas automáticas

Cuando un script en `scripts/` necesita iterar por todas las Noras:

```python
noras = supabase.table("configuracion_bot").select("nombre_nora").execute()
for nora in noras.data:
    procesar_nora(nora["nombre_nora"])
```

💡 Así no usas nombres duros ni duplicas listas.

### 5️⃣ Errores comunes a evitar

- ❌ Usar `nombre_nora` sin verificar si existe en `configuracion_bot`
- ❌ No filtrar por `nombre_nora` en tablas multi-Nora (puede filtrar datos cruzados)
- ❌ Hardcodear valores (`nombre_nora = "aura"`)
- ❌ Confiar en que `request.view_args.get("nombre_nora")` siempre traerá algo válido

---

## 🎯 Buenas prácticas:

1. **Siempre validar nombre_nora**:
   ```python
   nombre_nora = request.view_args.get("nombre_nora")
   if not validar_nombre_nora(nombre_nora):
       return "Error: Nora no encontrada", 404
   ```

2. **Pasar a templates**:
   ```python
   return render_template("index.html", 
                        nombre_nora=nombre_nora,
                        modulo="meta_ads")
   ```

3. **Usar en consultas DB con filtro**:
   ```python
   # Filtrar por nora específica SIEMPRE
   result = supabase.table('configuracion_bot') \
       .select('*') \
       .eq('nombre_nora', nombre_nora) \
       .execute()
   ```

4. **Validar antes de operaciones críticas**:
   ```python
   def crear_tarea(nombre_nora, datos_tarea):
       if not validar_nombre_nora(nombre_nora):
           raise ValueError("Nora inválida")
       
       # Proceder con seguridad
       result = supabase.table('tareas').insert({
           'nombre_nora': nombre_nora,
           **datos_tarea
       }).execute()
   ```
