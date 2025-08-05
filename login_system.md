# Guía técnica: Sistema de Login Simple en Flask (AuraAI)

---

## 1. 📂 Estructura de archivos relevantes

El sistema de login simple está compuesto por los siguientes archivos principales:

- `clientes/aura/auth/simple_login.py`  
  Blueprint con todas las rutas y lógica de autenticación simple.

- `clientes/aura/registro/registro_login.py`  
  Función para registrar el blueprint de login en la app Flask.

- `clientes/aura/__init__.py`  
  Inicialización de la app Flask, registro de blueprints y configuración global.

- `clientes/aura/templates/login_simple.html`  
  Template HTML para la pantalla de login simple.

- `clientes/aura/config/session_fix.py`  
  (Opcional) Configuración avanzada de sesiones si se requiere manejo especial.

---

## 2. 🔁 Registro del Blueprint

- El blueprint de login se define en `simple_login.py` como:

  ```python
  simple_login_bp = Blueprint("simple_login_unique", __name__, url_prefix='/auth')
  ```

- El registro del blueprint se realiza en `registro_login.py` mediante la función:

  ```python
  def registrar_blueprints_login(app, safe_register_blueprint):
      from ..auth.simple_login import simple_login_bp
      if 'simple_login_unique' not in app.blueprints:
          safe_register_blueprint(
              app,
              simple_login_bp,
              name='simple_login_unique'
          )
  ```

- En `__init__.py` se importa y ejecuta el registro:

  ```python
  from .registro.registro_login import registrar_blueprints_login
  registrar_blueprints_login(app, safe_register_blueprint)
  ```

---

## 3. 🌐 Rutas disponibles

- **`/auth/simple`**  
  - Métodos: GET (muestra formulario), POST (procesa login)
  - Función: `login_simple` y `auth_simple` en `simple_login.py`

- **`/auth/google`**  
  - Función: `google_login` en `simple_login.py`  
  - (Puede ser solo un redirect o placeholder si no está implementado OAuth)

- **`/logout`**  
  - Función: `logout` en `simple_login.py`  
  - Limpia la sesión y redirige al login

---

## 4. 🛠️ Errores comunes y soluciones

- **Error 404 por `login_blueprint.auth_simple`**  
  - Solución: Cambia todos los `url_for('login_blueprint.auth_simple')` a `url_for('simple_login_unique.auth_simple')` en templates y código.

- **Problema con `url_for`**  
  - Siempre usa el nombre correcto del blueprint: `simple_login_unique`.

- **La sesión no se guarda correctamente**  
  - Verifica que `flask_session` esté correctamente configurado en `__init__.py` o mediante `session_fix.py`.
  - Asegúrate de llamar a `Session(app)` después de configurar la app.

---

## 5. 🔐 Explicación de sesiones

- **Configuración básica:**  
  En `__init__.py` (o `session_fix.py`), la sesión se configura así:

  ```python
  app.config['SESSION_TYPE'] = 'filesystem'
  app.config['SESSION_PERMANENT'] = True
  app.config['SESSION_USE_SIGNER'] = True
  # ...otros parámetros...
  Session(app)
  ```

- **CustomSessionInterface:**  
  Si se usa, permite manejar casos donde el ID de sesión es bytes y no string.  
  Solo es necesario si tienes errores de serialización de sesión.

---

## 6. 🧪 Testing sugerido

- **Prueba local:**  
  - Ejecuta la app (`flask run` o `python main.py`).
  - Accede a `http://localhost:5000/auth/simple`
  - Debes ver el formulario de login.

- **Prueba funcional:**  
  - Ingresa un email y contraseña válidos (según tu lógica).
  - Si el login es exitoso, debe redirigir al panel o dashboard.
  - Si falla, debe mostrar un mensaje de error.

- **Visual:**  
  - El template debe verse moderno, con mensajes flash y botones claros.
  - El botón "Iniciar con Google" debe estar presente (aunque puede ser solo decorativo si no hay OAuth).

---

## Notas finales

- Mantén el nombre del blueprint (`simple_login_unique`) consistente en todo el código y templates.
- Si cambias el url_prefix o el nombre del blueprint, actualiza todos los `url_for` correspondientes.
- Para cambios en la lógica de login, modifica solo `simple_login.py` y el template.
- Si tienes problemas de sesión, revisa la configuración en `session_fix.py` y asegúrate de que el directorio de sesiones exista y sea escribible.

---
