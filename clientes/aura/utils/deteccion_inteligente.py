# ✅ Archivo: clientes/aura/utils/deteccion_inteligente.py

import re
from typing import Dict, Any

def contiene_blueprint(texto: str, nombre_modulo: str) -> bool:
    """
    Verifica si un módulo está registrado como Blueprint en el código.
    
    Args:
        texto (str): Contenido del archivo a analizar
        nombre_modulo (str): Nombre del módulo a buscar
        
    Returns:
        bool: True si encuentra el patrón del Blueprint
    """
    patrones = [
        # Patrón básico de Blueprint
        rf'Blueprint\(\s*["\']panel_cliente_{nombre_modulo}["\']',
        # Patrón de variable blueprint
        rf'panel_cliente_{nombre_modulo}_bp\s*=\s*Blueprint',
        # Patrón de registro dinámico
        rf'safe_register_blueprint\(.*panel_cliente_{nombre_modulo}'
    ]
    
    return any(re.search(patron, texto, re.MULTILINE) for patron in patrones)

def obtener_rutas_de_blueprint(texto: str) -> list[str]:
    """
    Extrae las rutas definidas en un blueprint de Flask.
    
    Args:
        texto (str): Contenido del archivo a analizar
        
    Returns:
        list[str]: Lista de rutas detectadas sin el prefijo
    """
    rutas = []
    try:
        # Buscar patrones de rutas en decoradores
        coincidencias = re.finditer(r'@[\w_]*\.route\((.*?)\)', texto)
        
        for match in coincidencias:
            ruta_raw = match.group(1)
            try:
                # Limpiar la ruta de decoradores y comillas
                if ruta_raw.strip().startswith(("'", '"')):
                    ruta = eval(ruta_raw.strip())
                else:
                    ruta = ruta_raw.strip()
                
                # Normalizar formato
                ruta = "/" + ruta.lstrip("/")
                rutas.append(ruta)
                
            except Exception as e:
                print(f"⚠️ Error al procesar ruta {ruta_raw}: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Error al extraer rutas: {e}")
        
    return rutas

def esta_registrado_ia(nombre_modulo: str, texto: str) -> Dict[str, Any]:
    """
    Analiza de forma inteligente si un módulo está registrado.
    
    Args:
        nombre_modulo (str): Nombre del módulo a verificar
        texto (str): Contenido del archivo a analizar
        
    Returns:
        dict: Información detallada del registro
    """
    try:
        tiene_blueprint = contiene_blueprint(texto, nombre_modulo)
        
        # Extraer rutas del blueprint
        url_prefix = f"/panel_cliente/{{nombre_nora}}/{nombre_modulo}"
        rutas_detectadas = obtener_rutas_de_blueprint(texto)
        rutas_completas = [url_prefix + ruta for ruta in rutas_detectadas]
        
        # Detectar método de registro
        if f'"{nombre_modulo}" in modulos' in texto:
            metodo = "dinámico"
        elif tiene_blueprint:
            metodo = "directo"
        else:
            metodo = "no encontrado"
            
        # Extraer detalles adicionales
        detalles = {
            "tiene_blueprint": tiene_blueprint,
            "tiene_url_prefix": url_prefix in texto,
            "tiene_import": f"from clientes.aura.routes.panel_cliente_{nombre_modulo}" in texto,
            "rutas_detectadas": rutas_completas
        }
        
        return {
            "registrado": tiene_blueprint,
            "metodo": metodo,
            "detalles": detalles
        }
        
    except Exception as e:
        print(f"❌ Error al analizar registro de {nombre_modulo}: {str(e)}")
        return {
            "registrado": False,
            "metodo": "error",
            "detalles": {"error": str(e)}
        }
