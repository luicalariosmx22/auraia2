# Resumen del Sistema de Login Simple (AuraAI)

## Blueprint y Prefijo

- El blueprint se declara así:
  ```python
  simple_login_bp = Blueprint("simple_login_unique", __name__, url_prefix='/login')
  ```
- Todas las rutas de login quedan bajo `/login`.

## Rutas y Endpoints del Blueprint `simple_login_unique`

| Método | Ruta completa                | Endpoint Flask                        | Descripción                                      |
|--------|------------------------------|---------------------------------------|--------------------------------------------------|
| GET    | /login/simple                | simple_login_unique.login_simple       | Muestra el formulario de login simple             |
| POST   | /login/simple/auth           | simple_login_unique.auth_simple        | Procesa login por email y contraseña              |
| GET    | /login/google/callback       | simple_login_unique.google_callback    | Callback de autenticación Google                  |
| GET    | /login/logout                | simple_login_unique.logout_simple      | Cierra la sesión del usuario                      |
| GET    | /login/status                | simple_login_unique.login_status       | Devuelve el estado de login en JSON               |
| GET    | /login/admin                 | simple_login_unique.admin_redirect     | Redirige a dashboard admin si es admin            |
| GET    | /login/login_supabase        | simple_login_unique.login_supabase     | Página alternativa de login con Supabase          |

## Decoradores

- `require_login_simple(f)`  
  Protege rutas que requieren sesión iniciada. Redirige a `/login/simple` si no hay sesión.

- `admin_login_required(f)`  
  (En `middlewares/verificar_login.py`) Protege rutas solo para administradores. Redirige a `/login/simple` si no es admin.

## Lógica de Autenticación

- **Email y contraseña:**  
  - Busca el usuario en la tabla `usuarios_clientes` de Supabase.
  - Verifica si la contraseña es hash SHA256 o texto plano.
  - Si es válida, establece la sesión y redirige según el rol:
    - Si es admin: `/admin`
    - Si es cliente: `/panel_cliente/<nombre_nora>/entrenar`

- **Google Login:**  
  - Recibe el email desde el callback (`/login/google/callback`).
  - Verifica el usuario en la base de datos.
  - Si es válido, establece la sesión y redirige igual que arriba.

## Sesión

- Se guarda en `session`:
  - `email`: correo del usuario
  - `name`: nombre
  - `nombre_nora`: nombre de la nora asignada
  - `is_admin`: bool
  - `user`: dict extendido con id, rol, módulos, permisos, etc.

## Mensajes y Errores

- Se usan `flash()` para mostrar mensajes de éxito o error en la plantilla.
- Los errores de autenticación y sesión se registran con `logger`.

## Plantilla login_simple.html

- Formulario de login con campos email y contraseña.
- Botón para login con Google (enlace a `simple_login_unique.google_callback`).
- Mensajes flash estilizados con Tailwind.
- Sección informativa sobre métodos de autenticación.

## Ejemplo de Registro de Blueprint

```python
from clientes.aura.auth.simple_login import simple_login_bp
app.register_blueprint(simple_login_bp)
```

## Notas de Seguridad

- Este sistema es solo para testing/desarrollo. No usar en producción sin:
  - Hash seguro de contraseñas
  - OAuth real para Google
  - Protección CSRF y HTTPS
  - Gestión robusta de sesiones

---

# Anexo: Diagnóstico y Solución de Problemas de Rutas en Login (Flask)

## I. Resumen del Problema

- **Problema:** Error al generar URLs para el inicio de sesión con Google en una aplicación Flask.
- **Error específico:**
  ```
  werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'simple_login_unique.google_login'.
  ```
- **Síntomas:** Al intentar iniciar sesión con Google, la aplicación mostraba un error o redireccionaba a una URL incorrecta.

## II. Diagnóstico

- Se analizó el traceback del error para identificar el origen.
- Se inspeccionó el código de las funciones de vista y los middlewares relacionados con login.
- Se revisó la configuración y prefijos de los blueprints.
- Se utilizó `app.url_map.iter_rules()` para listar las rutas registradas y verificar los endpoints disponibles.
- **Causa raíz:**
  - Referencia incorrecta al endpoint de Google Login en la plantilla `login_simple.html` (`google_login` en vez de `google_callback`).
  - Prefijo de ruta duplicado en la definición de la función `login_simple` dentro del blueprint, lo que generaba URLs como `/login/login/simple`.

## III. Solución

- Se corrigió el nombre del endpoint en la plantilla `login_simple.html`:
  ```html
  <!-- Antes -->
  <a href="{{ url_for('simple_login_unique.google_login') }}">
  <!-- Después -->
  <a href="{{ url_for('simple_login_unique.google_callback') }}">
  ```
- Se corrigió el prefijo de ruta en la función de vista:
  ```python
  # Antes
  @simple_login_bp.route("/login/simple", methods=["GET"])
  # Después
  @simple_login_bp.route("/simple", methods=["GET"])
  ```
- Se verificó la solución accediendo al login con Google y comprobando que la URL generada era la correcta y el flujo funcionaba sin errores.

## IV. Lecciones Aprendidas

- Es fundamental revisar cuidadosamente los tracebacks de los errores para identificar la causa raíz.
- Usar un depurador o prints para inspeccionar el flujo de ejecución ayuda a detectar errores de configuración.
- Verificar la configuración de los blueprints y los prefijos de ruta en Flask es clave para evitar rutas duplicadas o endpoints inexistentes.
- Utilizar `app.url_map.iter_rules()` es muy útil para depurar problemas de rutas y endpoints.
- Implementar un manejo de errores robusto mejora la experiencia de desarrollo y facilita la depuración.

## V. Código Relevante

**Declaración del blueprint:**
```python
simple_login_bp = Blueprint("simple_login_unique", __name__, url_prefix='/login')
```

**Función google_callback:**
```python
@simple_login_bp.route("/google/callback")
def google_callback():
    # ... lógica ...
    return procesar_login(usuario, origen="Google")
```

**Línea corregida en login_simple.html:**
```html
<a href="{{ url_for('simple_login_unique.google_callback') }}">Iniciar con Google</a>
```

**Middleware de admin:**
```python
def admin_login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("email"):
            return redirect(url_for("simple_login_unique.login_simple"))
        return func(*args, **kwargs)
    return wrapper
```

## Middlewares Relacionados

- Los middlewares de autenticación y autorización están en `clientes/aura/middlewares/verificar_login.py`.

### Ejemplo de middleware para admin:

```python
from flask import session, redirect, url_for
from functools import wraps

def admin_login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("email"):
            return redirect(url_for("simple_login_unique.login_simple"))
        return func(*args, **kwargs)
    return wrapper
```

- Puedes usar este decorador en cualquier vista que requiera autenticación de administrador.
- Si el usuario no está autenticado, será redirigido a `/login/simple`.
