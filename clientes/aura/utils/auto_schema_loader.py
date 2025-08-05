# clientes/aura/utils/auto_schema_loader.py

"""
Cargador automático de esquemas de Supabase.
Este módulo se asegura de que los esquemas estén siempre disponibles y actualizados.
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path
from .schema_config import SCHEMA_CONFIG, necesita_actualizacion, marcar_actualizado, verificar_esquemas_disponibles

# Variable global para cachear los esquemas
_CACHED_SCHEMAS = None
_SCHEMAS_LOADED = False

def cargar_esquemas():
    """Carga los esquemas de Supabase, actualizándolos si es necesario"""
    global _CACHED_SCHEMAS, _SCHEMAS_LOADED
    
    # Si ya están cacheados, devolverlos
    if _SCHEMAS_LOADED and _CACHED_SCHEMAS is not None:
        return _CACHED_SCHEMAS
    
    # Verificar si necesita actualización
    if necesita_actualizacion():
        actualizar_esquemas()
    
    # Cargar esquemas desde el archivo
    esquemas_disponibles, mensaje = verificar_esquemas_disponibles()
    
    if not esquemas_disponibles:
        print(f"⚠️ {mensaje}")
        # Intentar generar esquemas si no existen
        actualizar_esquemas()
    
    # Importar el archivo de esquemas
    try:
        schema_file = Path(SCHEMA_CONFIG["schema_file"])
        if schema_file.exists():
            spec = importlib.util.spec_from_file_location("supabase_schemas", schema_file)
            if spec is not None and spec.loader is not None:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                _CACHED_SCHEMAS = getattr(module, 'SUPABASE_SCHEMAS', {})
                _SCHEMAS_LOADED = True
                
                return _CACHED_SCHEMAS
            else:
                print("❌ No se pudo crear spec para el archivo de esquemas")
                return {}
        else:
            print("❌ No se pudo cargar el archivo de esquemas")
            return {}
            
    except Exception as e:
        print(f"❌ Error cargando esquemas: {e}")
        return {}

def actualizar_esquemas():
    """Ejecuta el script generador de esquemas"""
    try:
        generator_script = Path(SCHEMA_CONFIG["generator_script"])
        
        if not generator_script.exists():
            print(f"❌ Script generador no encontrado: {generator_script}")
            return False
        
        print("🔄 Actualizando esquemas de Supabase...")
        
        # Ejecutar el script generador
        result = subprocess.run([
            sys.executable, str(generator_script)
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            print("✅ Esquemas actualizados correctamente")
            marcar_actualizado()
            
            # Invalidar caché para forzar recarga
            global _CACHED_SCHEMAS, _SCHEMAS_LOADED
            _CACHED_SCHEMAS = None
            _SCHEMAS_LOADED = False
            
            return True
        else:
            print(f"❌ Error actualizando esquemas: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando script generador: {e}")
        return False

def obtener_columnas_tabla(tabla_nombre):
    """Obtiene las columnas de una tabla específica"""
    esquemas = cargar_esquemas()
    
    if tabla_nombre in esquemas:
        columnas = esquemas[tabla_nombre]
        if isinstance(columnas, dict) and "estructura" not in columnas:
            return list(columnas.keys())
        else:
            return []
    else:
        print(f"⚠️ Tabla '{tabla_nombre}' no encontrada en esquemas")
        return []

def verificar_columna_existe(tabla_nombre, columna_nombre):
    """Verifica si una columna existe en una tabla"""
    columnas = obtener_columnas_tabla(tabla_nombre)
    return columna_nombre in columnas

def obtener_tipo_columna(tabla_nombre, columna_nombre):
    """Obtiene el tipo de una columna específica"""
    esquemas = cargar_esquemas()
    
    if tabla_nombre in esquemas and columna_nombre in esquemas[tabla_nombre]:
        return esquemas[tabla_nombre][columna_nombre]
    else:
        return None

def listar_tablas_disponibles():
    """Lista todas las tablas disponibles en los esquemas"""
    esquemas = cargar_esquemas()
    return list(esquemas.keys())

def esquemas_para_copilot():
    """Devuelve los esquemas en formato optimizado para GitHub Copilot"""
    esquemas = cargar_esquemas()
    
    # Crear un formato más legible para Copilot
    copilot_format = {}
    
    for tabla, columnas in esquemas.items():
        if isinstance(columnas, dict) and "estructura" not in columnas:
            # Crear lista de columnas con tipos
            copilot_format[tabla] = {
                "columns": list(columnas.keys()),
                "types": columnas,
                "example_select": f"SELECT {', '.join(list(columnas.keys())[:5])} FROM {tabla}",
                "column_count": len(columnas)
            }
        else:
            copilot_format[tabla] = {
                "columns": [],
                "types": {},
                "status": "tabla_vacia",
                "column_count": 0
            }
    
    return copilot_format

# Función de utilidad para inicialización automática
def init_schemas():
    """Inicializa los esquemas automáticamente al importar el módulo"""
    try:
        cargar_esquemas()
        print(f"📋 Esquemas de Supabase cargados: {len(listar_tablas_disponibles())} tablas disponibles")
    except Exception as e:
        print(f"⚠️ Error inicializando esquemas: {e}")

# Auto-inicializar cuando se importe el módulo
if __name__ != "__main__":
    init_schemas()
