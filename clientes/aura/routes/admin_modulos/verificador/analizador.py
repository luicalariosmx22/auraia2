def listar_modulos_en_supabase():
    """
    Imprime la lista de nombres de módulos registrados en la tabla modulos_disponibles de Supabase.
    """
    from clientes.aura.utils.db import get_supabase_client
    supabase = get_supabase_client()
    response = supabase.table("modulos_disponibles").select("nombre").execute()
    if not response.data:
        print("No hay módulos registrados en la base de datos.")
        return []
    modulos = [row["nombre"] for row in response.data if "nombre" in row]
    print("Módulos en la base de datos:")
    for nombre in modulos:
        print(f"- {nombre}")
    return modulos
from pathlib import Path
import re
import os
import json
from typing import Dict, Any, List, Optional

from clientes.aura.logger import logger
from .http_checker import verificar_respuesta_http
from .file_utils import buscar_en_init, obtener_rutas_de_blueprint, contiene_blueprint, obtener_contenido_archivo
from .registro import buscar_en_registro_dinamico, modulo_parece_registrado, sugerencia_registro_dinamico
from clientes.aura.utils.nora_config import get_noras_with_module, is_module_active_in_nora

# Constantes
MODULOS_PATH = Path("clientes/aura/routes")

def analizar_modulo(nombre: str, ruta: str = None) -> dict:
    """
    Analiza el estado completo de un módulo.
    
    Args:
        nombre (str): Nombre del módulo a analizar (sin prefijo panel_cliente_)
        ruta (str, optional): Ruta al módulo. Por defecto None.
        
    Returns:
        dict: Diccionario con toda la información del módulo analizado
    """

    try:
        from clientes.aura.utils.db import get_supabase_client
        supabase = get_supabase_client()
        # Consultar si el módulo existe en Supabase
        response = supabase.table("modulos_disponibles").select("*").eq("nombre", nombre).execute()

        if not response.data or not response.data[0]:
            # No mostrar advertencias ni retornar objetos de diagnóstico
            return None

        # Si existe, inicializar el objeto modulo y continuar el análisis normal
        modulo = {
            "nombre": nombre,
            "ruta": ruta,
            "detalles_registro": {},
            "existe_archivo": False  # Siempre inicializar
        }

        # 2. Verificar carpeta templates
        carpeta_templates = None
        
        # Primero buscar en carpeta específica del módulo
        path_templates_especifico = MODULOS_PATH / f"panel_cliente_{nombre}" / "templates"
        if path_templates_especifico.exists():
            carpeta_templates = path_templates_especifico
            
        # Luego en templates general
        if not carpeta_templates:
            path_templates_general = Path("clientes/aura/templates") / nombre
            if path_templates_general.exists():
                carpeta_templates = path_templates_general

        modulo["carpeta_templates"] = str(carpeta_templates) if carpeta_templates else None
        modulo["templates_encontrados"] = []
        
        if carpeta_templates:
            for template in carpeta_templates.glob("*.html"):
                modulo["templates_encontrados"].append(template.name)
        else:
            modulo.setdefault("diagnostico_404", []).append(
                "⚠️ No se encontró carpeta de templates para este módulo"
            )

        # Verificar si existen templates HTML para este módulo
        modulo["template_html"] = False
        templates_paths = [
            Path("clientes/aura/templates") / nombre,
            Path("clientes/aura/templates") / f"panel_cliente_{nombre}",
            Path("clientes/aura/templates") / f"{nombre}",
        ]

        for templates_path in templates_paths:
            if templates_path.exists() and templates_path.is_dir():
                # Verificar si hay archivos HTML en esta carpeta
                html_files = list(templates_path.glob("*.html"))
                if html_files:
                    modulo["template_html"] = True
                    modulo["templates_path"] = str(templates_path)
                    modulo["templates_encontrados"] = [str(f.name) for f in html_files]
                    break

        # Si no se encontró en las rutas estándar, buscar en el código fuente
        if not modulo["template_html"] and modulo.get("existe_archivo", False):
            try:
                archivo_path = Path(modulo.get("path_archivo", ""))
                if archivo_path.exists():
                    with open(archivo_path, "r", encoding="utf-8") as f:
                        contenido = f.read()
                        
                        # Buscar referencias a render_template en el código
                        if "render_template" in contenido:
                            # Extraer nombres de plantillas
                            # import re ya está al inicio del archivo
                            template_matches = re.findall(r'render_template\s*\(\s*["\']([^"\']+)["\']', contenido)
                            
                            if template_matches:
                                modulo["template_html"] = True
                                modulo["templates_encontrados"] = template_matches
                                modulo["templates_detectados_en_codigo"] = True
                                
                                # Intentar determinar la ruta completa de los templates
                                templates_detectados = []
                                for template in template_matches:
                                    # Verificar diferentes rutas posibles para encontrar el template
                                    posibles_rutas = [
                                        Path("clientes/aura/templates") / template,
                                        Path("clientes/aura/templates") / nombre / Path(template).name,
                                        Path("clientes/aura/templates") / f"panel_cliente_{nombre}" / Path(template).name
                                    ]
                                    
                                    for ruta in posibles_rutas:
                                        if ruta.exists():
                                            templates_detectados.append(str(ruta))
                                            break
                                    else:
                                        templates_detectados.append(f"⚠️ No encontrado: {template}")
                                        
                                modulo["templates_rutas_completas"] = templates_detectados
            except Exception as e:
                print(f"❌ Error al buscar referencias a templates en el código: {str(e)}")
                modulo.setdefault("diagnostico_404", []).append(
                    f"❌ Error al buscar templates en código: {str(e)}"
                )

        # 3. Verificar respuesta HTTP
        try:
            # Obtener nombre_nora real del módulo
            nombre_nora = modulo.get("activado_en", ["aura"])[0]  # fallback a "aura" si no hay datos
            
            # Construir ruta completa para verificación
            ruta_completa = f"/panel_cliente/{nombre_nora}/{modulo['nombre']}"
            
            # Verificar respuesta HTTP
            info_http = verificar_respuesta_http(ruta_completa)
            
            modulo.update({
                "respuesta_http": info_http["status"],
                "explicacion_http": info_http["causa"],
                "redirige_a": info_http["location"],
                "existe_ruta": info_http.get("existe", False),
                "protegida_por_login": info_http.get("protegida_por_login", False)  # Asegurar que se propaga esta propiedad
            })
            
            # Verificar específicamente el caso de sesión no válida
            if info_http.get("status") == 302 and info_http.get("protegida_por_login"):
                modulo.setdefault("diagnostico_404", []).append(
                    "❌ Sesión no válida en localhost:5000, redirigiendo a login. Inicia sesión antes de verificar este módulo."
                )
            elif not info_http.get("existe", False):
                modulo.setdefault("diagnostico_404", []).append(
                    f"⚠️ {info_http['causa']}"
                )
                
            # Si es un código 308, añadir sugerencia específica
            if info_http.get("status") == 308:
                modulo.setdefault("diagnostico_404", []).append(
                    "💡 La URL necesita una barra diagonal (/) al final. Corrige tu configuración de url_prefix para añadirla."
                )
                
        except Exception as e:
            print(f"❌ Error al verificar respuesta HTTP de {nombre}: {e}")
            modulo.update({
                "respuesta_http": None,
                "existe_ruta": False,
                "explicacion_http": f"Error: {str(e)}",
                "redirige_a": None
            })

        # Verificar registro en registro_dinamico.py
        try:
            info_registro = buscar_en_registro_dinamico(nombre)
            modulo["registrado_codigo"] = info_registro.get("registrado", False)
            modulo["detalles_registro"] = info_registro.get("detalles", {})
            
            if not info_registro.get("registrado"):
                modulo.setdefault("diagnostico_404", []).append(
                    "⚠️ El módulo no está registrado correctamente"
                )
        except Exception as e:
            print(f"❌ Error al verificar registro dinámico: {e}")
            modulo["registrado_codigo"] = False
            modulo["detalles_registro"] = {"error": str(e)}

        # Análisis heurístico del registro
        try:
            with open("clientes/aura/registro/registro_dinamico.py", "r", encoding="utf-8") as f:
                contenido_registro = f.read()
                
            resultado_ia = modulo_parece_registrado(nombre, contenido_registro)
            
            modulo.update({
                "registro_dinamico_ia": resultado_ia,
                "nivel_confianza_registro": resultado_ia["nivel_confianza"]
            })
            
            if not resultado_ia["parece_registrado"]:
                modulo.setdefault("diagnostico_404", []).append(
                    "⚠️ No se detectó registro dinámico mediante análisis heurístico"
                )
                if resultado_ia["sugerencia"]:
                    modulo["sugerencia_registro"] = sugerencia_registro_dinamico(nombre)
                    
        except FileNotFoundError:
            print("❌ No se encontró el archivo registro_dinamico.py")
            modulo["registro_dinamico_ia"] = {
                "error": "Archivo no encontrado",
                "parece_registrado": False
            }
        except Exception as e:
            print(f"❌ Error en análisis heurístico: {e}")
            modulo["registro_dinamico_ia"] = {
                "error": str(e),
                "parece_registrado": False
            }
        
        # Verificar registro en __init__.py principal
        try:
            with open("clientes/aura/__init__.py", "r", encoding="utf-8") as f:
                init_texto = f.read()
            
            modulo["menciones_en_init"] = buscar_en_init(modulo["nombre"], init_texto)
            
            if not modulo["menciones_en_init"]:
                modulo.setdefault("diagnostico_404", []).append(
                    "⚠️ El módulo no parece estar registrado en __init__.py principal"
                )
        except Exception as e:
            print(f"❌ Error al verificar __init__.py principal: {e}")
            modulo["menciones_en_init"] = []  # Aseguramos que exista la clave

        # Verificar activación en instancias Nora
        try:
            # Consultar las Noras donde el módulo está activo
            noras_activas = get_noras_with_module(nombre)
            
            modulo["activado_en"] = noras_activas
            
            # Marcar error si no está activo en ninguna Nora
            if not noras_activas:
                modulo.setdefault("diagnostico_404", []).append(
                    "❌ No está activo en ninguna Nora"
                )
                
                # Añadir sugerencia de activación
                modulo.setdefault("sugerencias", []).append(
                    "💡 Para activar este módulo, añádelo a la configuración de la Nora en la sección de Administración"
                )
            else:
                # Está activo en al menos una Nora
                noras_lista = ", ".join(noras_activas)
                modulo.setdefault("resumen", []).append(
                    f"✅ Activo en {len(noras_activas)} Nora(s): {noras_lista}"
                )
                
        except Exception as e:
            logger.error(f"❌ Error al verificar activación en Noras para '{nombre}': {str(e)}")
            modulo["activado_en"] = []
            modulo.setdefault("diagnostico_404", []).append(
                "⚠️ No se pudo verificar si está activo en alguna Nora"
            )

        # Generar sugerencia si no está registrado dinámicamente
        if not modulo.get("registrado_en_registro_dinamico"):
            sugerencia = sugerencia_registro_dinamico(nombre)
            if sugerencia:
                modulo["sugerencia_registro"] = sugerencia
                modulo.setdefault("diagnostico_404", []).append(
                    "💡 Puedes agregar este código en registro_dinamico.py:"
                )
        
        # Detectar módulos "fantasma" (registrados pero sin archivos)
        if (modulo.get("registrado_codigo") or resultado_ia.get("parece_registrado", False)) and not modulo.get("existe_archivo"):
            modulo.setdefault("diagnostico_404", []).append(
                "⚠️ El módulo parece estar registrado en código pero no existe el archivo físico. Verifica si debería eliminarse el registro."
            )
        
        # Extraer la ruta base del módulo
        if modulo["existe_archivo"]:
            # Intentar extraer la ruta base del código
            ruta_base = None
            resultado = None
            # Obtener el contenido del archivo principal solo si existe
            archivo_path = Path(modulo.get("path_archivo", ""))
            if archivo_path.exists():
                resultado = obtener_contenido_archivo(str(archivo_path))
            # 1. Buscar en el código si hay un url_prefix explícito
            if resultado and resultado.get("contenido") and "url_prefix" in resultado["contenido"]:
                url_prefix_match = re.search(r'url_prefix\s*=\s*["\']([^"\']+)["\']', resultado["contenido"])
                if url_prefix_match:
                    ruta_base = url_prefix_match.group(1)
            # 2. Si no se encontró, buscar en registro dinámico
            if not ruta_base and modulo.get("detalles_registro") and modulo["detalles_registro"].get("ruta"):
                ruta_base = modulo["detalles_registro"].get("ruta")
            # 3. Si sigue sin encontrarse, buscar en Supabase
            if not ruta_base:
                try:
                    from clientes.aura.utils.db import get_supabase_client
                    supabase = get_supabase_client()
                    response = supabase.table("modulos_disponibles").select("ruta").eq("nombre", nombre).execute()
                    if response.data and response.data[0].get("ruta"):
                        ruta_base = response.data[0].get("ruta")
                except Exception as e:
                    print(f"⚠️ No se pudo consultar ruta en Supabase: {str(e)}")
            # 4. Finalmente, usar la ruta predeterminada si no se encontró ninguna
            if not ruta_base:
                ruta_base = f"/panel_cliente/{nombre}"
            # Guardar la ruta base en el objeto del módulo
            modulo["ruta_base"] = ruta_base
            # Construir rutas completas
            rutas_internas = []
            if resultado and resultado.get("contenido"):
                rutas_internas = obtener_rutas_de_blueprint(resultado["contenido"])
            modulo["rutas_flask"] = [f"{ruta_base}{ruta}" for ruta in rutas_internas]
            # Si hay al menos una ruta interna, usar la primera como ruta principal
            if rutas_internas:
                modulo["ruta_principal"] = f"{ruta_base}{rutas_internas[0]}"
            else:
                modulo["ruta_principal"] = ruta_base
        else:
            # Si no existe el archivo, establecer valores predeterminados
            modulo["ruta_base"] = f"/panel_cliente/{nombre}"
            modulo["rutas_flask"] = []
            modulo["ruta_principal"] = f"/panel_cliente/{nombre}"

        return modulo

    except Exception as e:
        print(f"❌ Error al analizar módulo: {str(e)}")
        return {
            "nombre": nombre,
            "error": str(e),
            "existe_ruta": False,
            "activado_en": ["aura"]  # valor por defecto
        }

