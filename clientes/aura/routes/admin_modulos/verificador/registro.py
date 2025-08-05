import re
from typing import Dict, Any, Union, List, Optional

def modulo_parece_registrado(nombre_modulo: str, contenido: str) -> dict:
    """
    Evalúa con heurística AI-like si un módulo parece estar registrado dinámicamente.
    
    Args:
        nombre_modulo (str): Nombre del módulo a verificar
        contenido (str): Contenido del archivo a analizar
        
    Returns:
        dict: Resultado del análisis heurístico con detalle de coincidencias
    """
    patrones_positivos = [
        # Declaración de inclusión en modulos
        rf'\bif\s+["\'{nombre_modulo}\'"]\s+in\s+modulos\b',
        
        # Import del blueprint
        rf'from .*panel_cliente_{nombre_modulo}\s+import',
        
        # Registro del blueprint
        rf'safe_register_blueprint\(.*?,\s*panel_cliente_{nombre_modulo}_bp',
        
        # URL prefix dinámico
        rf'url_prefix\s*=\s*f?["\'/panel_cliente/{{.*?}}/{nombre_modulo}["\']',
        
        # Patrones adicionales de registro
        rf'register_blueprint\(panel_cliente_{nombre_modulo}_bp\)',
        rf'Blueprint\(["\']panel_cliente_{nombre_modulo}["\']\)'
    ]
    
    patrones_negativos = [
        # Módulo explícitamente desactivado
        rf'pass\s*#\s*{nombre_modulo}\s+desactivado',
        rf'#\s*{nombre_modulo}\s+temporalmente\s+desactivado',
        
        # Errores o excepciones relacionadas
        rf'raise\s+ImportError.*{nombre_modulo}',
        rf'except.*{nombre_modulo}.*?pass',
        
        # Comentarios de problemas
        rf'#.*(?:error|falla|bug).*{nombre_modulo}'
    ]
    
    # Contar coincidencias
    positivos = sum(bool(re.search(p, contenido, re.IGNORECASE | re.MULTILINE)) for p in patrones_positivos)
    negativos = sum(bool(re.search(p, contenido, re.IGNORECASE | re.MULTILINE)) for p in patrones_negativos)
    
    # Evaluar resultado
    nivel_confianza = "alto" if positivos >= 3 else "medio" if positivos >= 2 else "bajo"
    parece_registrado = positivos > 0 and negativos == 0
    
    return {
        "parece_registrado": parece_registrado,
        "nivel_confianza": nivel_confianza,
        "coincidencias": {
            "positivas": positivos,
            "negativas": negativos
        },
        "detalle": f"{positivos} coincidencias positivas, {negativos} negativas",
        "sugerencia": None if parece_registrado else "Considerar agregar registro dinámico"
    }

