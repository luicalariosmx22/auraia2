# 🔑 Sistema de Tokens de Páginas de Facebook

## 📋 Resumen

Este sistema permite gestionar tokens de acceso específicos para cada página de Facebook en lugar de usar solo el token principal de la aplicación. Esto mejora la seguridad y permite un control más granular sobre los permisos de cada página.

## 🗃️ Estructura de Base de Datos

### Tabla `facebook_paginas`

La tabla `facebook_paginas` ahora incluye las siguientes columnas para el manejo de tokens:

```sql
-- Columnas relacionadas con tokens
access_token TEXT NULL                    -- Token específico de la página
access_token_valido BOOLEAN DEFAULT TRUE  -- Estado de validez del token
ultima_sincronizacion TIMESTAMP           -- Última sincronización exitosa
permisos_disponibles TEXT[]              -- Lista de permisos de la página
```

## 🔧 Archivos del Sistema

### 1. **webhooks_api.py**
- `obtener_token_pagina(page_id)` - Obtiene token específico de una página
- `actualizar_estado_token_pagina(page_id, es_valido)` - Actualiza estado del token
- `/api/webhooks/pagina/<page_id>/token` - API para obtener info del token
- `/api/webhooks/pagina/<page_id>/validar-token` - Valida token con Facebook

### 2. **webhooks_meta.py**
- `obtener_token_principal()` - Token principal de Meta
- `obtener_token_apropiado(page_id)` - Selecciona el mejor token disponible
- `/api/webhooks/tokens_paginas` - Estado de todos los tokens
- `/api/webhooks/actualizar_tokens_masivo` - Actualización masiva de tokens

### 3. **actualizar_tokens_paginas.py**
Script para poblar tokens de páginas usando el token principal:
```bash
python actualizar_tokens_paginas.py
```

### 4. **verificar_tokens_paginas.py**
Script de diagnóstico del sistema:
```bash
python verificar_tokens_paginas.py
```

### 5. **actualizar_tabla_tokens_paginas.sql**
Script SQL para asegurar que la tabla tenga las columnas necesarias.

## 🚀 Uso del Sistema

### Configuración Inicial

1. **Ejecutar script SQL** para asegurar columnas:
```sql
-- Ejecutar en Supabase
\i actualizar_tabla_tokens_paginas.sql
```

2. **Poblar tokens existentes**:
```bash
export $(grep -v '^#' .env.local | xargs)
python actualizar_tokens_paginas.py
```

3. **Verificar sistema**:
```bash
python verificar_tokens_paginas.py
```

### Uso en Código

#### Obtener Token para una Página
```python
from clientes.aura.routes.panel_cliente_meta_ads.webhooks_api import obtener_token_pagina

# Obtener token específico de página
token = obtener_token_pagina("123456789")
if token:
    # Usar token específico
    pass
else:
    # Página sin token configurado
    pass
```

#### Obtener Token Apropiado (con Fallback)
```python
from clientes.aura.routes.panel_cliente_meta_ads.webhooks_meta import obtener_token_apropiado

# Obtiene token específico o principal como fallback
token, tipo = obtener_token_apropiado("123456789")
if token:
    print(f"Usando token {tipo}: {token[:10]}...")
```

#### Validar Token de Página
```python
# Via API REST
POST /panel_cliente/aura/meta_ads/webhooks/validar_token_pagina/123456789

# Respuesta:
{
  "success": true,
  "message": "Token válido",
  "page_name": "Mi Página",
  "validado_en": "2025-01-01T12:00:00"
}
```

## 📡 APIs Disponibles

### Gestión de Tokens

#### `GET /api/webhooks/tokens_paginas`
Obtiene estado de todos los tokens de páginas.

**Respuesta:**
```json
{
  "success": true,
  "paginas": [
    {
      "page_id": "123456789",
      "nombre_pagina": "Mi Página",
      "activa": true,
      "tiene_token": true,
      "token_valido": true,
      "ultima_sincronizacion": "2025-01-01T12:00:00"
    }
  ],
  "estadisticas": {
    "total_paginas": 10,
    "activas": 8,
    "con_token": 6,
    "tokens_validos": 5,
    "sin_token": 2
  }
}
```

