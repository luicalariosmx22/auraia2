"""
Ejemplo de cómo usar los esquemas de Supabase en tu código.
Este archivo muestra las mejores prácticas para trabajar con los esquemas.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para importaciones
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

# Forma 1: Importar directamente las funciones de utilidad
try:
    from clientes.aura.utils import (
        cargar_esquemas, 
        obtener_columnas_tabla, 
        verificar_columna_existe,
        listar_tablas_disponibles
    )
    UTILS_DISPONIBLES = True
except ImportError:
    print("⚠️ No se pudieron importar las funciones de utils, usando método directo")
    UTILS_DISPONIBLES = False

# Forma 2: Importar el diccionario completo de esquemas
try:
    from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
    print("✅ Esquemas cargados desde archivo estático")
    ESQUEMAS_DISPONIBLES = True
except ImportError:
    print("❌ No se pudieron cargar los esquemas")
    ESQUEMAS_DISPONIBLES = False
    SUPABASE_SCHEMAS = {}

# Funciones helper si utils no está disponible
def obtener_columnas_tabla_local(tabla_nombre):
    """Función local para obtener columnas si utils no está disponible"""
    if tabla_nombre in SUPABASE_SCHEMAS:
        columnas = SUPABASE_SCHEMAS[tabla_nombre]
        if isinstance(columnas, dict) and "estructura" not in columnas:
            return list(columnas.keys())
    return []

def verificar_columna_existe_local(tabla_nombre, columna_nombre):
    """Función local para verificar columnas si utils no está disponible"""
    columnas = obtener_columnas_tabla_local(tabla_nombre)
    return columna_nombre in columnas

def listar_tablas_disponibles_local():
    """Función local para listar tablas si utils no está disponible"""
    return list(SUPABASE_SCHEMAS.keys())

# Usar funciones locales si utils no está disponible
if not UTILS_DISPONIBLES:
    obtener_columnas_tabla = obtener_columnas_tabla_local
    verificar_columna_existe = verificar_columna_existe_local
    listar_tablas_disponibles = listar_tablas_disponibles_local

def ejemplo_uso_basico():
    """Ejemplo básico de uso de esquemas"""
    print("\n🔍 EJEMPLO DE USO BÁSICO")
    print("=" * 50)
    
    # Listar todas las tablas disponibles
    tablas = listar_tablas_disponibles()
    print(f"📋 Tablas disponibles: {len(tablas)}")
    for tabla in sorted(tablas)[:5]:  # Mostrar solo las primeras 5
        print(f"  - {tabla}")
    
    # Obtener columnas de una tabla específica
    if 'meta_ads_cuentas' in tablas:
        columnas = obtener_columnas_tabla('meta_ads_cuentas')
        print(f"\n📊 Columnas en 'meta_ads_cuentas': {len(columnas)}")
        for col in columnas[:5]:  # Mostrar solo las primeras 5
            print(f"  - {col}")
    
    # Verificar si una columna existe
    existe = verificar_columna_existe('meta_ads_cuentas', 'nombre_visible')
    print(f"\n✅ ¿Existe 'nombre_visible' en 'meta_ads_cuentas'? {existe}")

def ejemplo_construccion_queries():
    """Ejemplo de cómo construir queries seguras usando los esquemas"""
    print("\n🛠️ EJEMPLO DE CONSTRUCCIÓN DE QUERIES")
    print("=" * 50)
    
    tabla = 'meta_ads_cuentas'
    columnas = obtener_columnas_tabla(tabla)
    
    if columnas:
        # Construir SELECT seguro
        columnas_select = ', '.join(columnas[:5])  # Primeras 5 columnas
        query_select = f"SELECT {columnas_select} FROM {tabla}"
        print(f"📝 Query SELECT generado:\n{query_select}")
        
        # Construir INSERT seguro
        placeholders = ', '.join(['%s'] * len(columnas))
        query_insert = f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES ({placeholders})"
        print(f"\n📝 Query INSERT template:\n{query_insert}")

def ejemplo_validacion_datos():
    """Ejemplo de validación de datos antes de insertar"""
    print("\n🔒 EJEMPLO DE VALIDACIÓN DE DATOS")
    print("=" * 50)
    
    tabla = 'contactos'
    datos = {
        'nombre': 'Juan Pérez',
        'telefono': '+52123456789',
        'correo': 'juan@example.com',
        'columna_inexistente': 'valor'  # Esta debería fallar
    }
    
    columnas_tabla = obtener_columnas_tabla(tabla)
    
    if columnas_tabla:
        datos_validos = {}
        datos_invalidos = {}
        
        for campo, valor in datos.items():
            if verificar_columna_existe(tabla, campo):
                datos_validos[campo] = valor
            else:
                datos_invalidos[campo] = valor
        
        print(f"✅ Datos válidos para '{tabla}':")
        for campo, valor in datos_validos.items():
            print(f"  - {campo}: {valor}")
        
        if datos_invalidos:
            print(f"\n❌ Datos inválidos (columnas no existen):")
            for campo, valor in datos_invalidos.items():
                print(f"  - {campo}: {valor}")

def ejemplo_helper_supabase():
    """Ejemplo de función helper para operaciones comunes"""
    print("\n🚀 EJEMPLO DE FUNCIÓN HELPER")
    print("=" * 50)
    
    def crear_insert_query(tabla, datos):
        """Crea un query INSERT seguro validando las columnas"""
        columnas_tabla = obtener_columnas_tabla(tabla)
        
        if not columnas_tabla:
            raise ValueError(f"Tabla '{tabla}' no encontrada en esquemas")
        
        # Filtrar solo datos válidos
        datos_validos = {
            campo: valor for campo, valor in datos.items()
            if verificar_columna_existe(tabla, campo)
        }
        
        if not datos_validos:
            raise ValueError("No hay datos válidos para insertar")
        
        columnas = list(datos_validos.keys())
        valores = list(datos_validos.values())
        placeholders = ', '.join(['%s'] * len(valores))
        
        query = f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES ({placeholders})"
        
        return query, valores
    
    # Ejemplo de uso
    try:
        datos_ejemplo = {
            'nombre': 'Cliente Test',
            'telefono': '+52123456789',
            'correo': 'test@example.com'
        }
        
        query, valores = crear_insert_query('contactos', datos_ejemplo)
        print(f"📝 Query generado: {query}")
        print(f"📊 Valores: {valores}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🎯 EJEMPLOS DE USO DE ESQUEMAS SUPABASE")
    print("=" * 60)
    
    ejemplo_uso_basico()
    ejemplo_construccion_queries()
    ejemplo_validacion_datos()
    ejemplo_helper_supabase()
    
    print("\n" + "=" * 60)
    print("✅ Ejemplos completados. ¡Usa estos patrones en tu código!")
