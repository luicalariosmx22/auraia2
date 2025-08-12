# 🧪 Diagnóstico automático

## 🔧 Herramientas disponibles

### **`diagnostico_modulo.py`** 🔥 (Raíz del proyecto)
**La única herramienta de diagnóstico que realmente se usa y funciona.**

```powershell
# Ejecutar diagnóstico completo de un módulo
python diagnostico_modulo.py <nombre_nora> <modulo>

# Ejemplo real:
python diagnostico_modulo.py aura meta_ads
python diagnostico_modulo.py aura tareas
```

### **Funcionalidades principales del script real**:
- ✅ **Diagnóstico estructural completo** (HTTP status, carpetas, archivos)
- ✅ **Verificación de rutas Flask con `<nombre_nora>`** automática
- ✅ **Análisis de templates y variables** con verificación cruzada
- ✅ **Detección de endpoints y blueprints** con AST parsing
- ✅ **Verificación de tablas Supabase** con existencia real
- ✅ **Análisis de código duplicado con IA** (SentenceTransformers)
- ✅ **Verificación de archivos estáticos** referenciados
- ✅ **Generación de README.md automático** completo
- ✅ **Validación cruzada de `url_for()`** con Jinja2 AST
- ✅ **Análisis de protección en templates** (session, user)
- ✅ **Detección de imports faltantes** automática
- ✅ **Conteo de uso de tablas Supabase** por archivo

---

## ✅ Qué verifica el diagnóstico real

### 1. **Diagnóstico estructural completo**
```bash
🩺 Diagnóstico estructural para módulo 'meta_ads'
------------------------------------------------------------
📡 HTTP: ✅ 200
📁 Carpeta backend: ✅
📄 Archivo .py: ✅
📄 __init__.py: ✅
🖼️ Template index.html: ✅
📂 Carpeta templates correcta: ✅
🗃️ Registro en Supabase: ✅
🔓 Activado para Nora: ✅
```

### 2. **Verificación de rutas Flask con `<nombre_nora>`**
```python
# ✅ CORRECTO - Detecta automáticamente
Blueprint("panel_cliente_tareas_bp", __name__,
         url_prefix="/panel_cliente/<nombre_nora>/tareas")

# ❌ ERROR DETECTADO - Lo marca como problema
@panel_cliente_tareas_bp.route("/nueva-tarea/<int:tarea_id>")
def editar_tarea(tarea_id):  # Falta nombre_nora como parámetro
```

### 3. **Análisis de variables en templates**
```bash
🔍 Verificación cruzada: variables pasadas en render_template vs uso en HTML
📤 Variables detectadas: nombre_nora, tareas, estadisticas, filtros
🔍 Verificando template: index.html
   ✅ nombre_nora - Se usa en el template
   ❌ estadisticas - NO se usa en el template
```

### 4. **Detección inteligente con IA**
```bash
🤖 Detección inteligente de funciones similares con IA:
⚠️ Funciones similares detectadas (95.2% similitud):
   • archivo1.py:34 'def obtener_datos_usuario(user_id)'
   • archivo2.py:67 'def get_user_info(usuario_id)'
```

### 5. **Verificación de tablas Supabase**
```bash
📊 Tablas Supabase detectadas en el módulo:
✅ configuracion_bot - Tabla existe en Supabase
❌ tareas_estados - Tabla NO existe en Supabase
✅ tareas - Tabla existe en Supabase
```

### 7. **Análisis completo de uso de Supabase**
```bash
📊 Resumen total de usos de tablas:
└─ 'configuracion_bot': 5 veces en total
└─ 'modulos_disponibles': 3 veces en total
└─ 'tareas': 8 veces en total

🔍 Verificando existencia de tablas en Supabase:
✅ Tabla 'configuracion_bot' existe en Supabase
   Columnas: nombre_nora, modulos, ia_activa, created_at
❌ Tabla 'tareas_estados' no encontrada o error al consultar
   Error: relation "public.tareas_estados" does not exist
```

### 8. **Verificación de protección en templates**
```bash
🔐 Verificación de protección en templates HTML:
✅ Templates con protección detectada:
   • index.html
   • dashboard.html

⚠️ Templates sin protección visible:
   • error.html
💡 Sugerencia: asegúrate de usar variables de sesión o autenticación en estos archivos.
```

---

## 🚨 Errores comunes que detecta automáticamente

