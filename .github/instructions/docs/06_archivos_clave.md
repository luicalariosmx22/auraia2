# 🛠️ Archivos clave por carpeta

## 📁 `clientes/aura/routes/`

### Archivos clave:
- **`clientes/aura/registro/registro_dinamico.py`** → ⚠️ Sistema de módulos dinámicos
- **`panel_cliente.py`** → Panel cliente principal
- **`panel_cliente_<modulo>/`** → Carpetas de módulos (meta_ads, tareas, contactos, etc.)
- **`webhook.py`** → Sistema principal de webhooks
- **`process_message.py`** → Procesamiento de mensajes WhatsApp
- **`admin_dashboard.py`** → Dashboard administrativo principal

---

## 📁 `clientes/aura/utils/`

### Archivos utilitarios críticos:

#### `supabase_client.py` 🔥
```python
# Cliente global de Supabase - USAR SIEMPRE ESTE
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)
```

#### Otros archivos importantes:
- **`config.py`** → Configuración centralizada
- **`auth_utils.py`** → Utilidades de autenticación
- **`validators.py`** → Validadores de datos
- **`supabase_helpers.py`** → Funciones auxiliares para Supabase
- **`webhook_utils.py`** → Utilidades para webhooks
- **`logging_utils.py`** → Sistema de logging

---

## 📁 `clientes/aura/scripts/`

### Scripts de mantenimiento importantes:
- **`sincronizador_semanal.py`** → Sincroniza datos externos
- **`diagnostico_modulo.py`** → Diagnóstica problemas en módulos
- **`actualizar_tokens.py`** → Renueva tokens de APIs
- **`backup_diario.py`** → Respaldos automáticos

---

## 📁 `templates/`

### Estructura de templates principales:
```bash
clientes/aura/templates/
├── base_cliente.html            # 🔥 Template base principal
├── panel_cliente_aura/
│   └── index.html              # Dashboard principal
├── panel_cliente_<modulo>/     # Templates por módulo
│   └── index.html              # Template principal del módulo
├── shared/
│   ├── navbar.html             # Navegación compartida
│   ├── footer.html             # Footer compartido
│   └── modals.html             # Modales reutilizables
└── admin/
    ├── dashboard.html          # Dashboard admin
    ├── noras.html              # Gestión Noras
    └── modulos.html            # Gestión módulos
```

---

## 📁 `static/`

### Archivos estáticos organizados:

#### `clientes/aura/static/css/` - Estilos principales
```bash
clientes/aura/static/css/
├── panel_cliente.css           # 🔥 Estilos principales
├── base.css                    # Estilos base
├── admin.css                   # Estilos admin
├── login.css                   # Estilos login
├── dashboard.css               # Dashboard general
├── modulos/
│   ├── <modulo>/
│   │   ├── main.css           # Estilos específicos
│   │   └── dashboard.css      # Dashboard del módulo
└── shared/
    ├── animations.css         # Animaciones reutilizables
    ├── utilities.css          # Clases utilitarias
    └── components.css         # Componentes
```

#### `clientes/aura/static/js/` - JavaScript modular
```bash
clientes/aura/static/js/
├── panel_cliente.js            # 🔥 JavaScript principal
├── shared/
│   ├── utils.js               # Utilidades compartidas
│   ├── api.js                 # Funciones de API
│   └── notifications.js       # Sistema de notificaciones
├── modulos/
│   ├── <modulo>/
│   │   ├── main.js           # JavaScript principal del módulo
│   │   └── dashboard.js      # Dashboard interactivo
└── admin/
    ├── dashboard.js          # Dashboard admin
    └── modulos.js            # Gestión módulos
```

#### `clientes/aura/static/images/`
```bash
clientes/aura/static/images/
├── logo_nora.png              # 🔥 Logo principal
├── favicon.ico                # Favicon
├── backgrounds/               # Fondos
├── icons/                     # Iconos
└── avatars/                   # Avatares
```

---

## 📁 Archivos de configuración raíz

### En la raíz del proyecto:

#### `.env.local` 🔥
```bash
# Variables de entorno para desarrollo local
SUPABASE_URL=https://sylqljdiiyhtgtrghwjk.supabase.co
SUPABASE_KEY=eyJ...
META_ACCESS_TOKEN=EAA...
```

