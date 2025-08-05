from typing import List, Dict
from flask import current_app
import importlib
import sys
import os
import re

def check_module_paths() -> Dict[str, List[str]]:
    """
    Diagnoses module import issues by checking Python path and module existence.
    Returns dict with valid and invalid module paths.
    """
    results = {
        'valid_modules': [],
        'invalid_modules': []
    }
    
    # Get registered blueprints
    if not hasattr(current_app, 'blueprints'):
        return results
        
    for blueprint_name in current_app.blueprints:
        module_path = current_app.blueprints[blueprint_name].import_name
        
        try:
            # Try importing the module
            importlib.import_module(module_path)
            results['valid_modules'].append(module_path)
        except ImportError:
            results['invalid_modules'].append(module_path)
            
    return results

def get_python_path() -> List[str]:
    """Returns current Python path directories."""
    return sys.path

def validate_file_paths(module_paths: List[str]) -> Dict[str, List[str]]:
    """
    Validates if module files exist in the filesystem.
    Returns dict with existing and missing file paths.
    """
    results = {
        'existing_files': [],
        'missing_files': []
    }
    
    for module_path in module_paths:
        # Convert module path to file path
        file_path = module_path.replace('.', os.path.sep) + '.py'
        
        if os.path.exists(file_path):
            results['existing_files'].append(file_path)
        else:
            results['missing_files'].append(file_path)
            
    return results

def run_diagnostics() -> Dict:
    """
    Runs full diagnostic check on Flask modules.
    Returns comprehensive diagnostic results.
    """
    return {
        'module_status': check_module_paths(),
        'python_path': get_python_path(),
        'file_status': validate_file_paths(
            [m for m in check_module_paths()['invalid_modules']]
        )
    }

def diagnosticar_error_404(contenido: str, nombre: str = "(archivo principal)") -> list[str]:
    """
    Analiza el contenido de un archivo de módulo Flask para diagnosticar posibles causas de error 404.
    
    Args:
        contenido (str): Contenido del archivo Python a analizar
        nombre (str, optional): Nombre del archivo para incluir en los mensajes. 
            Defaults to "(archivo principal)".
        
    Returns:
        list[str]: Lista de posibles causas del error 404
    """
    causas = []

    if "Blueprint(" in contenido and "@blueprint.route" not in contenido:
        causas.append(f"[{nombre}] No se encontró ningún decorador @blueprint.route. Podría faltar la definición de rutas.")

    if "render_template(" not in contenido:
        causas.append(f"[{nombre}] No se encontró render_template(...). El módulo podría no estar mostrando ninguna vista.")

    if not re.search(r"@[\w_]+\.route\(['\"]/?['\"]", contenido):
        causas.append(f"[{nombre}] No se encontró una ruta raíz (@blueprint.route('/')). Puede faltar la vista principal.")

    if "def " not in contenido or "return" not in contenido:
        causas.append(f"[{nombre}] No se encontró una función de vista clara. Podría faltar una función que maneje la ruta.")

    if not causas:
        causas.append(f"[{nombre}] No se detectó una causa clara. Revisa si la ruta esperada coincide con alguna definida.")

    return causas