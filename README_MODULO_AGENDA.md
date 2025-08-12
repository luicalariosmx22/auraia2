# 📅 Módulo de Agenda - Nora AI

Sistema completo de gestión de eventos y calendario con sincronización Google Calendar, integración con módulos de tareas y empresas.

## 🌟 Características

### ✅ Funcionalidades principales
- **Gestión de eventos**: Crear, editar, eliminar eventos de agenda
- **Vista de calendario**: Interfaz tipo Google Calendar con vistas mes/semana/día
- **Sincronización Google Calendar**: OAuth2 bidireccional con Google Calendar
- **Integración módulos**: Conexión con tareas (deadlines) y empresas (reuniones)
- **Tipos de eventos**: Reunión, cita, llamada, evento, recordatorio
- **Drag & Drop**: Arrastrar eventos para cambiar fechas
- **Responsive**: Funciona en desktop y móvil

### 🔗 Integraciones
1. **Módulo Tareas**: Fechas límite aparecen como eventos en calendario
2. **Módulo Empresas**: Crear reuniones vinculadas a fichas de empresa
3. **Google Calendar**: Sincronización bidireccional con calendario personal
4. **Sistema Nora**: Multiusuario por `nombre_nora`

## 🏗️ Arquitectura

### Backend
```
clientes/aura/routes/panel_cliente_agenda/
├── __init__.py                     # Registro del blueprint
├── panel_cliente_agenda.py         # Blueprint principal con rutas y API
└── google_calendar_service.py      # Servicio OAuth2 Google Calendar
```

### Frontend
```
clientes/aura/templates/panel_cliente_agenda/
└── index.html                      # Interfaz FullCalendar.js
```

### Base de datos
- `agenda_eventos`: Eventos principales
- `google_calendar_sync`: Credenciales OAuth2 por Nora
- `tareas`: Integración con módulo tareas (existente)
- `cliente_empresas`: Integración con módulo empresas (existente)

## 🚀 Instalación

### 1. Instalar dependencias
```bash
pip install -r requirements_agenda.txt
```

### 2. Configurar base de datos
```bash
python setup_modulo_agenda.py
```

### 3. Configurar Google Calendar (opcional)
```bash
# Copiar y configurar variables
cp config_google_calendar.env.example .env.local
```

Editar `.env.local` con tus credenciales de Google Cloud Console:
```bash
GOOGLE_CLIENT_ID=tu_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu_client_secret
BASE_URL=http://localhost:5000
```

### 4. Registrar módulo
Agregar en `clientes/aura/registro/registro_dinamico.py`:
```python
# Módulo de Agenda
if "agenda" in modulos:
    try:
        from clientes.aura.routes.panel_cliente_agenda import panel_cliente_agenda_bp
        safe_register_blueprint(app, panel_cliente_agenda_bp)
        print(f"✅ Módulo de agenda registrado para {nombre_nora}")
    except Exception as e:
        print(f"❌ Error registrando módulo agenda: {e}")
```

### 5. Reiniciar servidor
```bash
python dev_start.py
```

## 🌐 Uso

### Acceso
```
http://localhost:5000/panel_cliente/aura/agenda/
```

### API Endpoints
- `GET /api/eventos` - Listar eventos
- `POST /api/eventos` - Crear evento
- `PUT /api/eventos/<id>` - Actualizar evento
- `DELETE /api/eventos/<id>` - Eliminar evento
- `GET /google/auth` - Iniciar OAuth Google
- `GET /google/callback` - Callback OAuth

## 📊 Estructura de datos

### Tabla `agenda_eventos`
```sql
CREATE TABLE agenda_eventos (
    id BIGSERIAL PRIMARY KEY,
    nombre_nora VARCHAR(50) NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    fecha_inicio TIMESTAMPTZ NOT NULL,
    fecha_fin TIMESTAMPTZ,
    ubicacion VARCHAR(300),
    tipo VARCHAR(50) DEFAULT 'reunion',
    empresa_id BIGINT REFERENCES cliente_empresas(id),
    tarea_id BIGINT REFERENCES tareas(id),
    google_event_id VARCHAR(100),
    todo_el_dia BOOLEAN DEFAULT FALSE,
    recordatorio_minutos INTEGER DEFAULT 15,
    estado VARCHAR(20) DEFAULT 'confirmado',
    color VARCHAR(7) DEFAULT '#3b82f6',
    creado_por VARCHAR(100),
    creada_en TIMESTAMPTZ DEFAULT NOW(),
    actualizada_en TIMESTAMPTZ DEFAULT NOW()
);
```

### Tabla `google_calendar_sync`
```sql
CREATE TABLE google_calendar_sync (
    id BIGSERIAL PRIMARY KEY,
    nombre_nora VARCHAR(50) NOT NULL UNIQUE,
    google_client_id VARCHAR(200),
    google_client_secret VARCHAR(200),
    google_access_token TEXT,
    google_refresh_token TEXT,
    google_calendar_id VARCHAR(200),
    token_expires_at TIMESTAMPTZ,
    sync_activo BOOLEAN DEFAULT FALSE,
    ultima_sincronizacion TIMESTAMPTZ,
    configurado_en TIMESTAMPTZ DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NOW()
);
```

## 🔧 Configuración Google Calendar

### 1. Google Cloud Console
1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear proyecto o seleccionar existente
3. Habilitar Google Calendar API
4. Crear credenciales OAuth2:
   - Tipo: Web application
   - Authorized redirect URIs: `http://localhost:5000/panel_cliente/aura/agenda/oauth/callback`

### 2. Variables de entorno
```bash
# .env.local
GOOGLE_CLIENT_ID=tu_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu_client_secret
BASE_URL=http://localhost:5000
```

