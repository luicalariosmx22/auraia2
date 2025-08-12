# 🧪 Testing y Desarrollo

## ✅ Reglas para scripts de prueba

**NUNCA** crear scripts de test permanentes en el directorio raíz.

### Testing eficiente:

1. **SIEMPRE revisar `tests/` antes de crear un nuevo test**
   - Buscar archivos similares: `test_webhook_*`, `test_meta_*`, etc.
   - Reutilizar lógica existente cuando sea posible

2. **No cargar toda la app para tests simples**:
   ```python
   # ❌ No cargar toda la app para tests simples
   from app import create_app  # Carga 90+ blueprints
   
   # ✅ Importar solo lo necesario
   from clientes.aura.utils.supabase_client import supabase
   from clientes.aura.utils.meta_webhook_helpers import verificar_webhook
   ```

3. **Testing ULTRA eficiente** 🚀:
   ```python
   # 🔥 MÉTODO SUPREMO: Supabase directo sin imports de la app
   from supabase.client import create_client, Client
   
   def test_ultra_eficiente():
       # Conexión directa - SIN cargar Flask
       url = "https://sylqljdiiyhtgtrghwjk.supabase.co"
       key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN5bHFsamRpaXlodGd0cmdod2prIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDcwMzUzMiwiZXhwIjoyMDYwMjc5NTMyfQ.Y-LTUYS0qg8bKEX1c6MLdxudNUsJuZdQfV2Z0dx9n1Q"
       supabase = create_client(url, key)
       
       # Test directo contra BD
       result = supabase.table('tabla').update({'campo': 'valor'}).eq('id', '123').execute()
       
       # ⚡ Resultado: INSTANTÁNEO vs 30+ segundos cargando blueprints
   ```

4. **Verificación de schemas ultra rápida** 🔥:
   ```powershell
   # 💡 MÉTODO REAL: Verificar tipos de BD sin cargar Flask (< 3 segundos)
   python -c "
   from supabase.client import create_client
   url = 'https://sylqljdiiyhtgtrghwjk.supabase.co'
   key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN5bHFsamRpaXlodGd0cmdod2prIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDcwMzUzMiwiZXhwIjoyMDYwMjc5NTMyfQ.Y-LTUYS0qg8bKEX1c6MLdxudNUsJuZdQfV2Z0dx9n1Q'
   supabase = create_client(url, key)
   
   # Verificar tipos de campos específicos
   result = supabase.table('tareas').select('id').limit(1).execute()
   if result.data:
       id_val = result.data[0]['id']
       print(f'tareas.id ejemplo: {id_val} (tipo: {type(id_val).__name__})')
   
   # Verificar múltiples tablas
   for tabla in ['cliente_empresas', 'modulos_disponibles', 'configuracion_bot']:
       try:
           r = supabase.table(tabla).select('id').limit(1).execute()
           if r.data:
               print(f'{tabla}.id: {type(r.data[0]['id']).__name__}')
       except:
           print(f'{tabla}: no accesible')
   "
   
   # 🚀 Resultado: Verificación en < 3 segundos vs 30+ segundos con Flask
   ```

## 🚀 Comparación de velocidad:

* **🐌 Test normal**: 30+ segundos (carga 90+ blueprints)
* **⚡ Test eficiente**: 3-5 segundos (solo utils necesarios)  
* **🚀 Test ULTRA**: < 1 segundo (Supabase directo)
* **🔥 Verificación schemas**: < 3 segundos (método real comprobado)

## 📁 Ubicación de tests:

* **`tests/`** → Todos los archivos de testing (67+ archivos)
* **Nombres descriptivos**: `test_webhook_meta.py`, `test_sistema_meta_completo.py`, `test_ultra_eficiente_782681001814242.py`
* **Template disponible**: `template_ultra_eficiente.py` - Usar como base para nuevos tests
* **Revisar existentes**: Buscar `test_*tema*` antes de crear nuevos
* **Limpiar temporales**: Borrar tests específicos después de usar

### Tests existentes más útiles:
- `test_variables_env.py` - Verificar variables de entorno
- `test_webhook_meta.py` - Testing de webhooks Meta
- `test_sistema_meta_completo.py` - Tests completos Meta Ads
- `template_ultra_eficiente.py` - Template para copiar y modificar

## 🔧 Evitar reinicios del servidor:

```powershell
# ❌ Servidor se reinicia con cada test (PowerShell)
Get-Content .env.local | ForEach-Object { 
    if ($_ -notmatch '^#' -and $_ -match '=') { 
        $parts = $_ -split '=', 2
        [System.Environment]::SetEnvironmentVariable($parts[0], $parts[1], 'Process') 
    } 
}; python dev_start.py

# ✅ Servidor NO se reinicia al modificar tests/ (PowerShell)
$env:DISABLE_AUTO_RELOAD = "true"
Get-Content .env.local | ForEach-Object { 
    if ($_ -notmatch '^#' -and $_ -match '=') { 
        $parts = $_ -split '=', 2
        [System.Environment]::SetEnvironmentVariable($parts[0], $parts[1], 'Process') 
    } 
}; python dev_start.py

# 🚀 Script automático disponible:
.\dev_no_reload.ps1
```

## 💻 PowerShell Extension (Windows):

