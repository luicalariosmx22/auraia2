# ⚙️ Registro del módulo

Un módulo necesita 3 pasos para funcionar completamente:

## 1. 📊 Tabla `modulos_disponibles` (Supabase)

Registra el módulo en la base de datos:

```json
{
  "nombre": "meta_ads",
  "descripcion": "Gestión de campañas de Facebook e Instagram",
  "icono": "�",
  "ruta": "panel_cliente_meta_ads.panel_cliente_meta_ads_bp"
}
```

### Campos importantes:
- **`id`**: UUID único generado automáticamente
- **`nombre`**: Identificador único (snake_case)
- **`descripcion`**: Texto que aparece en el panel
- **`icono`**: Emoji que se muestra en la tarjeta
- **`ruta`**: Ruta del blueprint (formato: `archivo.blueprint_name`)
- **`archivo_principal`**: Archivo Python principal (opcional)

## 2. 🤖 Activación por Nora (`configuracion_bot`)

Activa el módulo para una Nora específica:

```json
{
  "nombre_nora": "aura",
  "modulos": {
    "meta_ads": true,
    "google_ads": true,
    "tareas": true,
    "redes_sociales": true,
    "contactos": true,
    "pagos": false
  }
}
```

## 3. 🔗 Registro dinámico (`registro_dinamico.py`)

**FUNCIÓN OFICIAL COMPLETA DEL SISTEMA**:

### Función principal de registro
```python
# En clientes/aura/registro/registro_dinamico.py

def registrar_modulos_dinamicos(app, nombre_nora=None):
    """Registra módulos dinámicamente según configuración de Supabase"""
    try:
        # Obtener módulos activos desde configuración_bot
        modulos_activos = obtener_modulos_activos(nombre_nora)
        
        # Registrar cada módulo activo
        for modulo in modulos_activos:
            registrar_modulo(app, modulo, nombre_nora)
            
    except Exception as e:
        print(f"❌ Error en registro dinámico: {e}")

def obtener_modulos_activos(nombre_nora):
    """Obtiene módulos activos desde configuracion_bot"""
    from clientes.aura.utils.supabase_client import supabase
    
    result = supabase.table('configuracion_bot') \
        .select('modulos') \
        .eq('nombre_nora', nombre_nora) \
        .single() \
        .execute()
    
    if result.data and result.data.get('modulos'):
        # Filtrar solo módulos activos (valor true)
        modulos = result.data['modulos']
        return [mod for mod, activo in modulos.items() if activo]
    
    return []
```

### Función de registro individual
```python
def registrar_modulo(app, modulo, nombre_nora):
    """Registra un módulo específico con manejo de errores"""
    try:
        # Meta Ads - Módulo principal con submódulos
        if modulo == "meta_ads":
            from clientes.aura.routes.panel_cliente_meta_ads import panel_cliente_meta_ads_bp
            from clientes.aura.routes.panel_cliente_meta_ads.automatizacion_routes import automatizacion_routes_bp
            from clientes.aura.routes.panel_cliente_meta_ads.webhooks_api import webhooks_api_bp
            
            safe_register_blueprint(app, panel_cliente_meta_ads_bp)
            safe_register_blueprint(app, automatizacion_routes_bp)
            safe_register_blueprint(app, webhooks_api_bp)
            print(f"✅ Módulo meta_ads registrado")
        
        # Google Ads
        elif modulo == "google_ads":
            from clientes.aura.routes.panel_cliente_google_ads import panel_cliente_google_ads_bp
            safe_register_blueprint(app, panel_cliente_google_ads_bp)
            print(f"✅ Módulo google_ads registrado")
        
        # Tareas - Sistema complejo
        elif modulo == "tareas":
            from clientes.aura.routes.panel_cliente_tareas import panel_cliente_tareas_bp
            safe_register_blueprint(app, panel_cliente_tareas_bp)
            print(f"✅ Módulo tareas registrado")
        
        # Redes Sociales
        elif modulo == "redes_sociales":
            from clientes.aura.routes.panel_cliente_redes_sociales import panel_cliente_redes_sociales_bp
            safe_register_blueprint(app, panel_cliente_redes_sociales_bp)
            print(f"✅ Módulo redes_sociales registrado")
        
        # Contactos
        elif modulo == "contactos":
            from clientes.aura.routes.panel_cliente_contactos import panel_cliente_contactos_bp
            safe_register_blueprint(app, panel_cliente_contactos_bp)
            print(f"✅ Módulo contactos registrado")
        
        # Pagos
        elif modulo == "pagos":
            from clientes.aura.routes.panel_cliente_pagos import panel_cliente_pagos_bp
            safe_register_blueprint(app, panel_cliente_pagos_bp)
            print(f"✅ Módulo pagos registrado")
        
        else:
            print(f"⚠️ Módulo desconocido: {modulo}")
            
    except ImportError as e:
        print(f"❌ Error importando {modulo}: {e}")
    except Exception as e:
        print(f"❌ Error registrando {modulo}: {e}")

def safe_register_blueprint(app, blueprint):
    """Registra blueprint con validación de duplicados"""
    try:
        # Verificar si ya está registrado
        for registered_blueprint in app.blueprints.values():
            if registered_blueprint.name == blueprint.name:
                print(f"⚠️ Blueprint {blueprint.name} ya registrado")
                return
        
        # Registrar blueprint
        app.register_blueprint(blueprint)
        
    except Exception as e:
        print(f"❌ Error registrando blueprint {blueprint.name}: {e}")
```

