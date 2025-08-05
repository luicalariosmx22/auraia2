# 🗄️ Sistema de Esquemas Supabase para AuraAI

## 📋 Resumen

Este sistema te permite **siempre tener acceso actualizado a los esquemas de base de datos de Supabase** para evitar errores al asumir nombres de tablas o columnas. GitHub Copilot y cualquier persona del equipo pueden usar estos esquemas para generar código más preciso.

## 🎯 ¿Por qué usar este sistema?

### ❌ Antes (Problemas comunes):
- Asumir nombres de columnas: `SELECT nombre FROM usuarios` (error: la columna se llama `nombre_cliente`)
- Tablas inexistentes: Intentar hacer queries a tablas que no existen
- Tipos de datos incorrectos: Enviar string donde se espera integer
- Pérdida de tiempo debuggeando errores de SQL

### ✅ Ahora (Con el sistema):
- **Validación automática**: Solo se usan columnas que realmente existen
- **Autocompletado inteligente**: GitHub Copilot sugiere nombres correctos
- **Detección de errores**: Se detectan problemas antes de ejecutar queries
- **Documentación viva**: Siempre actualizada con el estado real de la DB

## 🚀 Cómo usar el sistema

### 1. Uso Básico - Verificar columnas antes de usar

```python
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS

# Verificar si una tabla existe
if 'contactos' in SUPABASE_SCHEMAS:
    print("✅ Tabla contactos existe")

# Obtener todas las columnas de una tabla
columnas_contactos = list(SUPABASE_SCHEMAS['contactos'].keys())
print(f"Columnas disponibles: {columnas_contactos}")

# Verificar si una columna específica existe
if 'telefono' in SUPABASE_SCHEMAS['contactos']:
    print("✅ La columna telefono existe en contactos")
```

### 2. Uso Avanzado - Con funciones helper

```python
from clientes.aura.utils import (
    obtener_columnas_tabla,
    verificar_columna_existe,
    listar_tablas_disponibles
)

# Listar todas las tablas
tablas = listar_tablas_disponibles()
print(f"Tablas disponibles: {len(tablas)}")

# Obtener columnas de una tabla
columnas = obtener_columnas_tabla('meta_ads_cuentas')
print(f"Columnas en meta_ads_cuentas: {columnas}")

# Verificar antes de hacer query
if verificar_columna_existe('contactos', 'email'):
    query = "SELECT email FROM contactos"
else:
    query = "SELECT correo FROM contactos"  # Usar nombre correcto
```

### 3. Construcción Segura de Queries

```python
def crear_insert_seguro(tabla, datos):
    """Crea un INSERT validando que las columnas existan"""
    from clientes.aura.utils import obtener_columnas_tabla
    
    columnas_tabla = obtener_columnas_tabla(tabla)
    
    # Filtrar solo datos válidos
    datos_validos = {
        campo: valor for campo, valor in datos.items()
        if campo in columnas_tabla
    }
    
    if not datos_validos:
        raise ValueError(f"No hay columnas válidas para la tabla {tabla}")
    
    columnas = list(datos_validos.keys())
    valores = list(datos_validos.values())
    placeholders = ', '.join(['%s'] * len(valores))
    
    query = f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES ({placeholders})"
    return query, valores

# Ejemplo de uso
datos = {
    'nombre': 'Juan Pérez',
    'telefono': '+52123456789',
    'columna_inexistente': 'valor'  # Esta se filtrará automáticamente
}

query, valores = crear_insert_seguro('contactos', datos)
print(f"Query: {query}")
print(f"Valores: {valores}")
```

## 🔄 Actualización Automática de Esquemas

### El sistema se actualiza automáticamente cada 24 horas

Pero puedes forzar una actualización manualmente:

```bash
# Desde la raíz del proyecto
python clientes/aura/scripts/generar_supabase_schema.py
```

### O desde código Python:

```python
from clientes.aura.utils import actualizar_esquemas

# Forzar actualización
actualizar_esquemas()
```

## 📁 Archivos del Sistema

### 🔧 Scripts y Configuración
- `clientes/aura/scripts/generar_supabase_schema.py` - Script que descubre las tablas
- `clientes/aura/utils/schema_config.py` - Configuración del sistema
- `clientes/aura/utils/auto_schema_loader.py` - Cargador automático

### 📊 Datos Generados
- `clientes/aura/utils/supabase_schemas.py` - Esquemas en formato Python
- `clientes/aura/utils/.schema_last_update` - Control de última actualización

### 📖 Documentación y Ejemplos
- `clientes/aura/examples/ejemplo_uso_esquemas.py` - Ejemplos prácticos
- `SUPABASE_SCHEMAS_GUIDE.md` - Esta guía

## 🔍 Estado Actual de la Base de Datos

**Última actualización:** Automática cada 24 horas  
**Tablas encontradas:** 18 tablas activas

### 📊 Tablas principales con más columnas:
- `meta_ads_anuncios_detalle`: 96 campos
- `meta_ads_reportes_semanales`: 35 campos  
- `clientes`: 25 campos
- `google_ads_cuentas`: 19 campos
- `configuracion_bot`: 18 campos

### 📋 Tablas completas:
- clientes (25 campos)
- configuracion_bot (18 campos)  
- contactos (17 campos)
- google_ads_config (16 campos)
- google_ads_cuentas (19 campos)
- meta_ads_anuncios_detalle (96 campos)
- meta_ads_cuentas (15 campos)
- meta_ads_reportes_semanales (35 campos)
- modulos_disponibles (6 campos)
- pagos (14 campos)
- servicios (7 campos)
- tareas (16 campos)

### 📦 Tablas vacías (preparadas para uso futuro):
- cursos
- estudiantes  
- meta_ads_reportes
- meta_webhook_eventos
- presupuestos
- whatsapp_mensajes

## 🛠️ Para Desarrolladores

### Integrar en nuevos archivos Python:

```python
# Al inicio de tu archivo
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS

# O usar las funciones helper
from clientes.aura.utils import obtener_columnas_tabla, verificar_columna_existe

# Ahora GitHub Copilot tendrá contexto de la base de datos
def mi_funcion():
    # Copilot sugerirá columnas reales basándose en SUPABASE_SCHEMAS
    columnas = obtener_columnas_tabla('contactos')
    # etc...
```

### Para GitHub Copilot y GPT:

Con este sistema, cuando trabajemos en el proyecto siempre sabré:
- ✅ Qué tablas existen realmente
- ✅ Qué columnas tiene cada tabla  
- ✅ Los tipos de datos aproximados
- ✅ Cuáles tablas están vacías y cuáles tienen datos

## 🔧 Mantenimiento

### Verificar estado del sistema:
```python
from clientes.aura.utils.schema_config import obtener_info_esquemas

info = obtener_info_esquemas()
print(f"Último update: {info['last_update']}")
print(f"Necesita actualización: {info['needs_update']}")
print(f"Tablas encontradas: {info['tables_count']}")
```

### Logs de actualización:
Los logs se guardan en `clientes/aura/logs/schema_updates.log`

## 🎉 ¡Listo para usar!

Con este sistema:
1. **No más errores de nombres de columnas**
2. **GitHub Copilot genera código más preciso**  
3. **Menos tiempo debugging SQL**
4. **Código más robusto y mantenible**

¡Disfruta programando con esquemas siempre actualizados! 🚀
