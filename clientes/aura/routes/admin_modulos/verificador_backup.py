from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask import current_app
from clientes.aura.utils.login_required import login_required
from clientes.aura.utils.ai_modulos import validar_modulo
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.diagnostico_modulos import diagnosticar_error_404
from clientes.aura.utils.deteccion_inteligente import esta_registrado_ia
from clientes.aura.utils.verificar_http import verificar_respuesta_http
from clientes.aura.utils.diagnostico_ia import diagnosticar_modulo
from pathlib import Path
import os
import requests  # Añadimos requests para verificación HTTP
import re  # Importamos re para expresiones regulares

verificador_modulos_bp = Blueprint(
    "verificador_modulos",
    __name__,
    template_folder="../../../templates/admin_modulos",
)

# Directorio donde se encuentran los módulos
MODULOS_PATH = Path("clientes/aura/routes")

def _extraer_ruta(ruta_str):
    """Extrae una ruta de forma segura."""
    try:
        # Si es una cadena simple entre comillas
        if ruta_str.strip().startswith(("'", '"')):
            return eval(ruta_str.strip())
        # Si es una expresión f-string o variable
        return ruta_str.strip()
    except Exception:
        return ruta_str.strip()

def buscar_en_init(modulo_nombre: str, archivo_init_texto: str) -> list:
    """
    Busca patrones relacionados con un módulo en el archivo __init__.py principal.
    
    Args:
        modulo_nombre (str): Nombre del módulo a buscar
        archivo_init_texto (str): Contenido del archivo __init__.py
        
    Returns:
        list: Lista de patrones encontrados
    """
    patrones = [
        f"panel_cliente_{modulo_nombre}",
        f"clientes.aura.routes.panel_cliente_{modulo_nombre}",
        f"panel_cliente_{modulo_nombre}_bp",
        f"/panel_cliente/{{nombre_nora}}/{modulo_nombre}",
    ]
    encontrados = [p for p in patrones if p in archivo_init_texto]
    return encontrados

def buscar_menciones_en_init(modulo_nombre: str) -> list[str]:
    """
    Busca menciones de un módulo en el archivo __init__.py principal.
    
    Args:
        modulo_nombre (str): Nombre del módulo a buscar
        
    Returns:
        list[str]: Lista de patrones encontrados que mencionan al módulo
        
    Example:
        >>> buscar_menciones_en_init("meta_ads")
        ['panel_cliente_meta_ads', 'meta_ads_bp', '/panel_cliente/{nombre_nora}/meta_ads']
    """
    ruta = "clientes/aura/__init__.py"
    if not os.path.exists(ruta):
        print(f"⚠️ No se encontró el archivo {ruta}")
        return []
        
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read()
            
        coincidencias = []
        patrones = [
            f"panel_cliente_{modulo_nombre}",
            f"{modulo_nombre}_bp",
            f"/panel_cliente/{{nombre_nora}}/{modulo_nombre}",
        ]
        
        for patron in patrones:
            if patron in contenido:
                coincidencias.append(patron)
                
        return coincidencias
        
    except Exception as e:
        print(f"❌ Error al buscar menciones en __init__.py: {str(e)}")
        return []

def buscar_en_registro_dinamico(modulo_nombre: str) -> dict:
    """
    Verifica si un módulo está registrado en registro_dinamico.py usando detección inteligente.
    
    Args:
        modulo_nombre (str): Nombre del módulo a verificar
        
    Returns:
        dict: Información detallada del registro incluyendo método y detalles
    """
    try:
        with open("clientes/aura/registro/registro_dinamico.py", "r", encoding="utf-8") as f:
            texto_registro = f.read()
            
        info_registro = esta_registrado_ia(modulo_nombre, texto_registro)
        return info_registro
        
    except Exception as e:
        print(f"❌ Error al verificar registro_dinamico.py: {str(e)}")
        return {
            "registrado": False,
            "metodo": "error",
            "detalles": {"error": str(e)}
        }

def verificar_respuesta_http(url: str) -> dict:
    """
    Verifica si una URL responde correctamente y proporciona información detallada.
    
    Args:
        url (str): URL a verificar
        
    Returns:
        dict: Información detallada de la respuesta HTTP con:
            - status (int): Código de estado HTTP
            - causa (str): Explicación del resultado
            - location (str): URL de redirección si aplica
            - existe (bool): Si la ruta existe o no
        
    Example:
        >>> verificar_respuesta_http("http://localhost:5000/panel_cliente/aura/meta_ads")
        {
            "status": 302,
            "causa": "Ruta protegida por login",
            "location": "/login",
            "existe": True
        }
    """
    try:
        resp = requests.get(url, timeout=4, allow_redirects=False)
        
        resultado = {
            "status": resp.status_code,
            "causa": "",
            "location": resp.headers.get("Location", ""),
            "existe": False
        }
        
        if resp.status_code == 200:
            resultado.update({
                "causa": "Ruta accesible directamente",
                "existe": True
            })
        elif resp.status_code == 302:
            location = resp.headers.get("Location", "")
            if "/login" in location or "auth" in location:
                resultado.update({
                    "causa": "Ruta protegida por login",
                    "existe": True
                })
            else:
                resultado.update({
                    "causa": f"Redirección no esperada a: {location}"
                })
        elif resp.status_code == 404:
            resultado["causa"] = "Ruta no encontrada"
        elif resp.status_code == 500:
            resultado["causa"] = "Error interno del servidor"
        else:
            resultado["causa"] = f"Código de estado no esperado: {resp.status_code}"
            
        return resultado
        
    except Exception as e:
        return {
            "status": None,
            "causa": f"Error al verificar URL: {str(e)}",
            "location": "",
            "existe": False
        }