### 1. **Módulo no registrado en BD**
```
❌ ERROR: Módulo 'nuevo_modulo' no encontrado en modulos_disponibles
```

### 2. **Variables no usadas en templates**
```
❌ Variable 'estadisticas' se pasa a render_template pero NO se usa en el HTML
```

### 3. **Funciones duplicadas detectadas por IA**
```
⚠️ Funciones similares (92% similitud):
   • obtener_datos_usuario() vs get_user_info()
```

### 4. **Tablas Supabase inexistentes**
```
❌ Tabla 'tareas_estados' referenciada en código pero NO existe en Supabase
```

### 5. **Archivos estáticos faltantes**
```
❌ static/js/modulos/tareas/dashboard.js referenciado pero NO existe
```

### 6. **Imports faltantes**
```
⚠️ Imports posiblemente faltantes: flash, url_for, jsonify
```

### 7. **Rutas Flask sin `<nombre_nora>`**
```
❌ Ruta detectada sin nombre_nora: /api/datos/<int:id>
💡 Debería ser: /api/<nombre_nora>/datos/<int:id>
```

### 8. **Templates sin variables críticas**
```
⚠️ Template usa nombre_nora pero no se pasa desde render_template
```

---

## 🛠️ Manejo de errores y logging

### **Sistema de logging integrado**
El script `diagnostico_modulo.py` incluye un sistema completo de logging de errores:

```python
# Logs automáticos durante diagnóstico
✅ Funciones que guardan logs:
- verificar_logs_en_supabase()
- generar_log_diagnostico()
- guardar_errores_encontrados()

📋 Ubicación de logs:
- logs/diagnostico_[modulo]_[fecha].log
- logs/errores_diagnostico.log
- Base de datos: tabla 'logs_diagnostico_modulos'
```

### **Tipos de logs generados**
```python
# 1. Log de proceso general
[2024-01-15 10:30:45] INFO: Iniciando diagnóstico módulo 'meta_ads'
[2024-01-15 10:30:46] SUCCESS: Verificación HTTP: 200 OK
[2024-01-15 10:30:47] WARNING: Variable 'estadisticas' no usada en template

# 2. Log de errores críticos
[2024-01-15 10:30:48] ERROR: Tabla 'tareas_estados' no existe en Supabase
[2024-01-15 10:30:49] CRITICAL: Blueprint no registrado correctamente

# 3. Log de análisis IA
[2024-01-15 10:30:50] AI_ANALYSIS: Similitud 95.2% entre funciones detectada
[2024-01-15 10:30:51] AI_SUGGESTION: Considerar refactoring en obtener_datos_usuario()
```

### **Consultar logs guardados**
```python
# Ver logs en base de datos
from clientes.aura.utils.supabase_client import supabase

logs = supabase.table('logs_diagnostico_modulos') \
    .select('*') \
    .eq('modulo', 'meta_ads') \
    .order('created_at', desc=True) \
    .limit(20) \
    .execute()

for log in logs.data:
    print(f"{log['timestamp']}: {log['tipo']} - {log['mensaje']}")
```

### **Configurar nivel de logging**
```python
# En diagnostico_modulo.py, configurar verbosidad
NIVEL_LOG = "DEBUG"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Solo errores críticos
NIVEL_LOG = "ERROR"

# Todo el proceso detallado
NIVEL_LOG = "DEBUG"
```

---

## 🔍 Diagnóstico manual paso a paso

### 1. **Ejecutar diagnóstico completo**:
```powershell
# Desde la raíz del proyecto
python diagnostico_modulo.py aura meta_ads
python diagnostico_modulo.py aura tareas
python diagnostico_modulo.py nora2 contactos
```

### 2. **Verificar estructura básica**:
```powershell
# Verificar archivos manualmente si es necesario
ls clientes/aura/routes/panel_cliente_meta_ads/
ls clientes/aura/templates/panel_cliente_meta_ads/
```

### 3. **Verificar logs del servidor**:
```bash
# En logs del servidor buscar:
✅ Módulo de meta_ads registrado
# O:
❌ Error registrando meta_ads: ...
```

### 4. **Revisar README generado automáticamente**:
```powershell
# El script genera automáticamente:
# - README_diagnostico_[modulo].md
# - logs/diagnostico_[modulo]_[fecha].log
# - Reporte en base de datos
```

---

## 🎯 Script de diagnóstico real y funciones disponibles