#### `clientes/aura/__init__.py` (inicialización de la app)
```python
# Función factory principal que crea y configura toda la aplicación Flask
def create_app(config_class=Config):
    """Función factory para crear y configurar la aplicación Flask"""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config_class)
    
    # Inicializar todos los componentes
    initialize_app(app)
    
    return app, socketio

def initialize_app(app):
    """Inicializa blueprints, tareas y componentes adicionales"""
    # Registrar blueprints base
    from .registro.registro_login import registrar_blueprints_login
    from .registro.registro_admin import registrar_blueprints_admin
    from .registro.registro_dinamico import registrar_blueprints_por_nora
    
    # Blueprints dinámicos por cada Nora
    response = supabase.table("configuracion_bot").select("nombre_nora").execute()
    nombre_noras = [n["nombre_nora"] for n in response.data]
    for nombre in nombre_noras:
        registrar_blueprints_por_nora(app, nombre_nora=nombre)
```

#### `run.py` (punto de entrada principal)
```python
# Punto de entrada principal para producción y desarrollo
import os
from clientes.aura import create_app
import sys
import time
from flask import send_file

# Create the Flask application
app, socketio = create_app()

# This makes the app available for Gunicorn and other WSGI servers
application = app  # For WSGI servers that expect 'application' variable

if __name__ == '__main__':
    # For local development with Flask's built-in server
    print("🚀 Starting NORA application in development mode...")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
```

#### `dev_start.py` (desarrollo con parches)
```python
# Archivo para desarrollo local con parches de compatibilidad
from dotenv import load_dotenv
import os
import logging

# Aplicar parches antes de importar otras bibliotecas
from patches.werkzeug_patches import apply_patches
apply_patches()

# Cargar variables de entorno
modo = os.getenv("ENTORNO", "local")
if modo == "railway":
    load_dotenv(".env.railway")
else:
    load_dotenv(".env.local")

# Lanzar app Flask con configuración específica para desarrollo
from gunicorn_patch import app, socketio
```

#### `app_config.py` (configuración centralizada)
```python
# Configuración centralizada de la aplicación
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-fuerte")
    SESSION_TYPE = "filesystem"
    SESSION_COOKIE_NAME = os.environ.get("SESSION_COOKIE_NAME", "aura_multinora_cookie")
    
    # Configuración para auto-reload de templates
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0
    
    # Modo debug según entorno
    if os.environ.get("ENTORNO", "local") == "local":
        DEBUG = True
    else:
        DEBUG = False
```

#### `extensiones.py` (extensiones Flask)
```python
# Extensiones centralizadas para Flask
from flask_socketio import SocketIO
from flask_session import Session
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

socketio = SocketIO()
session_ext = Session()
scheduler = BackgroundScheduler(timezone=pytz.timezone('America/Hermosillo'))
```

#### `scheduler_jobs.py` (tareas programadas)
```python
# Registro centralizado de tareas programadas para APScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

def inicializar_cron_jobs(scheduler):
    """Inicializa los trabajos programados con APScheduler"""
    # Tareas diarias, reportes automáticos, sincronizaciones
    pass
```

#### `requirements.txt`
```txt
flask
supabase
requests
python-dotenv
gunicorn
google-ads
facebook-business
twilio
openai
```

#### `Dockerfile`
```dockerfile
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "run:app"]
```

#### `gunicorn_config.py`
```python
# Configuración de Gunicorn para producción
import os

bind = f"0.0.0.0:{os.environ.get('PORT', 8080)}"
workers = int(os.environ.get('WEB_CONCURRENCY', 4))
timeout = 120
keepalive = 2
worker_class = "sync"
```

---

## 🔍 Archivos que NO debes modificar sin cuidado:

### 🚨 CRÍTICOS - Modificar con extrema precaución:
- **`clientes/aura/registro/registro_dinamico.py`** → Sistema de módulos
- **`supabase_client.py`** → Conexión a BD
- **`base_cliente.html`** → Template base

### ⚠️ IMPORTANTES - Revisar antes de modificar:
- **`panel_cliente.css`** → Estilos principales
- **`panel_cliente.js`** → JavaScript principal
- **`auth_utils.py`** → Sistema de autenticación

### ✅ SEGUROS - Puedes modificar libremente:
- Templates específicos de módulos
- CSS/JS específicos de módulos
- Scripts de mantenimiento
- Archivos de configuración por módulo

---

## 🎯 Checklist al crear nuevos archivos:

1. **¿Dónde va?** → Revisar estructura estándar
2. **¿Imports correctos?** → Usar rutas relativas
3. **¿Nombre consistente?** → Seguir convenciones
4. **¿Documentado?** → Comentarios en código crítico
5. **¿Testeable?** → Funciones puras cuando sea posible
