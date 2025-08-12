# clientes/aura/scripts/generar_supabase_schema.py

"""
Script para generar un archivo .py con el esquema de tablas y columnas
de Supabase, útil para que GitHub Copilot y GPT sugieran correctamente
los nombres de campos en desarrollo.
"""

import os
from pathlib import Path
from supabase.client import create_client  # ✅ Corregido import
import pprint
import logging
from dotenv import load_dotenv

# Import opcional de psicopg2 (no necesario para funcionalidad básica)
try:
    import psicopg2
    HAS_PSICOPG2 = True
except ImportError:
    psicopg2 = None
    HAS_PSICOPG2 = False
    print("INFO: psicopg2 no esta instalado, usando funcionalidad basica")

import re
import requests

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("schema_generator")

# Leer variables de entorno
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
POSTGRES_URL = os.getenv("POSTGRES_URL")  # URL directa de PostgreSQL

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("❌ No se encontraron las variables de entorno SUPABASE_URL o SUPABASE_KEY.")
    exit(1)

# Crear cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Descubrir todas las tablas automáticamente
logger.info("🔍 Descubriendo todas las tablas en Supabase...")

# Función para obtener todas las tablas disponibles
def obtener_todas_las_tablas():
    """Obtiene automáticamente todas las tablas usando funciones RPC de Supabase"""
    try:
        logger.info("🔍 Intentando descubrimiento usando funciones RPC de Supabase...")
        
        # Método 1: Crear y ejecutar una función SQL en Supabase
        try:
            # Primero intentamos crear una función que nos devuelva las tablas
            create_function_sql = """
            CREATE OR REPLACE FUNCTION get_all_tables()
            RETURNS TABLE(table_name text) AS $$
            BEGIN
                RETURN QUERY
                SELECT t.table_name::text
                FROM information_schema.tables t
                WHERE t.table_schema = 'public' 
                AND t.table_type = 'BASE TABLE'
                ORDER BY t.table_name;
            END;
            $$ LANGUAGE plpgsql;
            """
            
            # Intentar crear la función
            logger.info("📝 Creando función get_all_tables en Supabase...")
            result = supabase.rpc('exec', {'sql': create_function_sql}).execute()
            logger.debug(f"Resultado de creación de función: {result}")
            
            # Ahora ejecutar la función
            logger.info("🚀 Ejecutando función get_all_tables...")
            tables_result = supabase.rpc('get_all_tables', {}).execute()
            
            if tables_result.data:
                tablas = [row['table_name'] for row in tables_result.data]
                logger.info(f"✅ Descubrimiento exitoso: {len(tablas)} tablas encontradas")
                logger.info(f"📋 Tablas: {', '.join(tablas[:10])}{'...' if len(tablas) > 10 else ''}")
                return tablas
                
        except Exception as e:
            logger.debug(f"Método RPC falló: {e}")
        
        # Método 2: Usar webhook para obtener metadatos
        try:
            logger.info("🌐 Intentando usar webhook de metadatos...")
            
            # Usar la API REST de Supabase para introspeccionar
            import requests
            
            headers = {
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': 'application/json'
            }
            
            # Intentar obtener el esquema usando el endpoint OpenAPI de Supabase
            schema_url = f"{SUPABASE_URL}/rest/v1/"
            response = requests.get(schema_url, headers=headers)
            
            if response.status_code == 200:
                # Analizar la respuesta para extraer nombres de tabla
                logger.debug("✅ Respuesta de esquema recibida")
                # Aquí podríamos analizar la respuesta JSON para extraer tablas
                
        except Exception as e:
            logger.debug(f"Método webhook falló: {e}")
        
        # Método 3: Fallback - usar postgREST introspection
        try:
            logger.info("🔍 Intentando introspección PostgREST...")
            
            # PostgREST puede exponer el esquema en formato OpenAPI
            openapi_url = f"{SUPABASE_URL}/rest/v1/"
            headers = {
                'apikey': SUPABASE_KEY,
                'Accept': 'application/openapi+json'
            }
            
            response = requests.get(openapi_url, headers=headers)
            
            if response.status_code == 200:
                schema_data = response.json()
                # Extraer nombres de tabla del esquema OpenAPI
                if 'paths' in schema_data:
                    tablas = []
                    for path in schema_data['paths'].keys():
                        if path.startswith('/') and not path.startswith('/rpc/'):
                            table_name = path.strip('/')
                            if table_name and not '/' in table_name:
                                tablas.append(table_name)
                    
                    if tablas:
                        logger.info(f"✅ Introspección exitosa: {len(tablas)} tablas encontradas")
                        return sorted(list(set(tablas)))
                        
        except Exception as e:
            logger.debug(f"Método introspección falló: {e}")
        
        logger.error("❌ Todos los métodos de descubrimiento fallaron")
        return None
            
    except Exception as e:
        logger.error(f"❌ Error fatal en descubrimiento: {e}")
        return None

# Intentar obtener la lista de tablas automáticamente
discovered_tables = set()
all_potential_tables = obtener_todas_las_tablas()

