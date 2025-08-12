# ⚙️ Registro del módulo

Un módulo necesita 2 pasos para funcionar completamente:

## 1. 📊 Tabla `modulos_disponibles` (Supabase)

Registra el módulo en la base de datos:

```json
{
  "nombre": "meta_ads",
  "descripcion": "Gestión de campañas de Facebook e Instagram",
  "icono": "📊",
  "ruta": "panel_cliente_meta_ads.panel_cliente_meta_ads_bp"
}
```

### Campos importantes:
- **`id`**: UUID único generado automáticamente
- **`nombre`**: Identificador único (snake_case)
- **`descripcion`**: Texto que aparece en el panel
- **`icono`**: Emoji que se muestra en la tarjeta
- **`ruta`**: Ruta del blueprint (formato: `archivo.blueprint_name`)

## 2. 🤖 Activación por Nora (`configuracion_bot`)

Activa el módulo para una Nora específica:

```json
{
  "nombre_nora": "aura",
  "modulos": {
    "meta_ads": true,
    "google_ads": true,
    "tareas": true,
    "contactos": true,
    "pagos": false
  }
}
```

## 3. 🔗 Registro automático desde Supabase

**SISTEMA REAL**: El registro es completamente automático desde Supabase, no manual.

### Función principal real (`registro_dinamico.py`)
```python
# clientes/aura/registro/registro_dinamico.py

def obtener_modulos_activos(nombre_nora):
    """Obtiene módulos activos desde configuracion_bot"""
    try:
        modulos_activados = supabase.table('configuracion_bot') \
            .select('modulos') \
            .eq('nombre_nora', nombre_nora) \
            .single() \
            .execute()
        return modulos_activados.data["modulos"] if modulos_activados.data else []
    except Exception as e:
        print(f"❌ Error al obtener módulos activos para {nombre_nora}: {e}")
        return []

def registrar_blueprints_por_nora(app, nombre_nora, safe_register_blueprint):
    """Registra blueprints automáticamente para una Nora específica"""
    try:
        # 1. OBTENER MÓDULOS ACTIVOS DESDE SUPABASE
        modulos = obtener_modulos_activos(nombre_nora)
        modulos_registrados = set()
        
        # 2. MÓDULOS BASE (siempre se registran)
        bp = crear_blueprint_panel_cliente(nombre_nora)
        safe_register_blueprint(app, bp, url_prefix=f"/panel_cliente/{nombre_nora}")
        
        # 3. MÓDULOS CONDICIONALES (según configuracion_bot)
        if "contactos" in modulos:
            registrar_modulo(app, "contactos", panel_cliente_contactos_bp, 
                           f"/panel_cliente/{nombre_nora}/contactos", modulos_registrados)
        
        if "tareas" in modulos:
            safe_register_blueprint(app, panel_cliente_tareas_bp, 
                                  url_prefix=f"/panel_cliente/{nombre_nora}/tareas")
            safe_register_blueprint(app, panel_tareas_gestionar_bp)
            safe_register_blueprint(app, panel_tareas_recurrentes_bp)
            safe_register_blueprint(app, panel_tareas_crud_bp)
            modulos_registrados.add("tareas")
        
        if "meta_ads" in modulos:
            from clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads import panel_cliente_meta_ads_bp
            safe_register_blueprint(app, panel_cliente_meta_ads_bp, 
                                  url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads")
            modulos_registrados.add("meta_ads")
        
        if "pagos" in modulos:
            # Importación dinámica para módulos complejos
            from clientes.aura.routes.panel_cliente_pagos import (
                panel_cliente_pagos_bp,
                panel_cliente_pagos_servicios_bp,
                panel_cliente_pagos_nuevo_bp,
                panel_cliente_pagos_recibo_bp
            )
            safe_register_blueprint(app, panel_cliente_pagos_bp, 
                                  url_prefix=f"/panel_cliente/{nombre_nora}/pagos")
            safe_register_blueprint(app, panel_cliente_pagos_servicios_bp, 
                                  url_prefix=f"/panel_cliente/{nombre_nora}/pagos/servicios")
            safe_register_blueprint(app, panel_cliente_pagos_nuevo_bp, 
                                  url_prefix=f"/panel_cliente/{nombre_nora}/pagos")
            safe_register_blueprint(app, panel_cliente_pagos_recibo_bp)
            modulos_registrados.add("pagos")
        
        # 4. MÓDULOS DINÁMICOS DESDE SUPABASE
        resultado = supabase.table("modulos_disponibles").select("nombre, ruta").execute()
        modulos_disponibles = resultado.data if resultado.data else []
        
        for item in modulos_disponibles:
            nombre_modulo = item["nombre"]
            ruta_import = item["ruta"]
            
            # Evitar duplicados
            if nombre_modulo in modulos_registrados:
                continue
                
            try:
                # Importación dinámica desde Supabase
                ruta_modulo = ruta_import.rsplit(".", 1)[0]  # Ej: 'panel_cliente_alertas'
                nombre_blueprint = ruta_import.split(".")[-1]  # Ej: 'panel_cliente_alertas_bp'
                
                modulo_importado = importlib.import_module(f"clientes.aura.routes.{ruta_modulo}")
                blueprint = getattr(modulo_importado, nombre_blueprint)
                
                ruta_url = f"/panel_cliente/{nombre_nora}/{nombre_modulo}"
                registrar_modulo(app, nombre_modulo, blueprint, ruta_url, modulos_registrados)
                
            except Exception as e:
                print(f"❌ Error al registrar módulo dinámico '{nombre_modulo}': {e}")
        
    except Exception as e:
        print(f"❌ Error al registrar blueprints dinámicos para {nombre_nora}: {e}")

def registrar_modulo(app, nombre_modulo, blueprint, ruta, modulos_registrados):
    """Registra un módulo con manejo de errores"""
    try:
        safe_register_blueprint(app, blueprint, url_prefix=ruta)
        print(f"✅ Módulo de {nombre_modulo} registrado")
        modulos_registrados.add(nombre_modulo)
        return True
    except Exception as e:
        print(f"❌ Error al registrar módulo de {nombre_modulo}: {e}")
        return False

def safe_register_blueprint(app, blueprint, **kwargs):
    """Registra blueprint con validación de duplicados"""
    if blueprint.name not in app.blueprints:
        app.register_blueprint(blueprint, **kwargs)
        print(f"✅ Blueprint '{blueprint.name}' registrado con prefijo '{kwargs.get('url_prefix', '')}'")
    else:
        print(f"⚠️ Blueprint '{blueprint.name}' ya estaba registrado.")
```