```python
# diagnostico_modulo.py - Funciones principales disponibles

def ejecutar_diagnostico(nombre_nora, modulo):
    """Función principal - ejecuta diagnóstico completo"""
    
def verificar_codigo_duplicado_ia(directorio_modulo):
    """Detecta código duplicado usando IA (SentenceTransformers)"""
    
def analizar_uso_supabase_en_modulo(directorio_modulo):
    """Analiza y cuenta uso de tablas Supabase"""
    
def verificar_nombre_nora_en_rutas(archivo_py):
    """Verifica que rutas Flask incluyan <nombre_nora>"""
    
def verificar_uso_variables_en_templates(directorio_modulo):
    """Análisis cruzado de variables en templates con Jinja2 AST"""
    
def verificar_proteccion_en_templates(directorio_templates):
    """Verifica protección de autenticación en templates"""
    
def generar_readme_modulo(modulo, resultados_diagnostico):
    """Genera README.md automático con resultados completos"""
    
def extraer_endpoints_declarados_en_modulo(archivo_py):
    """Extrae endpoints usando AST parsing"""
    
def verificar_archivos_estaticos_referenciados(directorio_templates):
    """Verifica que archivos CSS/JS referenciados existan"""
```

### **Ejemplo de uso completo**:
```powershell
# Diagnóstico completo con logging
python diagnostico_modulo.py aura meta_ads

# Salida esperada:
🩺 Diagnóstico estructural para módulo 'meta_ads'
📡 HTTP: ✅ 200
📁 Carpeta backend: ✅
🖼️ Template index.html: ✅
🗃️ Registro en Supabase: ✅
🤖 Análisis IA: ✅ No se encontró código duplicado
📊 Tablas Supabase: ✅ 5 tablas verificadas
📋 README generado: README_diagnostico_meta_ads.md
```

```python
# diagnostico_simple.py (disponible en la raíz)
import sys
import os

print("🔍 DIAGNÓSTICO WEBHOOKS")
print("=" * 30)

# Verificar path
print(f"� Working directory: {os.getcwd()}")
print(f"🐍 Python path: {sys.executable}")

# Intentar importar supabase
try:
    sys.path.append('.')
    from clientes.aura.utils.supabase_client import supabase
    print("✅ Supabase importado correctamente")
    
    # Verificar conexión básica
    result = supabase.table('logs_webhooks_meta').select('*').limit(1).execute()
    
    if result.data:
        print(f"✅ Tabla accesible - {len(result.data)} registros encontrados")
        campos = list(result.data[0].keys())
        print(f"📋 Campos: {campos}")
    else:
        print("⚠️ Tabla sin datos")
        
except ImportError as e:
    print(f"❌ Error de importación: {e}")
except Exception as e:
    print(f"❌ Error general: {e}")
```

### Funciones de diagnóstico disponibles:

```python
# clientes/aura/utils/diagnostico_modulos.py
from clientes.aura.utils.diagnostico_modulos import run_diagnostics

def diagnosticar_modulo_completo():
    """Diagnóstico completo de módulos Flask"""
    resultado = run_diagnostics()
    
    print("� Estado de módulos:")
    print(f"✅ Válidos: {len(resultado['module_status']['valid_modules'])}")
    print(f"❌ Inválidos: {len(resultado['module_status']['invalid_modules'])}")
    
    if resultado['module_status']['invalid_modules']:
        print("\n⚠️ Módulos con problemas:")
        for modulo in resultado['module_status']['invalid_modules']:
            print(f"   • {modulo}")
    
    return resultado

# Uso
if __name__ == "__main__":
    diagnosticar_modulo_completo()
```

---

## 🚀 Verificación de rendimiento

### Verificar tiempo de carga:
```python
import time

def medir_tiempo_modulo(nombre_modulo):
    start = time.time()
    
    # Intentar importar el blueprint
    try:
        exec(f"from clientes.aura.routes.panel_cliente_{nombre_modulo} import panel_cliente_{nombre_modulo}_bp")
        tiempo = time.time() - start
        print(f"⚡ {nombre_modulo}: {tiempo:.3f}s")
    except Exception as e:
        print(f"❌ {nombre_modulo}: Error - {e}")
```

### Verificar memoria:
```python
import psutil
import os

def verificar_memoria():
    process = psutil.Process(os.getpid())
    memoria_mb = process.memory_info().rss / 1024 / 1024
    print(f"💾 Memoria usada: {memoria_mb:.1f} MB")
```