def analizar_modulo_antiguo(nombre: str, ruta: str = None) -> dict:
    """
    Versión anterior del análisis de módulos, mantenida por compatibilidad.
    
    Args:
        nombre (str): Nombre del módulo
        ruta (str, optional): Ruta al módulo. Por defecto None.
        
    Returns:
        dict: Información del módulo
    """
    # Implementación mantenida por compatibilidad
    # (código antiguo que podría ser necesario mantener)
    return analizar_modulo(nombre, ruta)

def obtener_archivo_principal(nombre_modulo: str) -> Optional[str]:
    """
    Obtiene la ruta del archivo principal de un módulo consultando Supabase.
    
    Args:
        nombre_modulo: Nombre del módulo a consultar
        
    Returns:
        Ruta del archivo principal o None si no se encuentra
    """
    try:
        from clientes.aura.utils.db import get_supabase_client
        supabase = get_supabase_client()
        resultado = supabase.table('modulos_disponibles').select('archivo_principal').eq('nombre', nombre_modulo).execute()
        if resultado.data and resultado.data[0].get('archivo_principal'):
            logger.info(f"ℹ️ Usando archivo principal de modulos_disponibles para {nombre_modulo}: {resultado.data[0]['archivo_principal']}")
            return resultado.data[0]['archivo_principal']
        logger.warning(f"⚠️ No se encontró archivo_principal en modulos_disponibles para {nombre_modulo}")
        return None
    except Exception as e:
        logger.warning(f"⚠️ No se pudo consultar Supabase para archivo principal de {nombre_modulo}: {str(e)}")
        return None