#### `GET /api/webhooks/pagina/<page_id>/token`
Obtiene información del token de una página específica.

**Parámetros:**
- `include_token=true` - Incluye el token actual (solo para uso interno)

#### `POST /api/webhooks/pagina/<page_id>/validar-token`
Valida el token de una página contra la API de Facebook.

#### `POST /api/webhooks/actualizar_tokens_masivo`
Ejecuta actualización masiva de tokens usando el script Python.

### APIs de Páginas Mejoradas

#### `GET /api/webhooks/paginas`
Ahora incluye información sobre el estado de los tokens:

**Respuesta:**
```json
{
  "success": true,
  "paginas": [
    {
      "page_id": "123456789",
      "nombre_pagina": "Mi Página",
      "access_token_valido": true,
      "ultima_sincronizacion": "2025-01-01T12:00:00",
      "tiene_token": true
    }
  ]
}
```

## 🔒 Seguridad

### Almacenamiento Seguro
- Los tokens se almacenan en la base de datos Supabase (encriptada)
- Nunca se exponen tokens completos en logs
- Solo se muestran primeros caracteres para debugging

### Validación Automática
- El sistema marca automáticamente tokens como inválidos cuando fallan
- Se actualiza `access_token_valido = false` en la BD
- Las funciones usan fallback al token principal si el específico es inválido

### Rotación de Tokens
- Los tokens se pueden actualizar masivamente
- Se mantiene historial de última sincronización
- Sistema de verificación periódica disponible

## 🛠️ Mantenimiento

### Comandos Útiles

```bash
# Verificar estado del sistema
python verificar_tokens_paginas.py

# Actualizar todos los tokens
python actualizar_tokens_paginas.py

# Ver estado en consola
python -c "
from clientes.aura.utils.supabase_client import supabase
result = supabase.table('facebook_paginas').select('page_id,nombre_pagina,access_token_valido').execute()
for p in result.data: print(f'{p[\"nombre_pagina\"]}: {\"✅\" if p[\"access_token_valido\"] else \"❌\"}')"
```

### Monitoreo

El sistema incluye logging automático:
- ✅ Token encontrado y válido
- ⚠️ Token marcado como inválido
- ❌ Página sin token
- 🔍 DEBUG: Información de debugging

### Troubleshooting

#### Error: "Página no encontrada"
```bash
# Verificar que la página esté en la BD
python -c "
from clientes.aura.utils.supabase_client import supabase
result = supabase.table('facebook_paginas').select('*').eq('page_id', 'TU_PAGE_ID').execute()
print(result.data)"
```

#### Error: "Token inválido"
```bash
# Forzar actualización de token específico
python -c "
import sys; sys.path.append('.')
from actualizar_tokens_paginas import obtener_token_pagina_desde_meta, obtener_token_principal
token = obtener_token_pagina_desde_meta('TU_PAGE_ID', obtener_token_principal())
print(f'Nuevo token: {token[:10] if token else \"Error\"}...')"
```

## 📈 Beneficios del Sistema

1. **Seguridad Mejorada**: Tokens específicos por página en lugar de token global
2. **Control Granular**: Permisos específicos para cada página
3. **Monitoreo**: Estado de validez de cada token
4. **Fallback Automático**: Usa token principal si el específico falla
5. **Actualización Masiva**: Scripts para gestionar múltiples páginas
6. **APIs Completas**: Gestión vía REST APIs

## 🔄 Integración con Webhooks

El sistema se integra automáticamente con los webhooks de Meta:

1. **Recepción de Webhook**: Identifica `page_id` del evento
2. **Selección de Token**: Usa token específico de la página
3. **Actualización Automática**: Actualiza `ultima_sincronizacion`
4. **Fallback**: Si el token específico falla, usa el principal
5. **Logging**: Registra el tipo de token usado

Esto asegura que cada interacción con la API de Facebook use el token más apropiado y actualizado para cada página específica.
