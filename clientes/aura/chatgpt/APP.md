# 📘 Instrucciones para `app.py` en AuraAI2

Este archivo es el **punto de entrada principal** de la aplicación Flask.  
Contiene la configuración general del proyecto, define cómo se comporta el servidor, y controla **la carga de todos los blueprints** mediante funciones modulares.

---

## 🧠 Propósito de `app.py`

- Configurar la app de Flask y sus extensiones (socketio, sesiones, logs, scheduler, dotenv)
- Registrar todos los blueprints desde los archivos `registro_*.py`
- Cargar rutas dinámicas por Nora
- Manejar rutas globales como `/`, `/logout`, `/debug_info`
- Programar tareas automáticas (ej. reportes semanales)
- Iniciar el servidor con `socketio.run()`

---

## ✅ ¿Qué DEBE contener?

- Configuración de Flask (`SECRET_KEY`, `SESSION_TYPE`, etc.)
- Carga de variables de entorno con `dotenv`
- Configuración de `socketio`, `logging`, `scheduler`
- Importación de funciones de registro:
  ```python
  registrar_blueprints_login()
  registrar_blueprints_base()
  registrar_blueprints_admin()
  registrar_blueprints_invitado()
  registrar_blueprints_por_nora()


❌ ¿Qué NO debe contener?
❌ Registro manual de blueprints individuales como app.register_blueprint(x)
(excepto casos especiales justificados como /api/cobranza)

❌ Lógica de negocio

❌ Código duplicado de rutas que ya están en registro_*.py

❌ Rutas con lógica propia de clientes o admin (eso va en sus módulos)

🧪 Funciones clave
safe_register_blueprint(app, blueprint, url_prefix="..."):
Asegura que un blueprint no se registre dos veces.

registrar_rutas_en_supabase():
Guarda las rutas activas en la base de datos Supabase para trazabilidad.

generar_html_rutas():
Genera un archivo visual (debug_rutas.html) para ver las rutas desde el panel

⚠️ Advertencia de buenas prácticas
Si necesitas agregar una nueva ruta o módulo:

✅ Paso correcto:

Crear un archivo nuevo en registro/

Registrar ahí los blueprints

Importarlo en app.py y llamarlo con safe_register_blueprint

❌ Paso incorrecto:

Agregar app.register_blueprint(...) directamente en app.py

Registrar rutas duplicadas que ya están en otros registro_*.py

⚙️ Este archivo es el orquestador principal del sistema, debe ser limpio, modular y mantenerse lo más estable posible.