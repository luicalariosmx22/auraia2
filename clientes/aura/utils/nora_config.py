from typing import List, Dict, Any
import logging
from .supabase_client import supabase, get_supabase_client

# Configurar logger
logger = logging.getLogger(__name__)

def get_noras_with_module(modulo_nombre: str) -> List[str]:
    """
    Consulta las instancias de Nora donde un módulo específico está activado.
    
    Args:
        modulo_nombre (str): Nombre del módulo a verificar
        
    Returns:
        List[str]: Lista de nombres de Nora donde el módulo está activo
    """
    try:
        # Obtener cliente de Supabase
        cliente = get_supabase_client()
        
        # Obtener todas las configuraciones de bots
        response = cliente.table("configuracion_bot").select("nombre_nora, modulos").execute()
        
        # Verificar respuesta
        if not hasattr(response, 'data'):
            logger.error("Error al consultar configuración de Nora: Formato de respuesta inesperado")
            return []
            
        # Filtrar noras con el módulo activo
        noras_activas = []
        
        # La respuesta.data es una lista de diccionarios
        for nora in response.data:
            # Verificar que nora sea un diccionario
            if not isinstance(nora, dict):
                logger.warning(f"Formato inesperado en datos de Nora: {type(nora)}")
                continue
                
            # Obtener campo modulos de forma segura
            modulos = nora.get("modulos")
            
            # Si modulos es None o vacío, continuar con la siguiente nora
            if not modulos:
                continue
                
            # Verificar si modulos es una lista (formato antiguo)
            if isinstance(modulos, list):
                # En una lista, el módulo está activo si su nombre aparece en la lista
                if modulo_nombre in modulos:
                    nombre_nora = nora.get("nombre_nora")
                    if nombre_nora:  # Solo añadir si existe
                        noras_activas.append(nombre_nora)
            # Verificar si modulos es un diccionario (formato nuevo)
            elif isinstance(modulos, dict):
                # En un diccionario, el módulo está activo si su valor no es False
                if modulo_nombre in modulos and modulos[modulo_nombre] is not False:
                    nombre_nora = nora.get("nombre_nora")
                    if nombre_nora:  # Solo añadir si existe
                        noras_activas.append(nombre_nora)
            else:
                logger.warning(f"Campo 'modulos' con formato desconocido: {type(modulos)} - {modulos}")
                    
        return noras_activas
        
    except Exception as e:
        logger.error(f"Error al obtener configuración de Nora para módulo '{modulo_nombre}': {str(e)}")
        return []

def is_module_active_in_nora(modulo_nombre: str, nombre_nora: str) -> bool:
    """
    Verifica si un módulo específico está activo en una Nora específica.
    
    Args:
        modulo_nombre (str): Nombre del módulo a verificar
        nombre_nora (str): Nombre de la Nora a consultar
        
    Returns:
        bool: True si el módulo está activo, False en caso contrario
    """
    try:
        # Obtener cliente de Supabase
        cliente = get_supabase_client()
        
        # Consultar configuración específica
        response = cliente.table("configuracion_bot").select("modulos").eq("nombre_nora", nombre_nora).execute()
        
        # Verificar que hay datos en la respuesta
        if not hasattr(response, 'data') or not response.data:
            logger.warning(f"No se encontró configuración para Nora {nombre_nora}")
            return False
            
        # La primera entrada debería contener los datos de la Nora
        if not response.data[0]:
            return False
            
        # Verificar si el módulo está activo según el tipo de datos
        modulos = response.data[0].get("modulos")
        if not modulos:
            return False
            
        # Si es una lista (formato antiguo)
        if isinstance(modulos, list):
            return modulo_nombre in modulos
        # Si es un diccionario (formato nuevo)
        elif isinstance(modulos, dict):
            return modulo_nombre in modulos and modulos[modulo_nombre] is not False
        else:
            logger.warning(f"Campo 'modulos' para Nora {nombre_nora} con formato desconocido: {type(modulos)}")
            return False
            
    except Exception as e:
        logger.error(f"Error al verificar activación de '{modulo_nombre}' en Nora '{nombre_nora}': {str(e)}")
        return False

def get_active_modules_for_nora(nombre_nora: str) -> List[str]:
    """
    Obtiene todos los módulos activos para una Nora específica.
    
    Args:
        nombre_nora (str): Nombre de la Nora a consultar
        
    Returns:
        List[str]: Lista de módulos activos
    """
    try:
        # Obtener cliente de Supabase
        supabase = get_supabase_client()
        
        # Consultar configuración específica
        response = supabase.table("configuracion_bot").select("modulos").eq("nombre_nora", nombre_nora).execute()
        
        # Verificar respuesta
        if hasattr(response, 'error') and response.error:
            logger.error(f"Error al consultar configuración de Nora {nombre_nora}: {response.error}")
            return []
            
        if not response.data or len(response.data) == 0:
            logger.warning(f"No se encontró configuración para Nora {nombre_nora}")
            return []
            
        # Obtener módulos según el formato
        modulos = response.data[0].get("modulos")
        if not modulos:
            return []
            
        # Si es una lista (formato antiguo)
        if isinstance(modulos, list):
            return modulos  # La lista ya contiene los nombres de módulos activos
        # Si es un diccionario (formato nuevo)
        elif isinstance(modulos, dict):
            return [modulo for modulo, estado in modulos.items() if estado is not False]
        else:
            logger.warning(f"Campo 'modulos' para Nora {nombre_nora} con formato desconocido: {type(modulos)}")
            return []
        
    except Exception as e:
        logger.error(f"Error al obtener módulos activos para Nora '{nombre_nora}': {str(e)}")
        return []