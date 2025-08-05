# WhatsApp Web QR - Implementación WebSocket

## Descripción

Este módulo implementa una conexión WebSocket real para WhatsApp Web, permitiendo la generación de códigos QR y el manejo de conexiones en tiempo real.

## Arquitectura

### Componentes principales:

1. **Frontend WebSocket** (`index_websocket.html`):
   - Interfaz de usuario con conexión WebSocket
   - Manejo de estados de conexión en tiempo real
   - Generación y visualización de códigos QR
   - Registro de actividad en tiempo real

2. **Servidor WebSocket** (`websocket_server.py`):
   - Servidor Flask-SocketIO independiente
   - Manejo de sesiones de WhatsApp Web
   - Generación de códigos QR
   - Simulación de autenticación (para demostración)

3. **Backend del módulo** (`__init__.py`):
   - Integración con el sistema principal
   - Endpoints HTTP para funcionalidades adicionales
   - Verificación de sesiones y autenticación

## Configuración

### Puertos:
- **Aplicación principal**: Puerto 5000
- **Servidor WebSocket**: Puerto 5001

### Variables de entorno:
- `WS_PORT`: Puerto del servidor WebSocket (default: 5001)
- `WS_HOST`: Host del servidor WebSocket (default: 0.0.0.0)
- `DEBUG`: Modo debug (default: false)
- `SECRET_KEY`: Clave secreta para WebSocket

## Ejecución

### Iniciar servidor WebSocket:

**Linux/macOS:**
```bash
chmod +x start_websocket.sh
./start_websocket.sh
```

**Windows:**
```cmd
start_websocket.bat
```

**Manual:**
```bash
python websocket_server.py
```

### Verificar funcionamiento:

1. Acceder a `http://localhost:5001/health` para verificar el estado del servidor
2. Acceder a `http://localhost:5001/stats` para ver estadísticas

## Eventos WebSocket

### Eventos del cliente:
- `connect`: Conexión establecida
- `get_qr`: Solicitar código QR
- `get_status`: Obtener estado de sesión
- `disconnect_whatsapp`: Desconectar WhatsApp Web

### Eventos del servidor:
- `connected`: Confirmación de conexión
- `qr_code`: Código QR generado
- `authenticated`: Autenticación exitosa
- `disconnected`: Desconexión de WhatsApp Web
- `status`: Estado de la sesión
- `error`: Error en la operación

## Estructura de mensajes

### Solicitar QR:
```json
{
  "type": "get_qr",
  "session_id": "optional-session-id"
}
```

### Respuesta QR:
```json
{
  "type": "qr_code",
  "session_id": "unique-session-id",
  "qr_data": "whatsapp-qr-data",
  "message": "Código QR generado"
}
```

### Estado de sesión:
```json
{
  "type": "status",
  "session_id": "unique-session-id",
  "status": "pending|qr_ready|authenticated|disconnected",
  "authenticated": true|false,
  "message": "Estado actual"
}
```

## Características

### Implementadas:
- ✅ Conexión WebSocket en tiempo real
- ✅ Generación de códigos QR
- ✅ Manejo de sesiones
- ✅ Reconexión automática
- ✅ Limpieza de sesiones inactivas
- ✅ Estados de conexión visuales
- ✅ Registro de actividad
- ✅ Simulación de autenticación

### Para implementar (conexión real):
- 🔄 Integración con whatsapp-web.js
- 🔄 Integración con Baileys
- 🔄 Integración con go-whatsapp
- 🔄 Manejo de mensajes WhatsApp
- 🔄 Persistencia de sesiones
- 🔄 Manejo de múltiples dispositivos

## Nota importante

Esta implementación incluye una simulación de autenticación para demostrar el funcionamiento del WebSocket. Para una conexión real con WhatsApp Web, se necesita integrar con bibliotecas especializadas como:

- **whatsapp-web.js** (Node.js)
- **Baileys** (Node.js)
- **go-whatsapp** (Go)
- **yowsup** (Python)

## Seguridad

- Todas las conexiones WebSocket requieren autenticación
- Las sesiones se limpian automáticamente después de inactividad
- Los códigos QR tienen timestamp para evitar reutilización
- El servidor valida todos los mensajes entrantes

## Monitoreo

El servidor incluye endpoints para monitoreo:
- `/health`: Estado del servidor
- `/stats`: Estadísticas de sesiones activas

## Logs

El servidor genera logs detallados para:
- Conexiones y desconexiones
- Creación y eliminación de sesiones
- Errores y excepciones
- Actividad de limpieza

## Escalabilidad

Para entornos de producción:
- Usar Redis para almacenar sesiones
- Implementar load balancer para WebSocket
- Configurar clustering para múltiples instancias
- Implementar monitoreo con Prometheus/Grafana