def modulo_esta_registrado_dinamicamente(nombre_modulo: str, contenido_registro: str) -> dict:
    """
    Verifica de forma robusta si un módulo está registrado en registro_dinamico.py.
    
    Args:
        nombre_modulo (str): Nombre del módulo a verificar
        contenido_registro (str): Contenido del archivo registro_dinamico.py
        
    Returns:
        dict: Resultados detallados de la verificación
    """
    resultados = {
        "registrado": False,
        "detalles": {
            "mencionado_como_string": False,
            "import_presente": False, 
            "url_prefix_correcto": False,
            "blueprint_registrado": False
        }
    }
    
    # 1. Verifica si se menciona el nombre como string
    if re.search(rf"[\"']{nombre_modulo}[\"']", contenido_registro):
        resultados["detalles"]["mencionado_como_string"] = True
    
    # 2. Verifica si está el import correcto - Versión mejorada para detectar imports multilinea
    patron_import = rf"from\s+clientes\.aura\.routes\.panel_cliente_{nombre_modulo}.*?import"
    if re.search(patron_import, contenido_registro, re.DOTALL):
        resultados["detalles"]["import_presente"] = True
        
    # 3. Verifica si tiene el url_prefix correcto - Versión mejorada
    # Busca tanto el formato directo como el que está en líneas diferentes o dentro de bloques try/except
    patrones_url = [
        # Formato estándar - Versión más flexible
        rf"url_prefix\s*=\s*f?[\"\']/panel_cliente/.+/{nombre_modulo}[\"\']",
        
        # Formato con string separado por líneas
        rf"url_prefix=f[\"\']\/panel_cliente\/{{.*?}}\/\s*{nombre_modulo}[\"\']",
        
        # Formato con f-string directo
        rf"url_prefix=f?[\"\']\/panel_cliente\/.*?\/{nombre_modulo}[\"\']",
        
        # Formato usando registrar_modulo - Versión mejorada con más flexibilidad
        rf"registrar_modulo\(\s*app\s*,\s*[\"\']?{nombre_modulo}[\"\']?,.*?,\s*f?[\"\']\/panel_cliente\/{{.*?}}\/{nombre_modulo}[\"\']",
        
        # Formato usando registrar_modulo con espacios - Nueva detección
        rf"registrar_modulo\(\s*app\s*,\s*[\"\']{nombre_modulo}[\"\']"
    ]
    
    for patron in patrones_url:
        if re.search(patron, contenido_registro, re.MULTILINE | re.DOTALL):
            resultados["detalles"]["url_prefix_correcto"] = True
            break
    
    # 4. Verifica si el blueprint está siendo registrado - Versión mejorada
    patrones_blueprint = [
        # Registro directo del blueprint
        rf"safe_register_blueprint\(.*panel_cliente_{nombre_modulo}_bp",
        
        # Registro usando registrar_modulo - Versión mejorada con espacios opcionales
        rf"registrar_modulo\(\s*app\s*,\s*[\"\']?{nombre_modulo}[\"\']?,\s*panel_cliente_{nombre_modulo}_bp",
        
        # Registro con imports y blueprint en distintos lugares
        rf"(panel_cliente_{nombre_modulo}_bp.*?safe_register_blueprint|safe_register_blueprint.*?panel_cliente_{nombre_modulo}_bp)"
    ]
    
    for patron in patrones_blueprint:
        if re.search(patron, contenido_registro, re.MULTILINE | re.DOTALL):
            resultados["detalles"]["blueprint_registrado"] = True
            break
    
    # Verificación alternativa: safe_register_blueprint con url_prefix específico
    patron_safe_register = rf"safe_register_blueprint\(.*?,.*?,\s*url_prefix\s*=\s*f?[\"']/panel_cliente/.+/{nombre_modulo}[\"']"
    if not resultados["detalles"]["blueprint_registrado"] and re.search(patron_safe_register, contenido_registro):
        resultados["detalles"]["blueprint_registrado"] = True
    
    # Patrón combinado de URL y blueprint en diferentes líneas
    patron_combinado = rf"""
    # Busca cualquiera de estas combinaciones en un contexto de 10 líneas:
    (
        # 1. Blueprint seguido de URL
        panel_cliente_{nombre_modulo}_bp.+?url_prefix.+?{nombre_modulo}|
        # 2. URL seguida de blueprint
        url_prefix.+?{nombre_modulo}.+?panel_cliente_{nombre_modulo}_bp|
        # 3. Blueprint y URL con safe_register_blueprint
        safe_register_blueprint.+?panel_cliente_{nombre_modulo}_bp.+?url_prefix.+?{nombre_modulo}|
        # 4. URL y blueprint con safe_register_blueprint
        safe_register_blueprint.+?url_prefix.+?{nombre_modulo}.+?panel_cliente_{nombre_modulo}_bp
    )
    """
    
    if re.search(patron_combinado, contenido_registro, re.VERBOSE | re.MULTILINE | re.DOTALL):
        resultados["detalles"]["blueprint_registrado"] = True
        resultados["detalles"]["url_prefix_correcto"] = True
    
    # Determinar si está registrado basado en los criterios
    resultados["registrado"] = (
        resultados["detalles"]["mencionado_como_string"] and 
        (resultados["detalles"]["import_presente"] or resultados["detalles"]["blueprint_registrado"]) and
        resultados["detalles"]["url_prefix_correcto"]
    )
    
    # Añadir diagnóstico si hay problemas
    if not resultados["registrado"]:
        resultados["diagnostico"] = []
        if not resultados["detalles"]["mencionado_como_string"]:
            resultados["diagnostico"].append("⚠️ El módulo no está incluido en la lista de módulos")
        if not resultados["detalles"]["import_presente"]:
            resultados["diagnostico"].append("⚠️ Falta el import del blueprint")
        if not resultados["detalles"]["url_prefix_correcto"]:
            resultados["diagnostico"].append("⚠️ El url_prefix no está configurado correctamente")
        if not resultados["detalles"]["blueprint_registrado"]:
            resultados["diagnostico"].append("⚠️ No se detectó el registro del blueprint")
    
    return resultados

def buscar_en_registro_dinamico(nombre_modulo: str) -> dict:
    """
    Verifica si un módulo está registrado en registro_dinamico.py.
    
    Args:
        nombre_modulo (str): Nombre del módulo a verificar
        
    Returns:
        dict: Información detallada del registro
    """
    try:
        with open("clientes/aura/registro/registro_dinamico.py", "r", encoding="utf-8") as f:
            contenido_registro = f.read()
            
        resultado = modulo_esta_registrado_dinamicamente(nombre_modulo, contenido_registro)
        
        # Si no está registrado, generar sugerencia
        if not resultado["registrado"]:
            sugerencia = sugerencia_registro_dinamico(nombre_modulo)
            if sugerencia:
                resultado["sugerencia"] = sugerencia
                
        return resultado
        
    except Exception as e:
        print(f"❌ Error al verificar registro_dinamico.py: {str(e)}")
        return {
            "registrado": False,
            "error": str(e),
            "detalles": {"error": str(e)}
        }

def sugerencia_registro_dinamico(nombre_modulo: str) -> str:
    """
    Genera una sugerencia de código para agregar un módulo a registro_dinamico.py.
    
    Args:
        nombre_modulo (str): Nombre del módulo
        
    Returns:
        str: Código sugerido para agregar al registro dinámico
    """
    return f"""# Registro para módulo {nombre_modulo}
try:
    from clientes.aura.routes.panel_cliente_{nombre_modulo} import panel_cliente_{nombre_modulo}_bp
    if "{nombre_modulo}" in modulos:
        safe_register_blueprint(
            app, 
            panel_cliente_{nombre_modulo}_bp, 
            url_prefix=f"/panel_cliente/{{nombre_nora}}/{nombre_modulo}"
        )
        print(f"✅ Módulo {nombre_modulo} cargado para {{nombre_nora}}")
except ImportError:
    # Ignorar si el módulo no está disponible
    pass
"""