### 3. Proceso OAuth
1. Usuario hace clic en "Conectar Google Calendar"
2. Redirección a Google para autorización
3. Google redirige con código de autorización
4. Sistema intercambia código por tokens
5. Tokens se guardan en `google_calendar_sync`
6. Sincronización automática activada

## 🎨 Frontend

### FullCalendar.js
- **Librería**: FullCalendar v5.11.3
- **Vistas**: Mes, semana, día
- **Funciones**: Drag & drop, eventos click, responsive
- **Estilos**: Replica visual de Google Calendar

### Tipos de eventos
- 🤝 **Reunión**: Color azul (#3b82f6)
- 📞 **Llamada**: Color verde (#10b981)  
- 🗓️ **Cita**: Color amarillo (#f59e0b)
- 🎉 **Evento**: Color morado (#8b5cf6)
- ⏰ **Recordatorio**: Color rojo (#ef4444)

### Modal de evento
- Formulario completo de creación/edición
- Selección de empresa y tarea relacionada
- Configuración de recordatorios
- Validación de fechas
- Confirmación de eliminación

## 🔧 Testing

### Ejecutar tests
```bash
python test_modulo_agenda.py
```

### Verificaciones automáticas
- ✅ Imports de código
- ✅ Existencia de tablas BD
- ✅ Registro de módulo
- ✅ Activación para Nora
- ✅ Eventos de ejemplo
- ✅ Lógica de negocio
- ✅ Variables de entorno
- ✅ Archivos de template

## 📁 Archivos del proyecto

### Archivos principales
- `panel_cliente_agenda.py` - Blueprint principal (350+ líneas)
- `google_calendar_service.py` - Servicio Google Calendar (200+ líneas)
- `index.html` - Interfaz frontend (600+ líneas)
- `requirements_agenda.txt` - Dependencias Python

### Archivos de configuración
- `setup_modulo_agenda.py` - Script de configuración completa
- `config_google_calendar.env.example` - Variables de entorno
- `instrucciones_registro_agenda.py` - Guía de integración
- `test_modulo_agenda.py` - Suite de testing

## 🚂 Deploy Railway

### Variables de entorno Railway
```bash
# Básicas (ya configuradas)
SUPABASE_URL=https://sylqljdiiyhtgtrghwjk.supabase.co
SUPABASE_KEY=eyJhbGci...
SECRET_KEY=1002ivimyH!

# Google Calendar (nuevas)
GOOGLE_CLIENT_ID=tu_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu_client_secret
BASE_URL=https://app.soynoraai.com
```

### Configurar redirect URI
En Google Cloud Console, agregar:
```
https://app.soynoraai.com/panel_cliente/aura/agenda/oauth/callback
```

## 📈 Métricas y analytics

### Eventos trackeable
- Creación de eventos
- Sincronización Google Calendar
- Interacciones con empresas/tareas
- Tiempo en vista de calendario

### Logs automáticos
- OAuth flow Google Calendar
- Errores de sincronización
- Operaciones CRUD de eventos
- Performance de carga de calendario

## 🔒 Seguridad

### OAuth2 Google
- State parameter para CSRF protection
- Tokens encriptados en BD
- Refresh automático de tokens
- Scopes mínimos necesarios

### Validaciones
- Fechas de eventos válidas
- Permisos por `nombre_nora`
- Sanitización de inputs
- Rate limiting en API

## 🐛 Troubleshooting

### Errores comunes

#### Google Calendar no conecta
```bash
# Verificar variables
echo $GOOGLE_CLIENT_ID
echo $GOOGLE_CLIENT_SECRET

# Verificar redirect URI en Google Cloud Console
# Debe coincidir exactamente con BASE_URL + /oauth/callback
```

#### Módulo no aparece
```bash
# Verificar registro
python -c "from clientes.aura.utils.supabase_client import supabase; print(supabase.table('modulos_disponibles').select('*').eq('nombre', 'agenda').execute().data)"

# Verificar activación
python -c "from clientes.aura.utils.supabase_client import supabase; print(supabase.table('configuracion_bot').select('modulos').eq('nombre_nora', 'aura').execute().data)"
```

#### Eventos no cargan
```bash
# Verificar tabla
python -c "from clientes.aura.utils.supabase_client import supabase; print(supabase.table('agenda_eventos').select('*').limit(5).execute().data)"
```

### Logs útiles
```python
# En panel_cliente_agenda.py, línea ~200
print(f"DEBUG: Cargando eventos para {nombre_nora}")

# En google_calendar_service.py, línea ~150  
print(f"DEBUG: Token Google expires: {expires_at}")
```

## 🤝 Contribuir

### Estructura de commits
```bash
git commit -m "feat(agenda): nueva funcionalidad X"
git commit -m "fix(agenda): corregir error Y"
git commit -m "docs(agenda): actualizar documentación"
```

### Testing requerido
```bash
# Antes de commit
python test_modulo_agenda.py
python setup_modulo_agenda.py  # Verificar no rompe BD
```

## 📄 Licencia

Parte del sistema Nora AI. Uso interno del proyecto.

---

## 🎯 Roadmap

### v1.1 (Próximas mejoras)
- [ ] Notificaciones push de eventos
- [ ] Integración con Outlook Calendar
- [ ] Eventos recurrentes avanzados
- [ ] Timeline de empresa con eventos históricos
- [ ] Export a PDF de agenda semanal

### v1.2 (Futuro)
- [ ] Integración con videollamadas (Meet/Zoom)
- [ ] IA para sugerir horarios óptimos
- [ ] Sincronización con CRM externo
- [ ] App móvil nativa
- [ ] Multi-timezone support

---

**📅 Módulo de Agenda v1.0** - Desarrollado para Nora AI  
*Última actualización: Enero 2024*