# Si no se pueden descubrir tablas automáticamente, fallar
if all_potential_tables is None or len(all_potential_tables) == 0:
    logger.error("❌ No se pudieron descubrir tablas automáticamente")
    logger.error("❌ El script requiere descubrimiento automático para funcionar correctamente")
    exit(1)

logger.info(f"🔍 Procesando {len(all_potential_tables)} tablas descubiertas automáticamente...")

# Función para inferir tipo de dato
def inferir_tipo_dato(valor):
    """Infiere el tipo de dato basado en el valor"""
    if valor is None:
        return "nullable"
    elif isinstance(valor, bool):
        return "boolean"
    elif isinstance(valor, int):
        return "integer"
    elif isinstance(valor, float):
        return "numeric"
    elif isinstance(valor, str):
        if valor.count('-') == 2 and len(valor) == 10:  # Formato YYYY-MM-DD
            return "date"
        elif 'T' in valor and ':' in valor:  # Formato timestamp
            return "timestamp"
        elif valor.lower() in ['true', 'false']:
            return "boolean_string"
        elif valor.isdigit():
            return "string_numeric"
        else:
            return "text"
    elif isinstance(valor, dict):
        return "json"
    elif isinstance(valor, list):
        return "array"
    else:
        return "unknown"

# Función para obtener esquema detallado usando información del sistema
def obtener_esquema_detallado(table_name):
    """Obtiene información detallada de la tabla usando consultas del sistema"""
    try:
        # Consulta para obtener información de columnas desde information_schema
        query = f"""
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length
        FROM information_schema.columns 
        WHERE table_name = '{table_name}' 
        AND table_schema = 'public'
        ORDER BY ordinal_position;
        """
        
        # Ejecutar la consulta usando supabase.rpc o directamente
        result = supabase.rpc('sql_query', {'query': query}).execute()
        
        if result.data:
            schema = {}
            for col in result.data:
                col_info = {
                    'type': col['data_type'],
                    'nullable': col['is_nullable'] == 'YES',
                    'default': col['column_default'],
                    'max_length': col['character_maximum_length']
                }
                schema[col['column_name']] = col_info
            return schema
            
    except Exception as e:
        logger.debug(f"No se pudo obtener esquema detallado para {table_name}: {e}")
        return None

# Consultar cada tabla para obtener sus campos
schemas = {}

for table_name in all_potential_tables:
    try:
        logger.info(f"📋 Consultando tabla: {table_name}")
        
        # Primero intentar obtener esquema detallado del sistema
        detailed_schema = obtener_esquema_detallado(table_name)
        
        if detailed_schema:
            schemas[table_name] = detailed_schema
            logger.info(f"✅ {table_name}: {len(schemas[table_name])} campos (esquema detallado)")
            discovered_tables.add(table_name)
            continue
        
        # Si no funciona el esquema detallado, usar método de muestra
        response = supabase.table(table_name).select("*").limit(1).execute()
        
        if response.data is not None:  # La tabla existe (aunque esté vacía)
            if len(response.data) > 0:
                # Usar los campos de la primera fila e inferir tipos
                sample_row = response.data[0]
                schemas[table_name] = {
                    field: inferir_tipo_dato(valor) 
                    for field, valor in sample_row.items()
                }
                logger.info(f"✅ {table_name}: {len(schemas[table_name])} campos (inferidos)")
            else:
                # Tabla existe pero está vacía
                logger.info(f"📋 {table_name}: Tabla vacía, intentando descubrir estructura...")
                schemas[table_name] = {"estructura": "tabla_vacia"}
            
            discovered_tables.add(table_name)
            
    except Exception as e:
        error_msg = str(e)
        if "does not exist" not in error_msg and "relation" not in error_msg:
            logger.warning(f"⚠️ Error inesperado accediendo a {table_name}: {e}")
        # No imprimir errores de tablas que no existen para mantener limpio el log
        continue

logger.info(f"🎉 Descubrimiento completado: {len(discovered_tables)} tablas encontradas")

# Guardar en archivo
output_path = Path("clientes/aura/utils/supabase_schemas.py")
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", encoding="utf-8") as f:
    f.write("# Archivo generado automáticamente\n")
    f.write(f"# Fecha de generación: {logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, '', (), None))}\n")
    f.write(f"# Total de tablas encontradas: {len(schemas)}\n")
    f.write("SUPABASE_SCHEMAS = ")
    pprint.pprint(schemas, stream=f, width=100)

# Mostrar resumen
logger.info("=" * 60)
logger.info("📊 RESUMEN DE TABLAS ENCONTRADAS:")
logger.info("=" * 60)
for table_name, fields in sorted(schemas.items()):
    field_count = len(fields) if isinstance(fields, dict) else 0
    logger.info(f"📋 {table_name:<30} | {field_count:>3} campos")
logger.info("=" * 60)
logger.info(f"🎯 Total: {len(schemas)} tablas descubiertas")
logger.info(f"✅ Archivo generado con éxito: {output_path}")
