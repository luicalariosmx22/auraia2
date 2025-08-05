from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.openai_client import generar_respuesta
import logging
from pathlib import Path
import re
import ast
import inspect
import importlib.util
import sys
from collections import Counter
import time
import hashlib
import os
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Crear blueprint
registro_dinamico_frontend_bp = Blueprint(
    'registro_dinamico_frontend', 
    __name__, 
    template_folder='templates',
    static_folder='static',
    url_prefix='/admin/registro_dinamico'
)

# Caché de análisis para evitar recálculos frecuentes
_cache_analisis = {
    "timestamp": 0,
    "datos": None,
    "tiempo_vida": 300  # 5 minutos de caché
}

# Caché para análisis de IA (para evitar múltiples llamadas a la API)
_cache_analisis_ia = {
    "timestamp": 0,
    "datos": {},
    "tiempo_vida": 86400  # 24 horas (este análisis consume tokens de la API)
}

def obtener_analisis_con_cache():
    """
    Obtiene el análisis del registro dinámico, usando caché si está disponible y vigente.
    
    Returns:
        dict: Resultado del análisis
    """
    global _cache_analisis
    
    ahora = time.time()
    if _cache_analisis["datos"] is None or (ahora - _cache_analisis["timestamp"]) > _cache_analisis["tiempo_vida"]:
        logger.info("Generando nuevo análisis del registro dinámico (caché expirado o no existente)")
        _cache_analisis["datos"] = analizar_registro_dinamico_global()
        _cache_analisis["timestamp"] = ahora
        
        # Verificar problemas críticos que requieran notificación
        try:
            notificar_problemas_criticos(_cache_analisis["datos"])
        except Exception as e:
            logger.error(f"Error al notificar problemas críticos: {str(e)}")
    else:
        logger.debug("Usando análisis en caché (edad: {:.1f} segundos)".format(ahora - _cache_analisis["timestamp"]))
    
    return _cache_analisis["datos"]

@registro_dinamico_frontend_bp.route('/')
def index():
    """Vista principal del análisis global del registro dinámico."""
    try:
        # Usar la versión en caché
        registro_info = obtener_analisis_con_cache()
        
        # Verificar si hay error y proporcionar una estructura compatible
        if "error" in registro_info and not "estructura_global" in registro_info:
            # Crear estructura base para evitar errores en la plantilla
            registro_info["estructura_global"] = {
                "total_modulos": 0,
                "modulos_complejos": 0,
                "modulos_simples": 0,
                "nivel_salud_codigo": "desconocido",
                "puntuacion_seguridad_promedio": 0,
                "puntuacion_calidad_promedio": 0,
                "total_riesgos_seguridad": 0,
                "total_problemas_calidad": 0,
                "patrones_registro": {}
            }
            registro_info["modulos"] = []
            registro_info["recomendaciones"] = []
            registro_info["grafo_dependencias"] = {"grafo": {}, "modulos_acoplados": 0, "porcentaje_acoplamiento": 0}
            registro_info["metricas_globales"] = {}
            
            # Registrar el error para diagnóstico
            logger.error(f"Se encontró un error al analizar: {registro_info['error']}")
            flash(f"Error al analizar registro dinámico: {registro_info['error']}", "danger")
        
        # Usar la plantilla index.html existente
        # Asegurarse de que la lista de módulos siempre esté presente
        modulos = registro_info.get("modulos", [])
        return render_template(
            'admin_modulos/registro_dinamico/index.html',
            registro_info=registro_info,
            modulos=modulos
        )
    
    except Exception as e:
        logger.error(f"Error al cargar análisis del registro dinámico: {str(e)}")
        flash(f"Ha ocurrido un error: {str(e)}", "danger")
        
        # Crear estructura base para la plantilla
        registro_info = {
            "error": str(e),
            "estructura_global": {
                "total_modulos": 0,
                "modulos_complejos": 0,
                "modulos_simples": 0,
                "nivel_salud_codigo": "desconocido",
                "puntuacion_seguridad_promedio": 0,
                "puntuacion_calidad_promedio": 0,
                "total_riesgos_seguridad": 0,
                "total_problemas_calidad": 0,
                "patrones_registro": {}
            },
            "modulos": [],
            "recomendaciones": [],
            "grafo_dependencias": {"grafo": {}, "modulos_acoplados": 0, "porcentaje_acoplamiento": 0},
            "metricas_globales": {}
        }
        
        return render_template('admin_modulos/registro_dinamico/index.html', 
                               registro_info=registro_info)

@registro_dinamico_frontend_bp.route('/modulo/<nombre_modulo>')
def ver_modulo(nombre_modulo):
    """Vista detallada de un módulo específico."""
    try:
        # Usar la versión en caché
        registro_info = obtener_analisis_con_cache()
        
        # Buscar el módulo específico
        modulo_info = None
        for modulo in registro_info.get("modulos", []):
            if modulo["nombre"] == nombre_modulo:
                modulo_info = modulo
                break
        
        if not modulo_info:
            flash(f"No se encontró información para el módulo {nombre_modulo}", "warning")
            return redirect(url_for('registro_dinamico_frontend.index'))
        
        # Obtener estadísticas de uso del módulo por Noras
        noras_con_modulo = obtener_noras_con_modulo(nombre_modulo)
        
        # Cambiamos la ruta de la plantilla a la existente
        return render_template(
            'admin_modulos/registro_dinamico/detalle.html',  # Cambiado de detalle_modulo.html
            modulo_info=modulo_info,
            noras=noras_con_modulo
        )
    
    except Exception as e:
        logger.error(f"Error al cargar información del módulo {nombre_modulo}: {str(e)}")
        flash(f"Ha ocurrido un error: {str(e)}", "danger")
        return redirect(url_for('registro_dinamico_frontend.index'))