---

## 🚀 Tipos de módulos en el sistema real

### 1. **Módulos base (siempre activos)**
```python
# Panel cliente principal
bp = crear_blueprint_panel_cliente(nombre_nora)
safe_register_blueprint(app, bp, url_prefix=f"/panel_cliente/{nombre_nora}")

# Entrenamiento (siempre disponible)
safe_register_blueprint(app, panel_cliente_entrenamiento_bp, 
                       url_prefix=f"/panel_cliente/{nombre_nora}/entrenamiento")

# Webhook base
safe_register_blueprint(app, webhook_contactos_bp, url_prefix="/")
```

### 2. **Módulos condicionales (según configuracion_bot)**
```python
# Estos se registran solo si están en modulos["nombre"] = true

if "contactos" in modulos:
    registrar_modulo(app, "contactos", panel_cliente_contactos_bp, 
                   f"/panel_cliente/{nombre_nora}/contactos", modulos_registrados)

if "tareas" in modulos:
    # Módulo complejo con múltiples blueprints
    safe_register_blueprint(app, panel_cliente_tareas_bp, 
                          url_prefix=f"/panel_cliente/{nombre_nora}/tareas")
    safe_register_blueprint(app, panel_tareas_gestionar_bp)
    safe_register_blueprint(app, panel_tareas_recurrentes_bp)
    safe_register_blueprint(app, panel_tareas_crud_bp)

if "meta_ads" in modulos:
    from clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads import panel_cliente_meta_ads_bp
    safe_register_blueprint(app, panel_cliente_meta_ads_bp, 
                          url_prefix=f"/panel_cliente/{nombre_nora}/meta_ads")

if "google_ads" in modulos:
    registrar_modulo(app, "google_ads", panel_cliente_google_ads_bp, 
                   f"/panel_cliente/{nombre_nora}/google_ads", modulos_registrados)

if "qr_whatsapp_web" in modulos:
    # Importación dinámica para evitar conflictos de nombre
    from clientes.aura.routes.panel_cliente_whatsapp_web.panel_cliente_whatsapp_websocket import panel_cliente_whatsapp_web_bp as whatsapp_websocket_bp
    safe_register_blueprint(app, whatsapp_websocket_bp, 
                          url_prefix=f'/panel_cliente/{nombre_nora}/whatsapp')
```

