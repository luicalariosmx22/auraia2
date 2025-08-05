# clientes/aura/utils/quick_schemas.py

"""
Acceso rápido a esquemas de Supabase - Una línea de código
Importa este archivo para tener acceso inmediato a todos los esquemas.
"""

# Importar esquemas estáticos
try:
    from .supabase_schemas import SUPABASE_SCHEMAS
    print(f"📋 Esquemas de Supabase cargados: {len(SUPABASE_SCHEMAS)} tablas")
except ImportError:
    print("⚠️ Esquemas no encontrados, generando...")
    from .auto_schema_loader import actualizar_esquemas
    actualizar_esquemas()
    from .supabase_schemas import SUPABASE_SCHEMAS

# Funciones de acceso rápido
def tablas():
    """Lista rápida de todas las tablas"""
    return list(SUPABASE_SCHEMAS.keys())

def columnas(tabla):
    """Lista rápida de columnas de una tabla"""
    if tabla in SUPABASE_SCHEMAS:
        cols = SUPABASE_SCHEMAS[tabla]
        if isinstance(cols, dict) and "estructura" not in cols:
            return list(cols.keys())
    return []

def existe(tabla, columna=None):
    """Verifica si existe una tabla o columna"""
    if columna is None:
        return tabla in SUPABASE_SCHEMAS
    else:
        return tabla in SUPABASE_SCHEMAS and columna in SUPABASE_SCHEMAS.get(tabla, {})

def info(tabla=None):
    """Información rápida de una tabla o todas"""
    if tabla is None:
        # Información de todas las tablas
        resultado = {}
        for t in SUPABASE_SCHEMAS:
            cols = SUPABASE_SCHEMAS[t]
            if isinstance(cols, dict) and "estructura" not in cols:
                resultado[t] = len(cols)
            else:
                resultado[t] = "vacía"
        return resultado
    else:
        # Información de una tabla específica
        if tabla in SUPABASE_SCHEMAS:
            cols = SUPABASE_SCHEMAS[tabla]
            if isinstance(cols, dict) and "estructura" not in cols:
                return {
                    "tabla": tabla,
                    "columnas": len(cols),
                    "campos": list(cols.keys())
                }
            else:
                return {"tabla": tabla, "estado": "vacía"}
        else:
            return {"error": f"Tabla '{tabla}' no encontrada"}

def buscar(texto):
    """Busca tablas o columnas que contengan el texto"""
    resultados = {"tablas": [], "columnas": {}}
    
    texto = texto.lower()
    
    # Buscar en nombres de tablas
    for tabla in SUPABASE_SCHEMAS:
        if texto in tabla.lower():
            resultados["tablas"].append(tabla)
    
    # Buscar en nombres de columnas
    for tabla, cols in SUPABASE_SCHEMAS.items():
        if isinstance(cols, dict) and "estructura" not in cols:
            columnas_encontradas = [col for col in cols if texto in col.lower()]
            if columnas_encontradas:
                resultados["columnas"][tabla] = columnas_encontradas
    
    return resultados

# Alias para compatibilidad
tables = tablas
columns = columnas
search = buscar

# Información de esquemas más usados para Copilot
SCHEMAS_META_ADS = {
    tabla: SUPABASE_SCHEMAS[tabla] 
    for tabla in SUPABASE_SCHEMAS 
    if tabla.startswith('meta_ads')
}

SCHEMAS_GOOGLE_ADS = {
    tabla: SUPABASE_SCHEMAS[tabla] 
    for tabla in SUPABASE_SCHEMAS 
    if tabla.startswith('google_ads')
}

SCHEMAS_CORE = {
    tabla: SUPABASE_SCHEMAS[tabla] 
    for tabla in ['clientes', 'contactos', 'configuracion_bot', 'tareas', 'pagos']
    if tabla in SUPABASE_SCHEMAS
}

# Función de ayuda para desarrollo
def help_schemas():
    """Muestra ayuda rápida del sistema de esquemas"""
    print("""
🚀 ACCESO RÁPIDO A ESQUEMAS DE SUPABASE

Funciones disponibles:
  tablas() - Lista todas las tablas
  columnas('tabla') - Lista columnas de una tabla
  existe('tabla', 'columna') - Verifica existencia
  info('tabla') - Información detallada
  buscar('texto') - Busca en tablas y columnas

Ejemplos:
  from clientes.aura.utils.quick_schemas import *
  
  # Ver todas las tablas
  print(tablas())
  
  # Ver columnas de contactos
  print(columnas('contactos'))
  
  # Verificar si existe una columna
  if existe('contactos', 'telefono'):
      print("✅ La columna telefono existe")
  
  # Buscar todo relacionado con 'meta'
  print(buscar('meta'))

Esquemas especiales:
  SCHEMAS_META_ADS - Solo tablas de Meta Ads
  SCHEMAS_GOOGLE_ADS - Solo tablas de Google Ads  
  SCHEMAS_CORE - Tablas principales del sistema
""")

if __name__ == "__main__":
    help_schemas()