@registro_dinamico_frontend_bp.route('/api/registro_codigo')
def api_registro_codigo():
    """API para obtener el código del archivo registro_dinamico.py."""
    try:
        registro_path = Path("clientes/aura/registro/registro_dinamico.py")
        if not registro_path.exists():
            return jsonify({"error": "No se encontró el archivo de registro dinámico"})
            
        with open(registro_path, "r", encoding="utf-8") as f:
            contenido = f.read()
            
        return jsonify({"codigo": contenido})
    except Exception as e:
        logger.error(f"Error al obtener código de registro_dinamico.py: {str(e)}")
        return jsonify({"error": str(e)}), 500

@registro_dinamico_frontend_bp.route('/api/modulos')
def api_modulos():
    """API para obtener información de todos los módulos registrados."""
    try:
        # Usar la versión en caché
        registro_info = obtener_analisis_con_cache()
        return jsonify(registro_info)
    except Exception as e:
        logger.error(f"Error en API de módulos: {str(e)}")
        return jsonify({"error": str(e)}), 500

@registro_dinamico_frontend_bp.route('/api/actualizar_analisis', methods=['POST'])
def api_actualizar_analisis():
    """API para forzar la actualización del análisis del registro dinámico."""
    try:
        global _cache_analisis
        # Forzar nuevo análisis
        _cache_analisis["datos"] = None
        registro_info = obtener_analisis_con_cache()
        
        return jsonify({
            "estado": "actualizado",
            "timestamp": _cache_analisis["timestamp"],
            "modulos_analizados": registro_info["estructura_global"]["total_modulos"]
        })
    except Exception as e:
        logger.error(f"Error al actualizar análisis: {str(e)}")
        return jsonify({"error": str(e)}), 500

@registro_dinamico_frontend_bp.route('/api/exportar')
def api_exportar():
    """API para exportar el análisis completo en formato JSON."""
    try:
        import json
        from flask import Response
        
        registro_info = obtener_analisis_con_cache()
        
        # Generar timestamp para el nombre del archivo
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        
        # Preparar respuesta como archivo descargable
        response = Response(
            json.dumps(registro_info, indent=2, ensure_ascii=False),
            mimetype="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=analisis_registro_dinamico_{timestamp}.json"
            }
        )
        
        return response
    except Exception as e:
        logger.error(f"Error al exportar análisis: {str(e)}")
        return jsonify({"error": str(e)}), 500

def analizar_registro_dinamico_global():
    """
    Analiza el archivo registro_dinamico.py para obtener información completa sobre todos los módulos registrados.
    Utiliza técnicas avanzadas de análisis para identificar patrones en el código y evaluar su calidad.
    
    Returns:
        dict: Información global sobre los módulos registrados, estructura, métricas de calidad y alertas
    """
    # Estructura base para garantizar consistencia
    resultado_base = {
        "modulos": [],
        "estructura_global": {
            "total_modulos": 0,
            "modulos_complejos": 0,
            "modulos_simples": 0,
            "nivel_salud_codigo": "desconocido",
            "puntuacion_seguridad_promedio": 0,
            "puntuacion_calidad_promedio": 0,
            "total_riesgos_seguridad": 0,
            "total_problemas_calidad": 0,
            "patrones_registro": {}
        },
        "recomendaciones": [],
        "grafo_dependencias": {"grafo": {}, "modulos_acoplados": 0, "porcentaje_acoplamiento": 0},
        "metricas_globales": {}
    }
    
    try:
        # Cargar el módulo de registro dinámico para analizar
        registro_path = Path("clientes/aura/registro/registro_dinamico.py")
        if not registro_path.exists():
            return {"error": "No se encontró el archivo de registro dinámico"}
            
        # Leer el contenido del archivo
        with open(registro_path, "r", encoding="utf-8") as f:
            contenido = f.read()
        
        # Análisis del AST (Abstract Syntax Tree) para evaluación profunda
        try:
            modulo_ast = ast.parse(contenido)
            metricas_ast = analizar_ast(modulo_ast)
        except Exception as e:
            logger.warning(f"No se pudo analizar el AST: {str(e)}")
            metricas_ast = {}
            
        # Análisis de patrones con expresiones regulares
        modulos_info = []

        # 1. Buscar patrones de registro de módulos
        modulos_patrones = re.findall(r'if\s+[\'"]([^\'"]+)[\'"]\s+in\s+modulos', contenido)

        # 1.1 Obtener módulos válidos desde Supabase
        response = supabase.table("modulos_disponibles").select("nombre").execute()
        modulos_supabase = set(m["nombre"] for m in response.data) if response.data else set()

        # 2. Extraer información detallada solo de módulos que estén en Supabase
        for modulo in modulos_patrones:
            if modulo not in modulos_supabase:
                continue  # Ignorar módulos que no están en la base
            # Buscar el bloque completo asociado a este módulo
            patron_bloque = fr'if\s+[\'"]({modulo})[\'"]\s+in\s+modulos.*?(?=if\s+[\'"]\w+[\'"]\s+in\s+modulos|$)'
            bloque_match = re.search(patron_bloque, contenido, re.DOTALL)

            if bloque_match:
                bloque = bloque_match.group(0)

                # Análisis básico del bloque
                analisis_basico = analizar_bloque_basico(bloque, modulo)

                # Análisis avanzado de seguridad y rendimiento
                analisis_seguridad = analizar_seguridad_bloque(bloque)

                # Análisis de calidad de código
                analisis_calidad = analizar_calidad_codigo(bloque)

                # Combinar todos los análisis
                info_modulo = {
                    "nombre": modulo,
                    **analisis_basico,
                    "metricas_seguridad": analisis_seguridad,
                    "metricas_calidad": analisis_calidad
                }

                modulos_info.append(info_modulo)
        
        # Eliminar módulos duplicados por nombre antes de devolver resultados
        modulos_filtrados = {}
        for modulo in modulos_info:
            nombre = modulo["nombre"]
            if nombre not in modulos_filtrados:
                modulos_filtrados[nombre] = modulo
        modulos_info = list(modulos_filtrados.values())
        
        # 3. Analizar estructura global del registro
        estructura_global = generar_estructura_global(modulos_info)
        
        # 4. Análisis avanzado: detección de antipatrones y mejores prácticas
        recomendaciones = generar_recomendaciones(modulos_info, contenido, metricas_ast)
        
        # 5. Análisis de dependencias entre módulos
        grafo_dependencias = analizar_dependencias_modulos(modulos_info, contenido)
            
        return {
            "modulos": modulos_info,
            "estructura_global": estructura_global,
            "recomendaciones": recomendaciones,
            "grafo_dependencias": grafo_dependencias,
            "metricas_globales": metricas_ast
        }
    
    except Exception as e:
        logger.error(f"Error al analizar registro dinámico: {str(e)}")
        resultado_base["error"] = str(e)
        return resultado_base