def _construir_ruta_completa(ruta_base: str, ruta_blueprint: str, nombre: str) -> str:
    """
    Construye la ruta completa combinando el prefijo dinámico con la ruta del blueprint.
    
    Args:
        ruta_base (str): Prefijo base (ej: "/panel_cliente/{nombre}/contactos")
        ruta_blueprint (str): Ruta del blueprint (ej: "/", "/editar")
        nombre (str): Nombre del módulo actual
        
    Returns:
        str: Ruta completa formateada
    """
    # Limpiar la ruta del decorador y comillas
    ruta_limpia = _extraer_ruta(ruta_blueprint)
    
    # Formatear ruta base con el nombre actual
    ruta_base_formateada = ruta_base.format(nombre=nombre)
    
    # Combinar rutas evitando dobles slashes
    ruta_limpia = ruta_limpia.lstrip("/")
    return f"{ruta_base_formateada}/{ruta_limpia}".rstrip("/")

def contiene_blueprint(texto: str, nombre_modulo: str) -> bool:
    """
    Detecta si el archivo contiene un blueprint válido para el módulo dado.
    
    Args:
        texto (str): Contenido del archivo a analizar
        nombre_modulo (str): Nombre del módulo a buscar
        
    Returns:
        bool: True si encuentra un blueprint válido
    """
    patrones = [
        rf'Blueprint\(\s*["\']panel_cliente_{nombre_modulo}["\']',  # Blueprint directo
        rf'panel_cliente_{nombre_modulo}_bp\s*=\s*Blueprint',      # Asignación a variable
        rf'safe_register_blueprint\(.*panel_cliente_{nombre_modulo}'  # Registro dinámico
    ]
    return any(re.search(patron, texto, re.MULTILINE) for patron in patrones)

def obtener_rutas_de_blueprint(texto: str) -> list[str]:
    """
    Extrae las rutas registradas con @blueprint.route(...) en el archivo.
    
    Args:
        texto (str): Contenido del archivo a analizar
        
    Returns:
        list[str]: Lista de rutas normalizadas
    """
    rutas = []
    patron = re.compile(r'@.*?_bp\.route\(\s*["\'](.*?)["\']')

    for match in patron.finditer(texto):
        ruta = match.group(1)
        if not ruta.startswith("/"):
            ruta = "/" + ruta
        rutas.append(ruta)
    return rutas

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

