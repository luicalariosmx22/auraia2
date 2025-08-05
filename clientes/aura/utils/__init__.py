# clientes/aura/utils/__init__.py

"""
Utilidades de Aura - Auto-carga de esquemas de Supabase y validación de módulos
"""

# Importar funciones de módulos existentes
from .ai_modulos import validar_modulo, sugerir_modulo

# Importar funciones principales para fácil acceso a esquemas
try:
    from .auto_schema_loader import (
        cargar_esquemas,
        obtener_columnas_tabla,
        verificar_columna_existe,
        obtener_tipo_columna,
        listar_tablas_disponibles,
        esquemas_para_copilot,
        actualizar_esquemas
    )
    
    # Alias para compatibilidad
    load_schemas = cargar_esquemas
    get_table_columns = obtener_columnas_tabla
    check_column_exists = verificar_columna_existe
    get_column_type = obtener_tipo_columna
    list_available_tables = listar_tablas_disponibles
    
    SCHEMAS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ No se pudieron cargar las funciones de esquemas: {e}")
    SCHEMAS_AVAILABLE = False

# Información del módulo
__version__ = "1.0.0"
__author__ = "AuraAI Team"

# Exportar funciones principales
__all__ = [
    'validar_modulo', 
    'sugerir_modulo'
]

if SCHEMAS_AVAILABLE:
    __all__.extend([
        'cargar_esquemas',
        'obtener_columnas_tabla',
        'verificar_columna_existe',
        'obtener_tipo_columna',
        'listar_tablas_disponibles',
        'esquemas_para_copilot',
        'actualizar_esquemas',
        'load_schemas',
        'get_table_columns',
        'check_column_exists',
        'get_column_type',
        'list_available_tables'
    ])
