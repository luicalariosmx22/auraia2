import re
from typing import List, Optional
from pathlib import Path
from clientes.aura.logger import logger

def buscar_en_init(modulo_nombre: str, archivo_init_texto: str) -> list:
    """
    Busca menciones de un módulo en el archivo __init__.py.
    
    Args:
        modulo_nombre (str): Nombre del módulo a buscar
        archivo_init_texto (str): Contenido del archivo __init__.py
        
    Returns:
        list: Lista de patrones encontrados en el archivo
    """
    patrones = [
        rf"from clientes\.aura\.routes\.panel_cliente_{modulo_nombre}",  # Import
        rf"from \.panel_cliente_{modulo_nombre}",  # Import relativo
        rf"panel_cliente_{modulo_nombre}_bp",  # Blueprint
        rf"{modulo_nombre}\.blueprint",  # Blueprint por nombre
    ]
    
    encontrados = []
    for patron in patrones:
        if re.search(patron, archivo_init_texto):
            encontrados.append(patron)
            
    return encontrados

def contiene_blueprint(texto: str, nombre_modulo: str) -> bool:
    """
    Verifica si un texto contiene la definición de un blueprint.
    
    Args:
        texto (str): Texto a analizar
        nombre_modulo (str): Nombre del módulo
        
    Returns:
        bool: True si contiene blueprint, False en caso contrario
    """
    patrones = [
        rf"panel_cliente_{nombre_modulo}_bp\s*=\s*Blueprint",  # Definición directa
        rf"Blueprint\(\s*[\"']panel_cliente_{nombre_modulo}[\"']",  # Definición con nombre
    ]
    
    for patron in patrones:
        if re.search(patron, texto):
            return True
            
    return False

def obtener_rutas_de_blueprint(texto: str) -> List[str]:
    """
    Extrae las rutas definidas en un blueprint de un archivo Flask.
    
    Args:
        texto (str): Contenido del archivo a analizar
        
    Returns:
        List[str]: Lista de rutas encontradas
    """
    rutas = []
    
    # Patrón para encontrar decoradores de ruta
    patron_ruta = r'@\w+\.route\([\'"]([^\'"]+)[\'"]\s*(?:,\s*methods=\[[^\]]+\])?\)'
    
    # Buscar todas las coincidencias
    for match in re.finditer(patron_ruta, texto):
        ruta = match.group(1)
        rutas.append(ruta)
        
    return rutas

def extraer_carpeta_backend(modulo_nombre: str) -> Optional[Path]:
    """
    Determina la carpeta backend de un módulo.
    
    Args:
        modulo_nombre (str): Nombre del módulo
        
    Returns:
        Optional[Path]: Ruta a la carpeta backend o None
    """
    # Caso 1: carpeta como paquete Python
    carpeta_modulo = Path(f"clientes/aura/routes/panel_cliente_{modulo_nombre}")
    if carpeta_modulo.exists() and carpeta_modulo.is_dir():
        init_file = carpeta_modulo / "__init__.py"
        if init_file.exists():
            logger.debug(f"Módulo {modulo_nombre} encontrado como paquete en {carpeta_modulo}")
            return carpeta_modulo

    # Caso 2: archivo suelto tradicional
    archivo_suelto = Path(f"clientes/aura/routes/panel_cliente_{modulo_nombre}.py")
    if archivo_suelto.exists():
        logger.debug(f"Módulo {modulo_nombre} encontrado como archivo único en {archivo_suelto.parent}")
        return archivo_suelto.parent

    logger.warning(f"No se encontró carpeta backend para el módulo {modulo_nombre}")
    return None

def extraer_carpeta_templates(modulo_nombre: str) -> Optional[Path]:
    """
    Determina la carpeta de templates de un módulo.
    
    Args:
        modulo_nombre (str): Nombre del módulo
        
    Returns:
        Optional[Path]: Ruta a la carpeta de templates o None
    """
    # Primera opción: en la carpeta del módulo
    path_1 = Path(f"clientes/aura/routes/panel_cliente_{modulo_nombre}/templates")
    if path_1.exists() and path_1.is_dir():
        return path_1
        
    # Segunda opción: en templates general
    path_2 = Path(f"clientes/aura/templates/{modulo_nombre}")
    if path_2.exists() and path_2.is_dir():
        return path_2
        
    return None

def obtener_contenido_archivo(path_archivo: str) -> dict:
    """
    Obtiene el contenido de un archivo de forma segura.
    
    Args:
        path_archivo (str): Ruta del archivo a leer
        
    Returns:
        dict: Diccionario con el contenido o información de error
    """
    try:
        with open(path_archivo, "r", encoding="utf-8", errors="replace") as f:
            contenido = f.read()
        
        return {
            "ok": True,
            "contenido": contenido,
            "error": None
        }
    except FileNotFoundError:
        logger.error(f"❌ Error al obtener archivo principal: Archivo no encontrado - {path_archivo}")
        return {
            "ok": False,
            "contenido": None,
            "error": "❌ Error al obtener archivo principal: Archivo no encontrado"
        }
    except Exception as e:
        logger.error(f"❌ Error al leer archivo {path_archivo}: {str(e)}")
        return {
            "ok": False,
            "contenido": None,
            "error": f"❌ Error al leer archivo: {str(e)}"
        }