def analizar_bloque_basico(bloque, modulo):
    """
    Realiza un análisis básico de un bloque de código de un módulo.
    
    Args:
        bloque (str): Bloque de código a analizar
        modulo (str): Nombre del módulo
        
    Returns:
        dict: Información básica extraída del bloque
    """
    # Analizar estructura del registro
    urls = re.findall(r'url_prefix=f[\'"]([^\'"]+)[\'"]', bloque)
    blueprints = re.findall(r'safe_register_blueprint\(app,\s+(\w+)', bloque)
    
    # Buscar importaciones relacionadas en todo el archivo
    patron_import = re.findall(fr'from\s+[\w.]+\.{modulo}\s+import\s+([\w_,\s]+)', bloque)
    imports = []
    if patron_import:
        for imp in patron_import:
            imports.extend([i.strip() for i in imp.split(',')])
    
    # Buscar parámetros de registro
    parametros = re.findall(r'url_prefix=f[\'"][^\'"]+"[,\)]', bloque)
    parametros.extend(re.findall(r'template_folder=[\'"][^\'"]+[\'"]', bloque))
    
    # Buscar variables específicas del módulo
    variables = re.findall(rf'{modulo}_\w+\s*=', bloque)
    
    # Evaluar complejidad del registro
    complejidad = len(bloque.split('\n'))
    
    return {
        "urls": urls,
        "blueprints": blueprints,
        "imports": imports,
        "parametros": parametros,
        "variables": variables,
        "complejidad": complejidad,
        "lineas_codigo": complejidad,
        "tiene_condiciones": "if" in bloque.split("if")[0],
        "tiene_excepciones": "try" in bloque,
        "patron_registro": determinar_patron_registro(bloque)
    }

def analizar_seguridad_bloque(bloque):
    """
    Analiza aspectos de seguridad en un bloque de código.
    
    Args:
        bloque (str): Bloque de código a analizar
        
    Returns:
        dict: Métricas de seguridad y riesgos detectados
    """
    resultados = {
        "riesgos_detectados": [],
        "nivel_riesgo": "bajo",
        "puntuacion_seguridad": 100
    }
    
    # Si se llama a registrar_modulo, se asume manejo seguro
    if "registrar_modulo(" in bloque:
        return resultados  # Seguridad perfecta, no evaluar más
    
    # Detectar problemas de seguridad comunes
    patrones_riesgo = [
        ("Credenciales hardcodeadas", r'(password|api_key|token|secret)\s*=\s*["\'][^"\']+["\']', 50),
        ("Uso de eval", r'eval\(', 70),
        ("Acceso a sistema de archivos sin validación", r'open\([^,]+(,\s*[\'"]w[\'"]\s*\))', 40),
        ("Variables no validadas en URL", r'url_prefix\s*=\s*f[\'"][^\'"]*{\s*[^}]*}', 30),
        ("Uso de rutas absolutas", r'[\'"]\/[^\'"]*[\'"]', 20)
    ]
    
    for nombre, patron, severidad in patrones_riesgo:
        if re.search(patron, bloque):
            resultados["riesgos_detectados"].append({
                "tipo": nombre,
                "severidad": severidad,
                "descripcion": f"Se detectó {nombre.lower()} en el código"
            })
            resultados["puntuacion_seguridad"] -= severidad/10
    
    # Ajustar puntuación al rango válido
    resultados["puntuacion_seguridad"] = max(0, min(100, resultados["puntuacion_seguridad"]))
    
    # Determinar nivel de riesgo
    if resultados["puntuacion_seguridad"] < 60:
        resultados["nivel_riesgo"] = "alto"
    elif resultados["puntuacion_seguridad"] < 85:
        resultados["nivel_riesgo"] = "medio"
    
    return resultados