```powershell
# 🔧 Usamos PowerShell Extension en VS Code para Windows

# ✅ Cargar variables de entorno (PowerShell):
Get-Content .env.local | ForEach-Object { 
    if ($_ -notmatch '^#' -and $_ -match '=') { 
        $parts = $_ -split '=', 2
        [System.Environment]::SetEnvironmentVariable($parts[0], $parts[1], 'Process') 
    } 
}

# 🚀 Script automático sin auto-reload:
.\dev_no_reload.ps1

# 💡 Ventajas PowerShell Extension:
# - Sintaxis highlighting para .ps1
# - IntelliSense para comandos PowerShell  
# - Debugging integrado
# - Ejecución directa desde VS Code

# 📋 Scripts disponibles:
# - dev_no_reload.ps1: Sin auto-reload completo
# - dev_smart_reload.ps1: Auto-reload inteligente  
# - dev_reload_no_tests.ps1: Excluye tests/ del reload
```

## 🎯 Funciones puras para testing:

```python
def calcular_estado_webhook(estado_db: str, tiene_actividad: bool) -> str:
    """Función pura sin dependencias de Flask"""
    return 'activa' if estado_db == 'activa' or tiene_actividad else 'inactiva'

# Test directo sin Flask
assert calcular_estado_webhook('activa', False) == 'activa'
```

## 🎭 Usar mocks para evitar dependencias:

```python
from unittest.mock import patch, MagicMock

@patch('clientes.aura.utils.supabase_client.supabase')
def test_funcion(mock_supabase):
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = []
    # Test rápido sin BD real
```

## 🧪 Template ultra eficiente disponible:

```python
# Usar como base: tests/template_ultra_eficiente.py
# 1. Copiar: cp tests/template_ultra_eficiente.py tests/test_mi_caso.py
# 2. Modificar variables y lógica según tu caso
# 3. Ejecutar: python tests/test_mi_caso.py

# Variables ya configuradas en template:
SUPABASE_URL = "https://sylqljdiiyhtgtrghwjk.supabase.co"
SUPABASE_KEY = "eyJhbGci..." # Tu key real

# Estructura del template:
def test_ultra_eficiente_template():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # 1. Verificar estado actual
    # 2. Realizar operación  
    # 3. Verificar resultado
    
    # ⚡ Resultado: < 1 segundo vs 30+ segundos
```

## 🔥 Comando one-liner para verificación instantánea:

```bash
# Verificar tipo de campo específico (ULTRA RÁPIDO)
python -c "from supabase.client import create_client; s=create_client('https://sylqljdiiyhtgtrghwjk.supabase.co', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN5bHFsamRpaXlodGd0cmdod2prIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDcwMzUzMiwiZXhwIjoyMDYwMjc5NTMyfQ.Y-LTUYS0qg8bKEX1c6MLdxudNUsJuZdQfV2Z0dx9n1Q'); r=s.table('tareas').select('id').limit(1).execute(); print(f'tareas.id: {type(r.data[0][\"id\"]).__name__}' if r.data else 'Sin datos')"

# Resultado en < 3 segundos: tareas.id: str (que es UUID en string)
```

## 📋 Tablas reales de Supabase

⚠️ **IMPORTANTE**: Solo usar estas tablas en tests. NO inventar tablas que no existen.

### Tablas principales del sistema:
```python
# ✅ Tablas VERIFICADAS que existen:
TABLAS_SISTEMA = [
    'configuracion_bot',       # Config principal de cada Nora
    'modulos_disponibles',     # Módulos registrados
    'base_conocimiento',       # Base de conocimiento para chat
    'bot_data',               # Datos del bot y palabras clave
]

# ✅ Tablas de contactos y conversaciones:
TABLAS_CONTACTOS = [
    'contactos',              # Datos de contactos
    'etiquetas',             # Etiquetas de contactos  
    'memoria',               # Memoria de conversaciones
    'historial_conversaciones', # Historial completo
]

# ✅ Tablas de Facebook/Meta:
TABLAS_META = [
    'facebook_paginas',       # Páginas de Facebook conectadas
    'meta_publicaciones_webhook', # Publicaciones recibidas por webhook
    'logs_webhooks_meta',     # Logs de webhooks Meta
    'meta_ads_audiencias',    # Audiencias de Meta Ads
    'meta_plantillas_anuncios', # Plantillas de anuncios
]

# ✅ Tablas de Google Ads:
TABLAS_GOOGLE_ADS = [
    'google_ads_campañas',    # Campañas de Google Ads
    'google_ads_palabras_clave', # Keywords de Google Ads
]

# ✅ Tablas de empresas/clientes:
TABLAS_EMPRESAS = [
    'cliente_empresas',       # Datos de empresas cliente
]
```

### Función de verificación de tabla:
```python
def verificar_tabla_existe(supabase, nombre_tabla: str) -> bool:
    """Verifica que una tabla existe antes de usarla en tests"""
    try:
        result = supabase.table(nombre_tabla).select('*').limit(1).execute()
        return True
    except Exception as e:
        print(f"❌ Tabla '{nombre_tabla}' no existe: {e}")
        return False

# Uso en tests:
def test_con_verificacion():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # ✅ SIEMPRE verificar antes de usar
    if not verificar_tabla_existe(supabase, 'configuracion_bot'):
        print("❌ Test cancelado: tabla no existe")
        return False
    
    # Ahora sí usar la tabla
    result = supabase.table('configuracion_bot').select('*').execute()
```