## 🚀 Proceso completo paso a paso:

### Paso 1: Insertar en Supabase
```sql
INSERT INTO modulos_disponibles (nombre, descripcion, icono, ruta) VALUES 
('google_maps', 'Gestión de ubicaciones, rutas y puntos de interés', '🗺️', 'panel_cliente_google_maps.panel_cliente_google_maps_bp');
```

### Paso 2: Activar para Nora
```sql
UPDATE configuracion_bot 
SET modulos = jsonb_set(modulos, '{google_maps}', 'true', true)
WHERE nombre_nora = 'aura';
```

### Paso 3: Código en registro_dinamico.py
```python
# Buscar esta sección en registro_dinamico.py:
if "google_maps" in modulos:
    from clientes.aura.routes.panel_cliente_google_maps import panel_cliente_google_maps_bp
    safe_register_blueprint(app, panel_cliente_google_maps_bp, 
                          url_prefix=f"/panel_cliente/{nombre_nora}/google_maps")
    print(f"✅ Módulo de google_maps registrado")
```

## 🔍 Verificar que funciona:

### 1. Check en logs del servidor:
```
✅ Módulo de google_maps registrado
```

### 2. URL accesible:
```
http://localhost:5000/panel_cliente/aura/google_maps/
```

### 3. Aparece en panel principal:
- Tarjeta con icono 🗺️
- Descripción del módulo
- Enlace funcionando

## ⚠️ Errores comunes:

### 1. Ruta incorrecta en BD:
```json
// ❌ MAL
"ruta": "google_maps.panel_cliente_google_maps_bp"

// ✅ BIEN  
"ruta": "panel_cliente_google_maps.panel_cliente_google_maps_bp"
```

### 2. Import path incorrecto:
```python
# ❌ MAL - Path absoluto
from panel_cliente_google_maps import panel_cliente_google_maps_bp

# ✅ BIEN - Path relativo desde routes/
from clientes.aura.routes.panel_cliente_google_maps import panel_cliente_google_maps_bp
```

### 3. Nombre inconsistente:
```python
# ❌ MAL - Nombres diferentes
if "google_maps" in modulos:  # nombre en BD
    from ...google_maps_module import blueprint  # archivo diferente

# ✅ BIEN - Nombres consistentes
if "google_maps" in modulos:  # mismo nombre
    from ...panel_cliente_google_maps import panel_cliente_google_maps_bp
```

### 4. Módulo no activado:
```json
// ❌ Módulo existe en BD pero no está activado
{
  "nombre_nora": "aura",
  "modulos": {
    "tareas": true
    // "google_maps": true  ← Falta esta línea
  }
}
```

## 🎯 Template para nuevos módulos:

```python
# 1. Crear archivo: clientes/aura/routes/panel_cliente_MODULO/panel_cliente_MODULO.py
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

```sql
-- 2. Insertar en BD
INSERT INTO modulos_disponibles (nombre, descripcion, icono, ruta) VALUES 
('MODULO', 'Descripción del módulo', '🔧', 'panel_cliente_MODULO.panel_cliente_MODULO_bp');
```

```sql
-- 3. Activar para Nora
UPDATE configuracion_bot 
SET modulos = jsonb_set(modulos, '{MODULO}', 'true', true)
WHERE nombre_nora = 'aura';
```

```python
# 4. Registrar en registro_dinamico.py
if "MODULO" in modulos:
    from clientes.aura.routes.panel_cliente_MODULO import panel_cliente_MODULO_bp
    safe_register_blueprint(app, panel_cliente_MODULO_bp, url_prefix=f"/panel_cliente/{nombre_nora}/MODULO")
    print(f"✅ Módulo de MODULO registrado")
```