### 3. **Módulos dinámicos (desde modulos_disponibles)**
```python
# Se obtienen automáticamente desde Supabase
resultado = supabase.table("modulos_disponibles").select("nombre, ruta").execute()
modulos_disponibles = resultado.data if resultado.data else []

for item in modulos_disponibles:
    nombre_modulo = item["nombre"]
    ruta_import = item["ruta"]  # Ej: "panel_cliente_alertas.panel_cliente_alertas_bp"
    
    # Importación dinámica
    ruta_modulo = ruta_import.rsplit(".", 1)[0]  # "panel_cliente_alertas"
    nombre_blueprint = ruta_import.split(".")[-1]  # "panel_cliente_alertas_bp"
    
    modulo_importado = importlib.import_module(f"clientes.aura.routes.{ruta_modulo}")
    blueprint = getattr(modulo_importado, nombre_blueprint)
    
    ruta_url = f"/panel_cliente/{nombre_nora}/{nombre_modulo}"
    registrar_modulo(app, nombre_modulo, blueprint, ruta_url, modulos_registrados)
```

---

## 🔍 Proceso completo paso a paso

### Paso 1: Insertar en `modulos_disponibles`
```sql
INSERT INTO modulos_disponibles (nombre, descripcion, icono, ruta) VALUES 
('inventario', 'Gestión de productos y stock', '📦', 'panel_cliente_inventario.panel_cliente_inventario_bp');
```

### Paso 2: Activar en `configuracion_bot`
```sql
UPDATE configuracion_bot 
SET modulos = jsonb_set(modulos, '{inventario}', 'true', true)
WHERE nombre_nora = 'aura';
```

### Paso 3: Reiniciar aplicación
```bash
# En local
python dev_start.py

# En Railway (automático al hacer git push)
```

### Verificar funcionamiento:
```
✅ Módulo de inventario registrado
✅ Blueprint 'panel_cliente_inventario_bp' registrado con prefijo '/panel_cliente/aura/inventario'
```

---

## ⚠️ Diferencias del sistema real vs documentación anterior

### ❌ **LO QUE NO EXISTE** (documentación incorrecta):
- Función `registrar_modulos_dinamicos()` manual
- Imports hardcodeados en archivo de registro
- Registro manual blueprint por blueprint

### ✅ **LO QUE SÍ EXISTE** (sistema real):
- Función `obtener_modulos_activos()` que lee desde Supabase
- Función `registrar_blueprints_por_nora()` que registra todo automáticamente
- Importación dinámica desde `modulos_disponibles`
- Sistema híbrido: módulos base + condicionales + dinámicos

---

## 🎯 Template para nuevos módulos

### 1. Crear módulo
```python
# clientes/aura/routes/panel_cliente_MODULO/panel_cliente_MODULO.py
from flask import Blueprint, render_template, request

panel_cliente_MODULO_bp = Blueprint(
    "panel_cliente_MODULO_bp", __name__,
    url_prefix="/panel_cliente/<nombre_nora>/MODULO"
)

@panel_cliente_MODULO_bp.route("/")
def panel_cliente_MODULO():
    nombre_nora = request.view_args.get("nombre_nora")
    return render_template("panel_cliente_MODULO/index.html", nombre_nora=nombre_nora)
```

### 2. Registrar en Supabase
```sql
INSERT INTO modulos_disponibles (nombre, descripcion, icono, ruta) VALUES 
('MODULO', 'Descripción del módulo', '🔧', 'panel_cliente_MODULO.panel_cliente_MODULO_bp');
```

### 3. Activar para Nora
```sql
UPDATE configuracion_bot 
SET modulos = jsonb_set(modulos, '{MODULO}', 'true', true)
WHERE nombre_nora = 'aura';
```

### 4. Reiniciar aplicación
- El sistema automáticamente detectará el nuevo módulo desde `modulos_disponibles`
- Realizará la importación dinámica
- Registrará el blueprint con la URL correcta

**Resultado**: Módulo 100% funcional sin tocar `registro_dinamico.py` 🎉

---

## 🔧 Troubleshooting

### Error: Módulo no aparece
1. ✅ Verificar que existe en `modulos_disponibles`
2. ✅ Verificar que está activado en `configuracion_bot`
3. ✅ Reiniciar aplicación
4. ✅ Revisar logs: `✅ Módulo de NOMBRE registrado`

### Error: Blueprint no se encuentra
1. ✅ Verificar campo `ruta` en `modulos_disponibles`
2. ✅ Verificar que el archivo Python existe
3. ✅ Verificar nombre del blueprint coincide

### Error: Importación dinámica falla
1. ✅ Verificar estructura de carpetas
2. ✅ Verificar que `__init__.py` existe
3. ✅ Verificar imports en el archivo principal

El sistema está diseñado para ser **100% automático** una vez configurado en Supabase.
