# Corrección de Rutas en Panel de Cliente

## Problemas Detectados y Soluciones

### 1. Error en el Redireccionamiento del Login

**Problema:**
```python
# En panel_cliente.py y otros módulos, redireccionamiento incorrecto:
return redirect(url_for("login.login_screen"))
```

**Solución Actualizada:**
```python
# Corrección del endpoint de login:
return redirect(url_for("simple_login_unique.login_simple"))
```

- Ahora todas las redirecciones a login usan el endpoint del blueprint simple_login_unique, que es el sistema de login centralizado y seguro.
- Esto evita errores de endpoint y mantiene la autenticación consistente en todo el panel.

### 2. Estructura de URLs

**URLs que funcionan correctamente:**
```
/panel_cliente/aura/              # Ruta principal del panel
/panel_cliente/aura/clientes      # Módulo de clientes/empresas
/panel_cliente/aura/pagos         # Módulo de pagos
```

```python
# En registro_dinamico.py
safe_register_blueprint(
    app, 
    panel_cliente_pagos_bp,  # nombre del blueprint 
    url_prefix=f"/panel_cliente/{nombre_nora}/pagos"  # prefijo completo incluyendo el módulo
)
```

### 3. Rutas en el Blueprint

```python
# En el archivo del blueprint
@panel_cliente_pagos_bp.route("/", methods=["GET"])  # ruta raíz
def vista_principal():
    nombre_nora = request.path.split("/")[2]  # obtener de la URL
    ...

@panel_cliente_pagos_bp.route("/accion", methods=["GET"])  # subruta
def otra_vista():
    nombre_nora = request.path.split("/")[2]
    ...
```

### 4. Templates

```html
<!-- En los templates usar la ruta completa o url_for con el endpoint correcto -->
<a href="/panel_cliente/{{ nombre_nora }}/pagos">...</a>
<a href="/panel_cliente/{{ nombre_nora }}/pagos/accion">...</a>
<a href="{{ url_for('panel_cliente_tareas.index_tareas', nombre_nora=nombre_nora) }}">...</a>
```

### 5. Registro de Blueprints

```python
# En registro_dinamico.py:
bp = crear_blueprint_panel_cliente(nombre_nora)
safe_register_blueprint(app, bp, url_prefix=f"/panel_cliente/{nombre_nora}")
```

## Mejores Prácticas

1. **Redirecciones:**
   - Usar siempre `simple_login_unique.login_simple` para redirecciones al login.
   - Mantener consistencia en los nombres de los endpoints.

2. **URLs en Templates:**
   - Para rutas simples, usar URLs directas con `nombre_nora`.
   - Para rutas complejas, usar `url_for()` con el endpoint correcto.

3. **Registro de Blueprints:**
   - Mantener la estructura `/panel_cliente/{nombre_nora}/{modulo}`.
   - Usar `safe_register_blueprint` para evitar registros duplicados.

4. **Verificación de Sesión:**
```python
if not session.get("email"):
    return redirect(url_for("simple_login_unique.login_simple"))
```

## Notas Importantes

- No modificar las rutas que ya funcionan.
- Mantener la estructura actual de URLs.
- Verificar siempre el endpoint correcto para redirecciones.
- El nombre_nora se obtiene del prefijo de la URL en el blueprint principal.

```html
<!-- ✅ Correcto -->
<a href="{{ url_for('panel_cliente_modulo_bp.accion', nombre_nora=nombre_nora) }}">

<!-- ❌ Incorrecto - falta nombre_nora -->
<a href="{{ url_for('panel_cliente_modulo_bp.accion') }}">

<!-- ❌ Incorrecto - no usar rutas hardcodeadas -->
<a href="/panel_cliente/{{ nombre_nora }}/modulo/accion">
```

En las rutas del blueprint:
```python
# ✅ Correcto
@blueprint.route("/accion/<nombre_nora>")
def accion(nombre_nora):
    ...

# ❌ Incorrecto - no extraer nombre_nora de request.path
@blueprint.route("/accion")
def accion():
    nombre_nora = request.path.split("/")[2]  # ❌ No hacer esto
    ...
```

En el registro del blueprint:
```python
# ✅ Correcto - Registrar con el prefijo del módulo
safe_register_blueprint(
    app, 
    blueprint,
    url_prefix=f"/panel_cliente/{nombre_nora}/modulo"
)
```

---

## Checklist de Verificación

Antes de implementar nuevas rutas:

1. ✓ Verificar que el blueprint esté registrado correctamente
2. ✓ Confirmar que la ruta incluye todos los segmentos necesarios
3. ✓ Validar que el template use la estructura de URL correcta
4. ✓ Comprobar que se valide la sesión y el módulo activo
5. ✓ Asegurar que el nombre_nora se pase correctamente

## Corrección de URLs Existentes

Para corregir las URLs que no funcionan, se debe:

1. Actualizar los blueprints para incluir {nombre_nora} en sus rutas
2. Modificar los templates para usar la estructura completa
3. Verificar que los redirects usen url_for() con todos los parámetros necesarios

Ejemplo de corrección:

```python
# Antes
@blueprint.route("/contactos")
def lista_contactos():
    ...

# Después
@blueprint.route("/contactos/<nombre_nora>/lista")
def lista_contactos(nombre_nora):
    if not session.get("email"):
        return redirect(url_for("simple_login_unique.login_simple"))
    ...
```