def analizar_modulo(nombre: str, ruta: str = None) -> dict:
    """Analiza el estado completo de un módulo."""
    try:
        modulo = {
            "nombre": nombre,
            "ruta": ruta,
            "detalles_registro": {}
        }

        # 1. Verificar archivo principal
        archivo_principal = f"panel_cliente_{nombre}.py"
        
        # Ruta preferida (carpeta del módulo)
        path_archivo = MODULOS_PATH / f"panel_cliente_{nombre}" / archivo_principal

        # Fallback si no existe ahí
        if not path_archivo.exists():
            path_archivo = MODULOS_PATH / archivo_principal
            if path_archivo.exists():
                print(f"⚠️ Módulo {nombre} encontrado en raíz de routes/ en lugar de su propia carpeta")
                modulo.setdefault("diagnostico_404", []).append(
                    "⚠️ El archivo principal está en la raíz en lugar de su propia carpeta"
                )

        if path_archivo.exists():
            try:
                texto = path_archivo.read_text(encoding="utf-8", errors="replace")

                # ✅ Detección de blueprint mejorada
                modulo["registrado_codigo"] = contiene_blueprint(texto, nombre)

                # ✅ Rutas unidas con url_prefix
                rutas_internas = obtener_rutas_de_blueprint(texto)
                url_prefix = f"/panel_cliente/{nombre}/contactos"
                modulo["rutas_flask"] = [f"{url_prefix}{ruta}" for ruta in rutas_internas]
                
            except Exception as e:
                print(f"❌ Error al analizar archivo {archivo_principal}: {e}")
                modulo["registrado_codigo"] = False
                modulo["rutas_flask"] = []
        else:
            modulo["registrado_codigo"] = False
            modulo["rutas_flask"] = []

        # ✅ Verificación HTTP unificada
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
                "existe_ruta": info_http["existe"]  # Cambiado de "ok" a "existe"
            })
            
            if not info_http["existe"]:  # Cambiado de "ok" a "existe"
                modulo.setdefault("diagnostico_404", []).append(
                    f"⚠️ {info_http['causa']}"
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

        # 🧠 Análisis heurístico del registro
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
    """Analiza el estado de un módulo y retorna sus detalles."""
    modulo = {"nombre": nombre, "ruta": ruta}
    
    # 1. Verificar carpeta backend
    carpeta_backend = MODULOS_PATH / f"panel_cliente_{nombre}"
    modulo["carpeta_backend"] = os.path.isdir(carpeta_backend)
    
    # 2. Verificar template HTML
    template_path = Path("clientes/aura/templates") / f"panel_cliente_{nombre}" / "index.html"
    modulo["template_html"] = os.path.isfile(template_path)
    
    # 3. Verificar registro en registro_dinamico.py
    info_registro = buscar_en_registro_dinamico(nombre)
    modulo["registrado_dinamico"] = info_registro["registrado"]
    modulo["metodo_registro"] = info_registro["metodo"]
    modulo["detalles_registro"] = info_registro.get("detalles", {})
    
    if not modulo["registrado_dinamico"]:
        modulo.setdefault("diagnostico_404", []).append(
            "⚠️ El módulo no está registrado en registro_dinamico.py"
        )
    
    # 4. Verificar activación en Noras
    try:
        noras = supabase.table("configuracion_bot").select("nombre_nora", "modulos").execute().data
        noras_activas = []
        for nora in noras:
            if nora.get("modulos") and nombre in nora["modulos"]:
                noras_activas.append(nora["nombre_nora"])
        modulo["activado_en"] = noras_activas
    except Exception as e:
        print(f"❌ Error al consultar configuracion_bot: {e}")
        modulo["activado_en"] = []
    
    # 🧠 Determinar nombre del archivo principal
    nombre_archivo_principal = None

    # Paso 1: Intentar obtener desde Supabase
    try:
        resultado = supabase.table("modulos_disponibles").select("archivo_principal").eq("nombre", nombre).single().execute()
        if resultado.data and resultado.data.get("archivo_principal"):
            nombre_archivo_principal = resultado.data["archivo_principal"]
    except Exception as e:
        print(f"❌ Error al obtener archivo_principal de Supabase: {e}")

    # Paso 2: Si no existe, usar el nombre por convención
    if not nombre_archivo_principal:
        nombre_archivo_principal = f"panel_cliente_{nombre}.py"

    # Paso 3: Validar existencia
    archivo_path = carpeta_backend / nombre_archivo_principal
    modulo["nombre_archivo_principal"] = nombre_archivo_principal
    modulo["existe_archivo"] = archivo_path.exists()
    
    # Si existe, verificar estructura con IA y extraer rutas/templates
    if modulo["existe_archivo"]:
        try:
            resultado = validar_modulo(archivo_path.read_text())
            modulo["validacion"] = resultado
            
            # Extraer rutas y templates
            modulo["rutas_registradas"] = []
            modulo["templates_renderizados"] = []
            
            try:
                contenido = archivo_path.read_text(encoding='utf-8', errors='ignore')
                
                # 1. Rutas registradas with @blueprint.route(...)
                rutas = re.findall(r"@[\w_]*\.route\((.*?)\)", contenido)
                rutas_blueprint = []
                
                for ruta in rutas:
                    try:
                        ruta_limpia = _extraer_ruta(ruta)
                        # Construir ruta completa con el prefijo dinámico
                        ruta_completa = _construir_ruta_completa(
                            f"/panel_cliente/{{nombre}}/{nombre}",
                            ruta_limpia,
                            nombre
                        )
                        rutas_blueprint.append(ruta_completa)
                    except Exception as e:
                        print(f"❌ Error al procesar ruta {ruta}: {e}")
                
                modulo["rutas_registradas"] = rutas_blueprint
                
                # 2. Templates usados en render_template(...)
                templates = re.findall(r"render_template\((.*?)\)", contenido)
                for t in templates:
                    try:
                        partes = t.split(",")[0].strip()
                        if partes.startswith(("'", '"')):
                            nombre_tpl = eval(partes)
                            ruta_tpl = Path("clientes/aura/templates") / nombre_tpl
                            modulo["templates_renderizados"].append({
                                "nombre": nombre_tpl,
                                "existe": ruta_tpl.is_file()
                            })
                    except Exception as e:
                        print(f"❌ Error al procesar template {t}: {e}")
                        
            except Exception as e:
                print(f"❌ Error al extraer rutas o templates: {e}")
                
        except Exception as e:
            modulo["validacion"] = {"ok": False, "errores": [str(e)]}
    else:
        modulo["validacion"] = {"ok": False, "errores": ["Archivo no encontrado"]}
    
    # Lista de submódulos y dependencias
    modulo["submodulos"] = []
    modulo["dependencias"] = set()  # Usamos set para evitar duplicados
    
    # Extraer nombres de archivos importados en __init__.py (submódulos activos)
    submodulos_importados = set()
    init_path = carpeta_backend / "__init__.py"

    if init_path.exists():
        try:
            with open(init_path, "r", encoding='utf-8', errors='ignore') as f:
                for linea in f:
                    if linea.strip().startswith("from .") and "import" in linea:
                        archivo = linea.strip().split(" ")[1].replace(".", "")  # de "from .editar import *" → "editar"
                        submodulos_importados.add(f"{archivo}.py")
        except Exception as e:
            print(f"❌ Error al analizar __init__.py: {e}")

    # Analizar submódulos y dependencias si existe la carpeta
    if modulo["carpeta_backend"]:
        try:
            # 1. Lista completa de .py en la carpeta
            archivos_totales = set()
            modulo["submodulos"] = []
            modulo["no_importados"] = []

            for archivo_py in carpeta_backend.glob("*.py"):
                nombre_archivo = archivo_py.name
                archivos_totales.add(nombre_archivo)

                if nombre_archivo in submodulos_importados:
                    # Es un submódulo activo
                    modulo["submodulos"].append(nombre_archivo)

                    # Extraer rutas
                    try:
                        contenido = archivo_py.read_text(encoding='utf-8', errors='ignore')

                        rutas = re.findall(r"@[\w_]*\.route\((.*?)\)", contenido)
                        for ruta in rutas:
                            try:
                                ruta_eval = eval(ruta.strip())
                            except Exception:
                                ruta_eval = ruta.strip()
                            modulo.setdefault("rutas_registradas", []).append(ruta_eval)

                        # Extraer templates
                        templates = re.findall(r"render_template\((.*?)\)", contenido)
                        for t in templates:
                            parte = t.split(",")[0].strip()
                            if parte.startswith(("'", '"')):
                                nombre_tpl = eval(parte)
                                ruta_tpl = Path("clientes/aura/templates") / nombre_tpl
                                modulo.setdefault("templates_renderizados", []).append({
                                    "nombre": nombre_tpl,
                                    "existe": ruta_tpl.is_file()
                                })
                    except Exception as e:
                        print(f"❌ Error al leer {archivo_py.name}: {e}")

            # Detectar archivos que no están importados (potencial basura)
            archivos_totales = [f for f in archivos_totales if f != "__init__.py"]
            modulo["no_importados"] = sorted(list(set(archivos_totales) - set(submodulos_importados)))

            # 2. Extraer dependencias de cada archivo
            for archivo in modulo["submodulos"]:
                ruta_archivo = carpeta_backend / archivo
                try:
                    with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
                        for linea in f:
                            linea = linea.strip()
                            if linea.startswith('import ') or linea.startswith('from '):
                                # Ignorar imports internos
                                if not linea.startswith(('from clientes.', 'from .')):
                                    # Extraer nombre de la librería
                                    if linea.startswith('import '):
                                        lib = linea.split()[1].split('.')[0]
                                    else:  # from ... import ...
                                        lib = linea.split()[1].split('.')[0]
                                    # Añadir si es una librería externa
                                    if not lib.startswith('.'):
                                        modulo["dependencias"].add(lib)
                except Exception as e:
                    print(f"❌ Error al leer dependencias de {archivo}: {e}")
        except Exception as e:
            print(f"❌ Error al listar submódulos: {e}")
    
    # Convertir el set de dependencias a lista para JSON
    modulo["dependencias"] = sorted(list(modulo["dependencias"]))
    
    # Si existe, verificar estructura con IA
    if modulo["existe_archivo"]:
        try:
            resultado = validar_modulo(archivo_path.read_text())
            modulo["validacion"] = resultado
        except Exception as e:
            modulo["validacion"] = {"ok": False, "errores": [str(e)]}
    else:
        modulo["validacion"] = {"ok": False, "errores": ["Archivo no encontrado"]}

    # ✅ Verificación HTTP mejorada y unificada
    try:
        base_url = current_app.config.get("BASE_URL", "http://localhost:5000")
        test_url = f"{base_url}/panel_cliente/aura/{nombre}"
        
        info_http = verificar_respuesta_http(test_url)
        
        modulo.update({
            "respuesta_http": info_http["status"],
            "existe_ruta": info_http["existe"],
            "explicacion_http": info_http["causa"],
            "redirige_a": info_http["location"]
        })
        
        if not info_http["existe"]:
            modulo.setdefault("diagnostico_404", []).append(
                f"⚠️ {info_http['causa']}"
            )
            
    except Exception as e:
        print(f"❌ Error al verificar respuesta HTTP de {nombre}: {e}")
        modulo.update({
            "respuesta_http": None,
            "existe_ruta": False,
            "explicacion_http": f"Error: {str(e)}",
            "redirige_a": None
        })
    
    # ✅ Validación HTTP mejorada
    # ✅ Verificar registro en __init__.py principal
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

    # Generar sugerencia si no está registrado dinámicamente
    if not modulo.get("registrado_en_registro_dinamico"):
        sugerencia = sugerencia_registro_dinamico(nombre)
        if sugerencia:
            modulo["sugerencia_registro"] = sugerencia
            modulo.setdefault("diagnostico_404", []).append(
                "💡 Puedes agregar este código en registro_dinamico.py:"
            )
    
    return modulo

@verificador_modulos_bp.route("/", methods=["GET"])
@login_required
def index():
    """Dashboard del verificador de módulos."""
    # Obtener todos los módulos registrados
    modulos = supabase.table("modulos_disponibles").select("*").execute().data
    
    # Analizar estado de cada módulo
    for modulo in modulos:
        nombre = modulo["nombre"]
        
        # 1. Verificar carpeta backend
        carpeta_backend = MODULOS_PATH / f"panel_cliente_{nombre}"
        modulo["carpeta_backend"] = os.path.isdir(carpeta_backend)
        
        # 2. Verificar template HTML
        template_path = Path("clientes/aura/templates") / f"panel_cliente_{nombre}" / "index.html"
        modulo["template_html"] = os.path.isfile(template_path)
        
        # 3. Verificar registro en registro_dinamico.py con función unificada
        try:
            modulo["registrado_codigo"] = buscar_en_registro_dinamico(nombre)
        except Exception as e:
            print(f"❌ Error al verificar registro dinámico: {e}")
            modulo["registrado_codigo"] = False
            
        # 4. Verificar activación en Noras
        try:
            noras = supabase.table("configuracion_bot").select("nombre_nora", "modulos").execute().data
            noras_activas = []
            for nora in noras:
                if nora.get("modulos") and nombre in nora["modulos"]:
                    noras_activas.append(nora["nombre_nora"])
            modulo["activado_en"] = noras_activas
        except Exception as e:
            print(f"❌ Error al consultar configuracion_bot: {e}")
            modulo["activado_en"] = []
        
        # 🧠 Determinar nombre del archivo principal
        nombre_archivo_principal = None

        # Paso 1: Intentar obtener desde Supabase
        try:
            resultado = supabase.table("modulos_disponibles").select("archivo_principal").eq("nombre", nombre).single().execute()
            if resultado.data and resultado.data.get("archivo_principal"):
                nombre_archivo_principal = resultado.data["archivo_principal"]
        except Exception as e:
            print(f"❌ Error al obtener archivo_principal de Supabase: {e}")

        # Paso 2: Si no existe, usar el nombre por convención
        if not nombre_archivo_principal:
            nombre_archivo_principal = f"panel_cliente_{nombre}.py"

        # Paso 3: Validar existencia
        archivo_path = carpeta_backend / nombre_archivo_principal
        modulo["nombre_archivo_principal"] = nombre_archivo_principal

        # Validar si el archivo principal existe
        modulo["existe_archivo"] = archivo_path.exists()
        
        # Lista de submódulos y dependencias
        modulo["submodulos"] = []
        modulo["dependencias"] = set()  # Usamos set para evitar duplicados
        
        # Extraer nombres de archivos importados en __init__.py (submódulos activos)
        submodulos_importados = set()
        init_path = carpeta_backend / "__init__.py"

        if init_path.exists():
            try:
                with open(init_path, "r", encoding='utf-8', errors='ignore') as f:
                    for linea in f:
                        if linea.strip().startswith("from .") and "import" in linea:
                            archivo = linea.strip().split(" ")[1].replace(".", "")  # de "from .editar import *" → "editar"
                            submodulos_importados.add(f"{archivo}.py")
            except Exception as e:
                print(f"❌ Error al analizar __init__.py: {e}")

        # Analizar submódulos y dependencias si existe la carpeta
        if modulo["carpeta_backend"]:
            try:
                # 1. Lista completa de .py en la carpeta
                archivos_totales = set()
                modulo["submodulos"] = []
                modulo["no_importados"] = []

                for archivo_py in carpeta_backend.glob("*.py"):
                    nombre_archivo = archivo_py.name
                    archivos_totales.add(nombre_archivo)

                    if nombre_archivo in submodulos_importados:
                        # Es un submódulo activo
                        modulo["submodulos"].append(nombre_archivo)

                        # Extraer rutas
                        try:
                            contenido = archivo_py.read_text(encoding='utf-8', errors='ignore')

                            rutas = re.findall(r"@[\w_]*\.route\((.*?)\)", contenido)
                            for ruta in rutas:
                                try:
                                    ruta_eval = eval(ruta.strip())
                                except Exception:
                                    ruta_eval = ruta.strip()
                                modulo.setdefault("rutas_registradas", []).append(ruta_eval)

                        except Exception as e:
                            print(f"❌ Error al leer {archivo_py.name}: {e}")

                # Detectar archivos que no están importados (potencial basura)
                archivos_totales = [f for f in archivos_totales if f != "__init__.py"]
                modulo["no_importados"] = sorted(list(set(archivos_totales) - set(submodulos_importados)))

                # 2. Extraer dependencias de cada archivo
                for archivo in modulo["submodulos"]:
                    ruta_archivo = carpeta_backend / archivo
                    try:
                        with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
                            for linea in f:
                                linea = linea.strip()
                                if linea.startswith('import ') or linea.startswith('from '):
                                    # Ignorar imports internos
                                    if not linea.startswith(('from clientes.', 'from .')):
                                        # Extraer nombre de la librería
                                        if linea.startswith('import '):
                                            lib = linea.split()[1].split('.')[0]
                                        else:  # from ... import ...
                                            lib = linea.split()[1].split('.')[0]
                                        # Añadir si es una librería externa
                                        if not lib.startswith('.'):
                                            modulo["dependencias"].add(lib)
                    except Exception as e:
                        print(f"❌ Error al leer dependencias de {archivo}: {e}")
            except Exception as e:
                print(f"❌ Error al listar submódulos: {e}")
        
        # Convertir el set de dependencias a lista para JSON
        modulo["dependencias"] = sorted(list(modulo["dependencias"]))
        
        # Si existe, verificar estructura con IA
        if modulo["existe_archivo"]:
            try:
                resultado = validar_modulo(archivo_path.read_text())
                modulo["validacion"] = resultado
            except Exception as e:
                modulo["validacion"] = {"ok": False, "errores": [str(e)]}
        else:
            modulo["validacion"] = {"ok": False, "errores": ["Archivo no encontrado"]}

    return render_template(
        "admin_modulos/index.html", 
        modulos=modulos,
        titulo="Verificador de Módulos",
        modo="verificador"  # Para diferenciar del modo creador
    )

@verificador_modulos_bp.route("/verificar-todos", methods=["POST"])
@login_required
def verificar_todos():
    """Verifica todos los módulos registrados."""
    modulos = supabase.table("modulos_disponibles").select("*").execute().data
    errores = []
    exitos = []

    for modulo in modulos:
        nombre = modulo["nombre"]
        archivo_path = MODULOS_PATH / f"cliente_{nombre}" / f"panel_cliente_{nombre}.py"
        
        if not archivo_path.exists():
            errores.append(f"❌ {nombre}: Archivo no encontrado")
            continue
            
        try:
            resultado = validar_modulo(archivo_path.read_text())
            if resultado.get("ok"):
                exitos.append(f"✅ Módulo {nombre}: Sin errores detectados por IA")
            else:
                errores.append(f"❌ Módulo {nombre}: {', '.join(resultado['errores'])}")
        except Exception as e:
            errores.append(f"❌ Error al validar {nombre}: {str(e)}")

    # Mostrar resultados
    for mensaje in exitos:
        flash(mensaje, "success")
    for mensaje in errores:
        flash(mensaje, "error")

    return redirect(url_for("verificador_modulos.index"))

@verificador_modulos_bp.route("/verificar/<nombre>", methods=["POST"])
@login_required
def verificar_modulo(nombre):
    """Verifica un módulo específico."""
    archivo_path = MODULOS_PATH / f"cliente_{nombre}" / f"panel_cliente_{nombre}.py"
    
    if not archivo_path.exists():
        flash(f"❌ Módulo {nombre}: Archivo no encontrado", "error")
        return redirect(url_for("verificador_modulos.index"))

    try:
        resultado = validar_modulo(archivo_path.read_text())
        if resultado.get("ok"):
            flash(f"✅ Módulo {nombre}: Estructura correcta", "success")
        else:
            flash(f"❌ Módulo {nombre}: {', '.join(resultado['errores'])}", "error")
    except Exception as e:
        flash(f"❌ Módulo {nombre}: Error al validar - {str(e)}", "error")

    return redirect(url_for("verificador_modulos.index"))

def verificar_ruta_disponible_por_nombre(modulo_nombre):
    """
    Verifica si existe una ruta dinámica registrada para el módulo.
    
    Args:
        modulo_nombre (str): Nombre del módulo a verificar
        
    Returns:
        bool: True si existe una ruta que coincide con el patrón /panel_cliente/<param>/{modulo}
    """
    reglas = [rule.rule for rule in current_app.url_map.iter_rules()]
    for ruta in reglas:
        # Verifica que la ruta siga el patrón: /panel_cliente/<algo>/{modulo}
        partes = ruta.strip("/").split("/")
        if (
            len(partes) >= 3 and
            partes[0] == "panel_cliente" and
            partes[2] == modulo_nombre and
            "<" in partes[1]  # para validar que es un parámetro dinámico como <nombre_nora>
        ):
            return True
    return False

@verificador_modulos_bp.route("/<nombre_modulo>", methods=["GET"])
@login_required
def ver_modulo(nombre_modulo):
    """Vista detallada de un módulo específico."""
    try:
        # 1. Buscar el módulo en la base de datos
        response = supabase.table("modulos_disponibles").select("*").eq("nombre", nombre_modulo).single().execute()
        if not response.data:
            flash(f"❌ Módulo {nombre_modulo} no encontrado", "error")
            return redirect(url_for("verificador_modulos.index"))
        
        modulo = response.data
        
        # 2. Obtener información básica mediante la función existente
        detalles = analizar_modulo(nombre_modulo, modulo.get("ruta"))
        modulo.update(detalles)
        
        # 3. Añadir información extra
        carpeta_backend = MODULOS_PATH / f"panel_cliente_{nombre_modulo}"
        
        # 3.1 Obtener nombre del archivo principal desde Supabase
        try:
            resultado = supabase.table("modulos_disponibles").select("archivo_principal").eq("nombre", nombre_modulo).single().execute()
            if resultado.data and resultado.data.get("archivo_principal"):
                nombre_archivo_principal = resultado.data["archivo_principal"]
            else:
                # Fallback a nombre por convención
                nombre_archivo_principal = f"panel_cliente_{nombre_modulo}.py"
                
            # Construir ruta completa al archivo
            archivo_path = carpeta_backend / nombre_archivo_principal
            
            # Agregar print de depuración
            print(f"[DEBUG] Verificando módulo '{nombre_modulo}' usando archivo: {archivo_path}")
            
            # Leer contenido una sola vez
            if archivo_path.exists():
                modulo["archivo_contenido"] = archivo_path.read_text(encoding='utf-8', errors='ignore')
                modulo["existe_archivo"] = True
                
                # Verificar que el contenido corresponde al archivo correcto
                if f"Archivo: clientes/aura/routes/{nombre_archivo_principal}" not in modulo["archivo_contenido"]:
                    modulo["diagnostico_404"] = modulo.get("diagnostico_404", [])
                    primera_linea = modulo["archivo_contenido"].splitlines()[0] if modulo["archivo_contenido"] else "desconocido"
                    modulo["diagnostico_404"].append(
                        f"⚠️ El contenido del archivo leído parece ser de otro módulo (quizás {primera_linea})"
                    )
                
                # Continuar con el diagnóstico 404 existente
                if modulo.get("respuesta_http") == 404:
                    modulo.setdefault("diagnostico_404", [])
                    modulo["diagnostico_404"].extend(
                        diagnosticar_error_404(modulo["archivo_contenido"], nombre="archivo principal")
                    )
            
            else:
                modulo["archivo_contenido"] = None
                modulo["existe_archivo"] = False
                
        except Exception as e:
            print(f"❌ Error al obtener/leer archivo principal: {e}")
            modulo["archivo_contenido"] = None
            modulo["existe_archivo"] = False

        # Agregar explicaciones generadas por IA
        modulo["explicaciones_ai"] = generar_explicacion_errores(modulo)
        
        # Diagnóstico adicional con IA
        modulo["diagnostico_ia"] = diagnosticar_modulo(modulo)
        
        # Renderizar template con los datos del módulo
        return render_template(
            "admin_modulos/detalle.html",
            modulo=modulo,
            titulo=f"Módulo: {nombre_modulo}",
            modo="verificador"
        )

    except Exception as e:
        import traceback
        print(f"❌ Error detallado al cargar módulo {nombre_modulo}:")
        print(traceback.format_exc())
        flash(f"❌ Error al cargar módulo {nombre_modulo}: {str(e)}", "error")
        return redirect(url_for("verificador_modulos.index"))

@verificador_modulos_bp.route("/<nombre_modulo>/archivo_principal", methods=["POST"])
@login_required
def definir_archivo_principal(nombre_modulo):
    """Guarda el archivo principal elegido manualmente para un módulo."""
    archivo = request.form.get("archivo_principal")
    if not archivo:
        flash("❌ No se seleccionó ningún archivo", "error")
        return redirect(url_for("verificador_modulos.ver_modulo", nombre_modulo=nombre_modulo))

    try:
        supabase.table("modulos_disponibles").update(
            {"archivo_principal": archivo}
        ).eq("nombre", nombre_modulo).execute()
        flash(f"✅ Archivo principal actualizado a: {archivo}", "success")
    except Exception as e:
        flash(f"❌ Error al guardar archivo principal: {str(e)}", "error")

    return redirect(url_for("verificador_modulos.ver_modulo", nombre_modulo=nombre_modulo))

def actualizar_registro_modulo(nombre_modulo: str, nuevo_archivo: str = None, nueva_ruta: str = None) -> dict:
    """
    Actualiza el registro de un módulo en la tabla modulos_disponibles de Supabase.
    
    Args:
        nombre_modulo (str): Nombre identificador del módulo
        nuevo_archivo (str, optional): Nuevo nombre del archivo principal. Defaults to None.
        nueva_ruta (str, optional): Nueva ruta del módulo. Defaults to None.
    
    Returns:
        dict: Resultado de la operación de Supabase o None si no hay cambios
    
    Example:
        >>> actualizar_registro_modulo("meta_ads", nuevo_archivo="panel_cliente_meta_ads.py")
        >>> actualizar_registro_modulo("meta_ads", nueva_ruta="panel_cliente_meta_ads.index")
    """
    campos_actualizar = {}
    
    if nuevo_archivo:
        campos_actualizar["archivo_principal"] = nuevo_archivo
    if nueva_ruta:
        campos_actualizar["ruta"] = nueva_ruta

    if not campos_actualizar:
        print("⚠️ No hay campos para actualizar.")
        return None

    try:
        resultado = supabase.table("modulos_disponibles") \
            .update(campos_actualizar) \
            .eq("nombre", nombre_modulo) \
            .execute()
        
        print(f"✅ Resultado al actualizar '{nombre_modulo}': {resultado}")
        return resultado
        
    except Exception as e:
        print(f"❌ Error al actualizar módulo '{nombre_modulo}': {str(e)}")
        raise

def sugerencia_registro_dinamico(modulo_nombre: str) -> dict:
    """
    Genera una sugerencia de código para registrar un módulo en registro_dinamico.py
    
    Args:
        modulo_nombre (str): Nombre del módulo a registrar
        
    Returns:
        dict: Diccionario con las líneas de código sugeridas y metadata
    """
    try:
        # Generar nombres y rutas
        nombre_blueprint = f"panel_cliente_{modulo_nombre}_bp"
        ruta_modulo = f"panel_cliente_{modulo_nombre}"
        
        # Construir las líneas de código
        lineas = {
            "import": f"from clientes.aura.routes.{ruta_modulo} import {nombre_blueprint}",
            "registro": f'safe_register_blueprint(app, {nombre_blueprint}, url_prefix=f"/panel_cliente/{{nombre_nora}}/{modulo_nombre}")',
            "condicion": f'if "{modulo_nombre}" in modulos:'
        }
        
        # Formatear el código completo
        codigo_completo = f"""
{lineas['condicion']}
    {lineas['import']}
    {lineas['registro']}"""
        
        return {
            "lineas": lineas,
            "codigo_completo": codigo_completo.strip(),
            "nombre_blueprint": nombre_blueprint,
            "ruta_modulo": ruta_modulo
        }
        
    except Exception as e:
        print(f"❌ Error al generar sugerencia para {modulo_nombre}: {str(e)}")
        return None

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
    
    # 2. Verifica si está el import correcto
    patron_import = rf"from clientes\.aura\.routes\.panel_cliente_{nombre_modulo}"
    if re.search(patron_import, contenido_registro):
        resultados["detalles"]["import_presente"] = True
        
    # 3. Verifica si tiene el url_prefix correcto
    patron_url = rf"url_prefix=f\"/panel_cliente/{{nombre_nora}}/{nombre_modulo}\""
    if re.search(patron_url, contenido_registro):
        resultados["detalles"]["url_prefix_correcto"] = True
    
    # 4. Verifica si el blueprint está siendo registrado
    patron_blueprint = rf"safe_register_blueprint\(.*panel_cliente_{nombre_modulo}_bp"
    if re.search(patron_blueprint, contenido_registro, re.MULTILINE | re.DOTALL):
        resultados["detalles"]["blueprint_registrado"] = True
    
    # Determinar si está registrado basado en los criterios
    resultados["registrado"] = (
        resultados["detalles"]["mencionado_como_string"] and 
        (resultados["detalles"]["import_presente"] or resultados["detalles"]["blueprint_registrado"])
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

# Actualizar la función que lo usa
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

def generar_explicacion_errores(modulo: dict) -> list[str]:
    """
    Genera explicaciones amigables para los errores detectados en el módulo.
    
    Args:
        modulo (dict): Diccionario con la información del módulo analizado
        
    Returns:
        list[str]: Lista de explicaciones en formato amigable
    """
    explicaciones = []

    # 1. Verificar estructura de archivos
    if not modulo.get("carpeta_backend"):
        explicaciones.append(
            "❌ No se encontró la carpeta backend del módulo. "
            "Asegúrate de que exista en 'clientes/aura/routes'."
        )

    if not modulo.get("existe_archivo"):
        explicaciones.append(
            f"❌ No se encontró el archivo principal '{modulo.get('nombre_archivo_principal')}'. "
            "Verifica el nombre y ubicación del archivo."
        )
    elif modulo.get("validacion", {}).get("errores"):
        errores_ia = ", ".join(modulo["validacion"]["errores"])
        explicaciones.append(
            f"⚠️ El archivo principal tiene errores de estructura: {errores_ia}"
        )

    # 2. Verificar registro y configuración
    if not modulo.get("registrado_codigo"):
        explicaciones.append(
            "❌ El módulo no está registrado correctamente en 'registro_dinamico.py'. "
            "Revisa que esté importado y registrado con safe_register_blueprint()."
        )
        
        # Añadir detalles del registro si están disponibles
        if modulo.get("detalles_registro", {}).get("diagnostico"):
            for detalle in modulo["detalles_registro"]["diagnostico"]:
                explicaciones.append(f"  → {detalle}")
        
    if not modulo.get("menciones_en_init"):
        explicaciones.append(
            "⚠️ El módulo no fue encontrado en '__init__.py'. "
            "Esto puede impedir su carga por Flask."
        )

    # 3. Verificar rutas y respuestas HTTP
    if not modulo.get("existe_ruta"):
        explicacion_base = (
            f"❌ La ruta '/panel_cliente/{{nombre}}/{modulo['nombre']}' "
            "no responde correctamente."
        )
        
        if modulo.get("explicacion_http"):
            explicacion_base += f" Causa: {modulo['explicacion_http']}"
            
        if modulo.get("respuesta_http"):
            explicacion_base += f" (HTTP {modulo['respuesta_http']})"
            
        explicaciones.append(explicacion_base)

    # 4. Verificar registro dinámico con IA
    if modulo.get("registro_dinamico_ia"):
        ia_info = modulo["registro_dinamico_ia"]
        if not ia_info.get("parece_registrado"):
            explicaciones.append(
                "🧠 Análisis IA: El módulo podría no estar correctamente registrado. "
                f"({ia_info.get('detalle', 'Sin detalles')})"
            )

    return explicaciones