def analizar_calidad_codigo(bloque):
    """
    Analiza la calidad del código en términos de mantenibilidad, claridad y buenas prácticas.
    
    Args:
        bloque (str): Bloque de código a analizar
        
    Returns:
        dict: Métricas de calidad y recomendaciones
    """
    resultados = {
        "puntuacion_calidad": 100,
        "problemas_detectados": [],
        "nivel_mantenibilidad": "bueno"
    }
    
    # Calcular longitud promedio de línea
    lineas = [linea for linea in bloque.split('\n') if linea.strip()]
    longitud_promedio = sum(len(linea) for linea in lineas) / len(lineas) if lineas else 0
    
    # Detectar problemas de calidad comunes
    problemas_calidad = []
    
    if longitud_promedio > 100:
        problemas_calidad.append({
            "tipo": "legibilidad",
            "mensaje": f"Líneas demasiado largas (promedio {longitud_promedio:.1f} caracteres)",
            "impacto": 10
        })
    
    # Detectar código comentado
    lineas_comentadas = len(re.findall(r'^\s*#\s*[^\n]+$', bloque, re.MULTILINE))
    if lineas_comentadas > 5:
        problemas_calidad.append({
            "tipo": "mantenibilidad",
            "mensaje": f"{lineas_comentadas} líneas comentadas pueden indicar código obsoleto",
            "impacto": 5
        })
    
    # Detectar complejidad excesiva
    if len(lineas) > 30:
        problemas_calidad.append({
            "tipo": "complejidad",
            "mensaje": f"Bloque demasiado largo ({len(lineas)} líneas)",
            "impacto": 15
        })
    
    # Contar cantidad de declaraciones anidadas
    nivel_anidamiento = max([len(re.findall(r'^\s+', linea)) // 4 for linea in lineas]) if lineas else 0
    if nivel_anidamiento > 3:
        problemas_calidad.append({
            "tipo": "complejidad",
            "mensaje": f"Nivel de anidamiento excesivo ({nivel_anidamiento} niveles)",
            "impacto": 20
        })
    
    # Actualizar puntuación
    for problema in problemas_calidad:
        resultados["puntuacion_calidad"] -= problema["impacto"]
        resultados["problemas_detectados"].append(problema)
    
    # Ajustar puntuación al rango válido
    resultados["puntuacion_calidad"] = max(0, min(100, resultados["puntuacion_calidad"]))
    
    # Determinar nivel de mantenibilidad
    if resultados["puntuacion_calidad"] < 60:
        resultados["nivel_mantenibilidad"] = "deficiente"
    elif resultados["puntuacion_calidad"] < 85:
        resultados["nivel_mantenibilidad"] = "regular"
    
    return resultados

def analizar_ast(modulo_ast):
    """
    Analiza el AST (Abstract Syntax Tree) del módulo para obtener métricas avanzadas.
    
    Args:
        modulo_ast: AST del módulo a analizar
        
    Returns:
        dict: Métricas extraídas del AST
    """
    metricas = {
        "funciones": 0,
        "imports": 0,
        "clases": 0,
        "llamadas_funciones": 0,
        "complejidad_ciclomatica": 0
    }
    
    # Contar elementos
    for nodo in ast.walk(modulo_ast):
        if isinstance(nodo, ast.FunctionDef):
            metricas["funciones"] += 1
            
            # Calcular complejidad ciclomática por función
            cc = 1  # Valor base
            for sub_nodo in ast.walk(nodo):
                if isinstance(sub_nodo, (ast.If, ast.For, ast.While, ast.Try)):
                    cc += 1
            metricas["complejidad_ciclomatica"] += cc
            
        elif isinstance(nodo, ast.Import) or isinstance(nodo, ast.ImportFrom):
            metricas["imports"] += 1
        elif isinstance(nodo, ast.ClassDef):
            metricas["clases"] += 1
        elif isinstance(nodo, ast.Call):
            metricas["llamadas_funciones"] += 1
    
    # Calcular promedios
    if metricas["funciones"] > 0:
        metricas["complejidad_promedio"] = metricas["complejidad_ciclomatica"] / metricas["funciones"]
    else:
        metricas["complejidad_promedio"] = 0
    
    return metricas

def generar_estructura_global(modulos_info):
    """
    Genera métricas globales a partir de la información de todos los módulos.
    
    Args:
        modulos_info (list): Lista de información de módulos
        
    Returns:
        dict: Estructura global con métricas consolidadas
    """
    # Métricas básicas
    estructura_global = {
        "total_modulos": len(modulos_info),
        "modulos_complejos": len([m for m in modulos_info if m["complejidad"] > 10]),
        "modulos_simples": len([m for m in modulos_info if m["complejidad"] <= 10]),
        "blueprint_mas_usado": obtener_mas_comun([bp for m in modulos_info for bp in m["blueprints"]]),
        "patron_url_comun": obtener_patron_url_comun([url for m in modulos_info for url in m["urls"]]),
        "imports_comunes": obtener_imports_comunes([imp for m in modulos_info for imp in m.get("imports", [])]),
        "patrones_registro": contar_ocurrencias([m["patron_registro"] for m in modulos_info])
    }
    
    # Métricas de seguridad y calidad
    riesgos_seguridad = [riesgo for m in modulos_info 
                        for riesgo in m.get("metricas_seguridad", {}).get("riesgos_detectados", [])]
    
    problemas_calidad = [problema for m in modulos_info 
                        for problema in m.get("metricas_calidad", {}).get("problemas_detectados", [])]
    
    # Calcular puntuaciones promedio
    puntuaciones_seguridad = [m.get("metricas_seguridad", {}).get("puntuacion_seguridad", 100) 
                            for m in modulos_info if "metricas_seguridad" in m]
    
    puntuaciones_calidad = [m.get("metricas_calidad", {}).get("puntuacion_calidad", 100) 
                          for m in modulos_info if "metricas_calidad" in m]
    
    # Añadir métricas de seguridad y calidad a la estructura global
    estructura_global.update({
        "total_riesgos_seguridad": len(riesgos_seguridad),
        "total_problemas_calidad": len(problemas_calidad),
        "puntuacion_seguridad_promedio": sum(puntuaciones_seguridad) / len(puntuaciones_seguridad) if puntuaciones_seguridad else 100,
        "puntuacion_calidad_promedio": sum(puntuaciones_calidad) / len(puntuaciones_calidad) if puntuaciones_calidad else 100,
        "nivel_salud_codigo": calcular_nivel_salud(puntuaciones_seguridad, puntuaciones_calidad)
    })
    
    return estructura_global

def calcular_nivel_salud(puntuaciones_seguridad, puntuaciones_calidad):
    """
    Calcula el nivel de salud general del código basado en métricas de seguridad y calidad.
    
    Args:
        puntuaciones_seguridad (list): Lista de puntuaciones de seguridad
        puntuaciones_calidad (list): Lista de puntuaciones de calidad
        
    Returns:
        str: Nivel de salud del código
    """
    if not puntuaciones_seguridad or not puntuaciones_calidad:
        return "desconocido"
    
    promedio_seguridad = sum(puntuaciones_seguridad) / len(puntuaciones_seguridad)
    promedio_calidad = sum(puntuaciones_calidad) / len(puntuaciones_calidad)
    
    # Ponderación: seguridad 60%, calidad 40%
    puntuacion_salud = (promedio_seguridad * 0.6) + (promedio_calidad * 0.4)
    
    if puntuacion_salud >= 90:
        return "excelente"
    elif puntuacion_salud >= 80:
        return "bueno"
    elif puntuacion_salud >= 70:
        return "aceptable"
    elif puntuacion_salud >= 60:
        return "necesita mejoras"
    else:
        return "crítico"

def generar_recomendaciones(modulos_info, contenido_completo, metricas_ast):
    """
    Genera recomendaciones basadas en el análisis de los módulos y el código completo.
    
    Args:
        modulos_info (list): Lista de información de módulos
        contenido_completo (str): Contenido completo del archivo
        metricas_ast (dict): Métricas del AST
        
    Returns:
        list: Lista de recomendaciones con tipo, mensaje e impacto
    """
    recomendaciones = []
    
    # 1. Recomendaciones de seguridad
    riesgos_altos = []
    for modulo in modulos_info:
        if "metricas_seguridad" in modulo:
            for riesgo in modulo["metricas_seguridad"].get("riesgos_detectados", []):
                if riesgo["severidad"] > 40:  # Solo riesgos importantes
                    riesgos_altos.append({
                        "modulo": modulo["nombre"],
                        "riesgo": riesgo
                    })
    
    if riesgos_altos:
        recomendaciones.append({
            "tipo": "seguridad",
            "mensaje": f"Se detectaron {len(riesgos_altos)} riesgos de seguridad importantes",
            "impacto": "Alto",
            "detalles": riesgos_altos
        })
    
    # 2. Recomendaciones de calidad de código
    # Detectar módulos sin manejo de excepciones
    modulos_sin_excepciones = [m["nombre"] for m in modulos_info if not m["tiene_excepciones"]]
    if modulos_sin_excepciones:
        recomendaciones.append({
            "tipo": "seguridad",
            "mensaje": f"Módulos sin manejo de excepciones: {', '.join(modulos_sin_excepciones)}",
            "impacto": "Alto"
        })
    
    # Detectar patrones inconsistentes
    patrones = [m["patron_registro"] for m in modulos_info]
    if len(set(patrones)) > 1:
        recomendaciones.append({
            "tipo": "consistencia",
            "mensaje": f"Se detectaron {len(set(patrones))} patrones diferentes de registro",
            "impacto": "Medio"
        })
    
    # 3. Recomendaciones de arquitectura
    # Detectar URLs potencialmente conflictivas
    todas_urls = [url for m in modulos_info for url in m["urls"]]
    urls_genericas = [url for url in todas_urls if '{nombre_nora}' in url]
    if len(urls_genericas) < len(todas_urls):
        recomendaciones.append({
            "tipo": "arquitectura",
            "mensaje": f"Algunas URLs ({len(todas_urls) - len(urls_genericas)}) no son dinámicas",
            "impacto": "Bajo"
        })
    
    # 4. Recomendaciones basadas en AST
    if metricas_ast and metricas_ast.get("complejidad_promedio", 0) > 8:
        recomendaciones.append({
            "tipo": "complejidad",
            "mensaje": f"La complejidad ciclomática promedio ({metricas_ast['complejidad_promedio']:.1f}) es alta",
            "impacto": "Medio",
            "detalles": "Considere refactorizar las funciones más complejas para mejorar la mantenibilidad"
        })
    
    # 5. Detección de código duplicado (simplificada)
    lineas = contenido_completo.split('\n')
    bloques = []
    
    for i in range(len(lineas) - 4):
        bloque = '\n'.join(lineas[i:i+5])
        if len(bloque.strip()) > 100:  # Solo bloques significativos
            bloques.append(bloque)
    
    # Contar bloques similares (simplificado, un análisis real usaría algoritmos más sofisticados)
    contador_bloques = Counter(bloques)
    bloques_duplicados = [b for b, count in contador_bloques.items() if count > 1]
    
    if bloques_duplicados:
        recomendaciones.append({
            "tipo": "duplicación",
            "mensaje": f"Se detectaron {len(bloques_duplicados)} posibles bloques de código duplicados",
            "impacto": "Medio",
            "detalles": "Considere extraer estos patrones en funciones para mejorar mantenibilidad"
        })
    
    return recomendaciones

def analizar_dependencias_modulos(modulos_info, contenido):
    """
    Analiza las dependencias entre módulos.
    
    Args:
        modulos_info (list): Lista de información de módulos
        contenido (str): Contenido completo del archivo
        
    Returns:
        dict: Información sobre dependencias entre módulos
    """
    dependencias = {}
    
    for modulo in modulos_info:
        nombre_modulo = modulo["nombre"]
        dependencias[nombre_modulo] = []
        
        # Buscar referencias a otros módulos en el bloque de este módulo
        for otro_modulo in modulos_info:
            if otro_modulo["nombre"] != nombre_modulo:
                patron_referencia = rf'[\s.(]({otro_modulo["nombre"]})[\s.)]'
                bloque_modulo = next((m for m in re.finditer(rf'if\s+[\'"]({nombre_modulo})[\'"]\s+in\s+modulos.*?(?=if\s+[\'"]\w+[\'"]\s+in\s+modulos|$)', contenido, re.DOTALL)), None)
                
                if bloque_modulo and re.search(patron_referencia, bloque_modulo.group(0)):
                    dependencias[nombre_modulo].append(otro_modulo["nombre"])
    
    # Calcular métricas de acoplamiento
    modulos_acoplados = sum(1 for m, deps in dependencias.items() if deps)
    
    return {
        "grafo": dependencias,
        "modulos_acoplados": modulos_acoplados,
        "porcentaje_acoplamiento": (modulos_acoplados / len(modulos_info)) * 100 if modulos_info else 0
    }

@registro_dinamico_frontend_bp.route('/api/analisis_avanzado')
def api_analisis_avanzado():
    """
    API para obtener un análisis avanzado del código del registro dinámico.
    Incluye métricas de seguridad, calidad y recomendaciones detalladas.
    
    Returns:
        Response: JSON con el resultado del análisis avanzado
    """
    try:
        registro_info = analizar_registro_dinamico_global()
        
        # Filtrar información relevante para el análisis avanzado
        analisis_avanzado = {
            "metricas_globales": registro_info.get("metricas_globales", {}),
            "salud_codigo": registro_info.get("estructura_global", {}).get("nivel_salud_codigo", "desconocido"),
            "recomendaciones": registro_info.get("recomendaciones", []),
            "dependencias": registro_info.get("grafo_dependencias", {})
        }
        
        return jsonify(analisis_avanzado)
    except Exception as e:
        logger.error(f"Error en API de análisis avanzado: {str(e)}")
        return jsonify({"error": str(e)}), 500

def realizar_analisis_ia(codigo, modulos_info):
    """
    Utiliza IA para analizar el código del registro dinámico y proporcionar recomendaciones avanzadas.
    
    Args:
        codigo (str): Código fuente a analizar
        modulos_info (list): Información de los módulos extraída del análisis estándar
        
    Returns:
        dict: Análisis y recomendaciones generadas por IA
    """
    try:
        # Crear un hash del código para verificar si ha cambiado
        codigo_hash = hashlib.md5(codigo.encode()).hexdigest()
        
        global _cache_analisis_ia
        # Si tenemos un análisis reciente y el código no ha cambiado, usar caché
        if (_cache_analisis_ia["datos"] and 
            time.time() - _cache_analisis_ia["timestamp"] < _cache_analisis_ia["tiempo_vida"] and
            _cache_analisis_ia["datos"].get("codigo_hash") == codigo_hash):
            
            logger.debug("Usando análisis IA en caché")
            return _cache_analisis_ia["datos"]
            
        # Preparar contexto para el análisis
        modulos_nombres = [m["nombre"] for m in modulos_info]
        contexto = {
            "total_modulos": len(modulos_info),
            "nombres_modulos": modulos_nombres,
            "complejidad_promedio": sum(m["complejidad"] for m in modulos_info) / len(modulos_info) if modulos_info else 0
        }
        
        # Limitar el código a analizar para evitar tokens excesivos
        codigo_resumido = codigo[:15000] if len(codigo) > 15000 else codigo
        
        # Crear prompt para el análisis
        prompt = f"""
        Analiza el siguiente código de registro dinámico de módulos de Python y proporciona:
        
        1. Identificación de patrones de diseño utilizados
        2. Problemas potenciales de escalabilidad
        3. Duplicación de código y oportunidades de refactorización
        4. Vulnerabilidades de seguridad específicas
        5. Recomendaciones para mejorar la arquitectura
        
        Contexto del sistema:
        - Hay {contexto['total_modulos']} módulos registrados
        - Los módulos son: {', '.join(contexto['nombres_modulos'][:10])}{"..." if len(contexto['nombres_modulos']) > 10 else ""}
        - Complejidad promedio: {contexto['complejidad_promedio']:.1f}
        
        Código a analizar:
        ```python
        {codigo_resumido}
        ```
        
        Responde en formato JSON con la siguiente estructura:
        {{
            "patrones_identificados": [lista de patrones],
            "problemas_escalabilidad": [lista de problemas],
            "codigo_duplicado": [lugares donde hay duplicación],
            "vulnerabilidades": [lista de vulnerabilidades],
            "recomendaciones_arquitectura": [lista de recomendaciones],
            "evaluacion_general": "texto con evaluación general"
        }}
        """
        
        # Llamar a OpenAI para análisis
        respuesta = generar_respuesta(prompt, model="gpt-4o", temperature=0.2, response_format={"type": "json_object"})
        
        try:
            resultado = json.loads(respuesta)
            # Añadir metadatos
            resultado["codigo_hash"] = codigo_hash
            resultado["timestamp"] = time.time()
            
            # Guardar en caché
            _cache_analisis_ia["datos"] = resultado
            _cache_analisis_ia["timestamp"] = time.time()
            
            return resultado
        except json.JSONDecodeError:
            logger.error("La respuesta de la IA no es un JSON válido")
            return {
                "error": "Formato de respuesta inválido",
                "respuesta_raw": respuesta[:500]
            }
            
    except Exception as e:
        logger.error(f"Error en análisis IA: {str(e)}")
        return {"error": str(e)}

@registro_dinamico_frontend_bp.route('/api/analisis_ia')
def api_analisis_ia():
    """
    API que proporciona análisis avanzado usando IA sobre el registro dinámico.
    
    Returns:
        Response: JSON con el resultado del análisis de IA
    """
    try:
        # Obtener código fuente
        registro_path = Path("clientes/aura/registro/registro_dinamico.py")
        if not registro_path.exists():
            return jsonify({"error": "No se encontró el archivo de registro dinámico"}), 404
            
        with open(registro_path, "r", encoding="utf-8") as f:
            codigo = f.read()
        
        # Obtener análisis básico
        registro_info = obtener_analisis_con_cache()
        
        # Realizar análisis de IA
        analisis_ia = realizar_analisis_ia(codigo, registro_info.get("modulos", []))
        
        return jsonify(analisis_ia)
    except Exception as e:
        logger.error(f"Error en API de análisis IA: {str(e)}")
        return jsonify({"error": str(e)}), 500

def determinar_patron_registro(bloque_codigo):
    """
    Determina el patrón de registro utilizado en un bloque de código.
    
    Args:
        bloque_codigo (str): Bloque de código a analizar
        
    Returns:
        str: Tipo de patrón detectado (try-except, if-else, etc.)
    """
    if "try:" in bloque_codigo and "except" in bloque_codigo:
        return "try-except"
    elif "if" in bloque_codigo and "else" in bloque_codigo:
        return "if-else"
    elif "if" in bloque_codigo:
        return "if-simple"
    else:
        return "directo"

def obtener_mas_comun(items):
    """
    Obtiene el elemento más común de una lista.
    
    Args:
        items (list): Lista de elementos
        
    Returns:
        str: El elemento más común o 'Ninguno' si la lista está vacía
    """
    if not items:
        return "Ninguno"
    
    contador = Counter(items)
    return contador.most_common(1)[0][0] if contador else "Ninguno"

def obtener_patron_url_comun(urls):
    """
    Obtiene el patrón común entre varias URLs.
    
    Args:
        urls (list): Lista de URLs a analizar
        
    Returns:
        str: El patrón de URL más común o 'Ninguno' si no hay URLs
    """
    if not urls:
        return "Ninguno"
        
    try:
        # Extraer partes comunes de las URLs
        partes = []
        for url in urls:
            # Dividir por "/" y extraer partes significativas (no variables)
            partes.extend([p for p in url.split('/') if p and '{' not in p])
        
        contador = Counter(partes)
        mas_comunes = contador.most_common(3)
        
        return '/'.join([parte for parte, _ in mas_comunes]) if mas_comunes else "Personalizada"
    except Exception:
        return "Personalizada"

def obtener_imports_comunes(imports):
    """
    Obtiene los imports más comunes.
    
    Args:
        imports (list): Lista de imports a analizar
        
    Returns:
        list: Los 3 imports más comunes
    """
    if not imports:
        return []
        
    contador = Counter(imports)
    return [imp for imp, _ in contador.most_common(3)]

def contar_ocurrencias(items):
    """
    Cuenta las ocurrencias de cada elemento en una lista.
    
    Args:
        items (list): Lista de elementos a contar
        
    Returns:
        dict: Diccionario con el recuento de cada elemento
    """
    if not items:
        return {}
        
    contador = Counter(items)
    return dict(contador)

def obtener_noras_con_modulo(nombre_modulo):
    """
    Obtiene las Noras que tienen un módulo específico activado.
    
    Args:
        nombre_modulo (str): Nombre del módulo a buscar
        
    Returns:
        list: Lista de Noras que tienen el módulo activado
    """
    try:
        # Consultar Noras en Supabase
        response = supabase.table("configuracion_bot").select("nombre_nora,numero_nora,modulos").execute()
        
        if not response.data:
            logger.warning(f"No se encontraron configuraciones de Noras para el módulo {nombre_modulo}")
            return []
        
        # Filtrar las Noras que tienen este módulo
        noras_con_modulo = []
        for nora in response.data:
            modulos = nora.get("modulos", [])
            # Convertir a lista si es string
            if isinstance(modulos, str):
                try:
                    import json
                    modulos = json.loads(modulos)
                except:
                    modulos = []
                    
            if nombre_modulo in modulos:
                noras_con_modulo.append({
                    "nombre_nora": nora.get("nombre_nora", "Sin nombre"),
                    "numero_nora": nora.get("numero_nora", "0")
                })
        
        return noras_con_modulo
    except Exception as e:
        logger.error(f"Error al obtener Noras con el módulo {nombre_modulo}: {str(e)}")
        return []

def notificar_problemas_criticos(registro_info):
    """
    Revisa el análisis en busca de problemas críticos que requieran notificación inmediata.
    
    Args:
        registro_info (dict): Información del análisis del registro
    """
    try:
        # Verificar si hay problemas críticos de seguridad
        problemas_criticos = []
        
        # 1. Verificar riesgos de seguridad altos
        for modulo in registro_info.get("modulos", []):
            if "metricas_seguridad" in modulo:
                for riesgo in modulo.get("metricas_seguridad", {}).get("riesgos_detectados", []):
                    if riesgo.get("severidad", 0) > 60:  # Solo riesgos muy importantes
                        problemas_criticos.append(
                            f"Módulo '{modulo['nombre']}': {riesgo['tipo']} (severidad: {riesgo['severidad']})"
                        )
        
        # 2. Verificar nivel de salud crítico
        if registro_info.get("estructura_global", {}).get("nivel_salud_codigo") == "crítico":
            problemas_criticos.append("La salud general del código es crítica")
        
        # Si hay problemas críticos, notificar
        if problemas_criticos:
            from clientes.aura.utils.notificaciones import enviar_notificacion_sistema
            
            mensaje = "⚠️ ALERTAS CRÍTICAS en el Registro Dinámico:\n\n" + "\n".join(problemas_criticos)
            enviar_notificacion_sistema(
                titulo="Alerta de seguridad: Registro Dinámico",
                mensaje=mensaje,
                nivel="critico"
            )
            logger.warning(f"Se enviaron notificaciones por {len(problemas_criticos)} problemas críticos")
    
    except Exception as e:
        logger.error(f"Error al procesar notificaciones de problemas críticos: {str(e)}")

@registro_dinamico_frontend_bp.route('/api/estado')
def api_estado_registro():
    """
    API que devuelve un resumen del estado del registro dinámico para monitoreo.
    Formato compatible con sistemas de monitorización.
    """
    try:
        registro_info = obtener_analisis_con_cache()
        estructura = registro_info.get("estructura_global", {})
        
        # Determinar estado general
        estado = "ok"
        if estructura.get("nivel_salud_codigo") in ["necesita mejoras", "crítico"]:
            estado = "warning"
        
        # Si hay errores críticos de seguridad, marcar como error
        for modulo in registro_info.get("modulos", []):
            if "metricas_seguridad" in modulo:
                for riesgo in modulo.get("metricas_seguridad", {}).get("riesgos_detectados", []):
                    if riesgo.get("severidad", 0) > 60:
                        estado = "error"
                        break
        
        # Preparar respuesta
        respuesta = {
            "estado": estado,
            "mensaje": f"Estado de salud: {estructura.get('nivel_salud_codigo', 'desconocido')}",
            "datos": {
                "total_modulos": estructura.get("total_modulos", 0),
                "seguridad": estructura.get("puntuacion_seguridad_promedio", 0),
                "calidad": estructura.get("puntuacion_calidad_promedio", 0),
                "ultimo_analisis": _cache_analisis["timestamp"]
            }
        }
        
        return jsonify(respuesta)
    except Exception as e:
        logger.error(f"Error al obtener estado del registro: {str(e)}")
        return jsonify({
            "estado": "error",
            "mensaje": f"Error al analizar: {str(e)}",
            "datos": {}
        }), 500

@registro_dinamico_frontend_bp.route('/analisis_ia')
def vista_analisis_ia():
    """Vista del análisis avanzado con IA del registro dinámico."""
    try:
        # Obtener análisis estándar y de IA
        registro_info = obtener_analisis_con_cache()
        
        # Obtener código fuente
        registro_path = Path("clientes/aura/registro/registro_dinamico.py")
        if not registro_path.exists():
            flash("No se encontró el archivo de registro dinámico", "warning")
            return redirect(url_for('registro_dinamico_frontend.index'))
            
        with open(registro_path, "r", encoding="utf-8") as f:
            codigo = f.read()
        
        # Realizar análisis de IA
        analisis_ia = realizar_analisis_ia(codigo, registro_info.get("modulos", []))
        
        return render_template(
            'admin_modulos/registro_dinamico/analisis_ia.html',
            registro_info=registro_info,
            analisis_ia=analisis_ia
        )
    
    except Exception as e:
        logger.error(f"Error al cargar análisis IA: {str(e)}")
        flash(f"Ha ocurrido un error: {str(e)}", "danger")
        return redirect(url_for('registro_dinamico_frontend.index'))

# Añadir después de la definición del blueprint
@registro_dinamico_frontend_bp.app_template_filter('timestamp_to_date')
def timestamp_to_date(timestamp):
    """Convierte un timestamp a formato legible de fecha y hora."""
    if not timestamp:
        return "Fecha desconocida"
    return datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M:%S")