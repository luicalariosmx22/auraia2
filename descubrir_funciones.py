#!/usr/bin/env python3
"""
Sistema de descubrimiento automático de funciones para automatizaciones
Escanea módulos y registra funciones disponibles en la base de datos
"""

import os
import sys
import ast
import re
import inspect
import importlib
from datetime import datetime
from typing import Dict, List, Any, Optional

# Añadir el directorio raíz al path
sys.path.append('.')

from clientes.aura.utils.supabase_client import supabase

class DescubrirFunciones:
    """
    Clase para descubrir y registrar funciones automatizables
    """
    
    def __init__(self):
        self.modulos_base = {
            'automatizaciones_ejecutor': 'clientes.aura.utils.automatizaciones_ejecutor',
            'notificaciones': 'clientes.aura.utils.notificaciones',
            'reportes': 'clientes.aura.utils.reportes',
            'google_ads': 'clientes.aura.utils.google_ads_utils',
            'meta_ads': 'clientes.aura.utils.meta_ads_utils',
            'tareas': 'clientes.aura.utils.tareas_utils',
            'backup': 'clientes.aura.utils.backup_utils'
        }
        
        # Directorios completos de módulos (como diagnostico_modulos)
        self.directorios_modulos = {
            'meta_ads': 'clientes/aura/routes/panel_cliente_meta_ads',
            'google_ads': 'clientes/aura/routes/panel_cliente_google_ads', 
            'tareas': 'clientes/aura/routes/panel_cliente_tareas',
            'contactos': 'clientes/aura/routes/panel_cliente_contactos',
            'pagos': 'clientes/aura/routes/panel_cliente_pagos',
            'automatizaciones': 'clientes/aura/routes/panel_cliente_automatizaciones',
            'notificaciones': 'clientes/aura/routes/panel_cliente_notificaciones',
            'alertas': 'clientes/aura/routes/panel_cliente_alertas'
        }
        
        # Prefijos de funciones que se consideran automatizables
        self.prefijos_automatizables = [
            'ejemplo_',
            'automatizar_',
            'generar_',
            'enviar_',
            'procesar_',
            'sincronizar_',
            'limpiar_',
            'backup_',
            'reporte_',
            'crear_',
            'actualizar_',
            'eliminar_',
            'guardar_',
            'obtener_',
            'listar_',
            'importar_',
            'exportar_',
            'calcular_',
            'validar_',
            'verificar_',
            'conectar_',
            'configurar_',
            'activar_',
            'desactivar_',
            'ejecutar_',
            'filtrar_',
            'buscar_'
        ]
    
    def agregar_modulos_cliente(self, nombre_nora: str):
        """
        Agrega módulos específicos del cliente a la lista de módulos a escanear
        """
        # Módulos de rutas específicos del cliente
        modulos_adicionales = {
            f'panel_cliente_tareas': f'clientes.aura.routes.panel_cliente_tareas.panel_cliente_tareas',
            f'panel_cliente_contactos': f'clientes.aura.routes.panel_cliente_contactos.panel_cliente_contactos',
            f'panel_cliente_pagos': f'clientes.aura.routes.panel_cliente_pagos.panel_cliente_pagos',
            f'panel_cliente_meta_ads': f'clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads',
            f'panel_cliente_google_ads': f'clientes.aura.routes.panel_cliente_google_ads.panel_cliente_google_ads',
            f'panel_cliente_automatizaciones': f'clientes.aura.routes.panel_cliente_automatizaciones.panel_cliente_automatizaciones'
        }
        
        # Verificar cuáles módulos están activos para el cliente
        modulos_activos = self.obtener_modulos_activos_cliente(nombre_nora)
        
        for modulo_nombre, ruta_modulo in modulos_adicionales.items():
            modulo_corto = modulo_nombre.replace('panel_cliente_', '')
            if modulo_corto in modulos_activos:
                self.modulos_base[modulo_nombre] = ruta_modulo
                print(f"➕ Agregado módulo del cliente: {modulo_nombre}")
    
    def crear_tabla_funciones_automatizables(self):
        """
        Crea la tabla para almacenar las funciones automatizables
        """
        try:
            # Nota: Esta función solo documenta la estructura
            # La tabla debe crearse manualmente en Supabase
            sql_crear_tabla = """
            CREATE TABLE IF NOT EXISTS funciones_automatizables (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                modulo TEXT NOT NULL,
                nombre_funcion TEXT NOT NULL,
                descripcion TEXT,
                parametros JSONB,
                docstring TEXT,
                es_automatizable BOOLEAN DEFAULT true,
                activa BOOLEAN DEFAULT true,
                categoria TEXT,
                envia_notificacion BOOLEAN DEFAULT false,
                ejemplo_uso JSONB,
                codigo_fuente TEXT,
                linea_inicio INTEGER,
                ruta_modulo_python TEXT,
                tipo_archivo TEXT,
                archivo_origen TEXT,
                ruta_completa TEXT,
                metodo_deteccion TEXT,
                creado_en TIMESTAMP WITH TIME ZONE DEFAULT now(),
                actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT now(),
                UNIQUE(modulo, nombre_funcion)
            );
            """
            
            print("📝 SQL para crear la tabla:")
            print(sql_crear_tabla)
            print("\n🔧 Ejecuta este SQL en Supabase para crear la tabla")
            
        except Exception as e:
            print(f"❌ Error al mostrar SQL de tabla: {e}")
    
    def extraer_info_funcion(self, modulo_obj, nombre_funcion: str) -> Optional[Dict[str, Any]]:
        """
        Extrae información detallada de una función
        """
        try:
            funcion = getattr(modulo_obj, nombre_funcion)
            
            if not callable(funcion):
                return None
            
            # Obtener signature y parámetros
            try:
                sig = inspect.signature(funcion)
                parametros = {}
                
                for param_name, param in sig.parameters.items():
                    param_info = {
                        'tipo': str(param.annotation) if param.annotation != inspect.Parameter.empty else 'Any',
                        'requerido': param.default == inspect.Parameter.empty,
                        'valor_defecto': str(param.default) if param.default != inspect.Parameter.empty else None
                    }
                    parametros[param_name] = param_info
                    
            except Exception:
                parametros = {}
            
            # Obtener docstring
            docstring = inspect.getdoc(funcion) or ""
            
            # Extraer descripción (primera línea del docstring)
            descripcion = docstring.split('\n')[0] if docstring else nombre_funcion
            
            # Determinar categoría basada en el nombre
            categoria = self.determinar_categoria(nombre_funcion)
            
            # Determinar si envía notificaciones
            envia_notificacion = self.determinar_si_envia_notificacion(nombre_funcion, docstring)
            
            # Crear ejemplo de uso
            ejemplo_uso = self.generar_ejemplo_uso(nombre_funcion, parametros)
            
            return {
                'nombre_funcion': nombre_funcion,
                'descripcion': descripcion,
                'parametros': parametros,
                'docstring': docstring,
                'categoria': categoria,
                'envia_notificacion': envia_notificacion,
                'ejemplo_uso': ejemplo_uso,
                'es_automatizable': self.es_automatizable(nombre_funcion)
            }
            
        except Exception as e:
            print(f"⚠️ Error al extraer info de {nombre_funcion}: {e}")
            return None
    
    def es_automatizable(self, nombre_funcion: str) -> bool:
        """
        Determina si una función es automatizable basado en su nombre
        MODO INCLUSIVO: Incluye todas las funciones excepto las claramente no automatizables
        """
        # Excluir SOLO funciones privadas o de sistema muy específicas
        if nombre_funcion.startswith('_'):
            return False
        
        # Excluir SOLO funciones muy específicas del sistema
        excluidos_estrictos = [
            'main', 'init', 'setup', 'app', 'create_app', 'register_blueprints',
            'before_request', 'after_request', 'teardown_appcontext'
        ]
        if nombre_funcion.lower() in excluidos_estrictos:
            return False
        
        # Excluir rutas de Flask específicas (que empiecen con ciertos patrones)
        patrones_excluir = ['route_', 'blueprint_', 'handler_', 'middleware_']
        for patron in patrones_excluir:
            if nombre_funcion.startswith(patron):
                return False
        
        # INCLUIR TODO LO DEMÁS - Modo super inclusivo
        # Si tiene más de 2 caracteres y no está en la lista de exclusiones, es automatizable
        if len(nombre_funcion) > 2:
            return True
        
        return False
    
    def determinar_categoria(self, nombre_funcion: str) -> str:
        """
        Determina la categoría de una función basada en su nombre
        """
        if any(nombre_funcion.startswith(p) for p in ['reporte_', 'generar_reporte']):
            return 'reportes'
        elif any(nombre_funcion.startswith(p) for p in ['enviar_', 'notificar_']):
            return 'notificaciones'
        elif any(nombre_funcion.startswith(p) for p in ['backup_', 'respaldar_']):
            return 'backup'
        elif any(nombre_funcion.startswith(p) for p in ['limpiar_', 'eliminar_']):
            return 'mantenimiento'
        elif any(nombre_funcion.startswith(p) for p in ['sincronizar_', 'actualizar_']):
            return 'sincronizacion'
        elif nombre_funcion.startswith('ejemplo_'):
            return 'ejemplos'
        else:
            return 'general'
    
    def determinar_si_envia_notificacion(self, nombre_funcion: str, docstring: str) -> bool:
        """
        Determina si una función envía notificaciones basado en su nombre y documentación
        """
        # Palabras clave en el nombre que indican notificación
        palabras_notificacion_nombre = [
            'enviar_', 'notificar_', 'alert_', 'email_', 'whatsapp_', 
            'sms_', 'mensaje_', 'avisar_', 'informar_'
        ]
        
        # Verificar nombre de función
        for palabra in palabras_notificacion_nombre:
            if palabra in nombre_funcion.lower():
                return True
        
        # Palabras clave en la documentación
        palabras_notificacion_doc = [
            'notifica', 'envía', 'alerta', 'email', 'correo', 'whatsapp', 
            'mensaje', 'sms', 'telegram', 'slack', 'webhook', 'push notification',
            'mail', 'send', 'notify', 'alert', 'message'
        ]
        
        # Verificar documentación
        if docstring:
            doc_lower = docstring.lower()
            for palabra in palabras_notificacion_doc:
                if palabra in doc_lower:
                    return True
        
        # Verificar si está en módulo de notificaciones
        return False
    
    def es_funcion_para_cliente(self, info_funcion: Dict[str, Any], nombre_nora: str) -> bool:
        """
        Determina si una función es específica para un cliente determinado
        """
        # Por ahora, todas las funciones son genéricas, pero se puede extender
        # para filtrar funciones específicas por cliente
        
        nombre_funcion = info_funcion.get('nombre_funcion', '')
        modulo = info_funcion.get('modulo', '')
        
        # Funciones que contienen el nombre del cliente
        if nombre_nora.lower() in nombre_funcion.lower():
            return True
        
        # Funciones específicas de módulos del cliente
        modulos_cliente = self.obtener_modulos_activos_cliente(nombre_nora)
        if modulo in modulos_cliente:
            return True
        
        # Por defecto, todas las funciones son válidas para cualquier cliente
        return True
    
    def obtener_modulos_activos_cliente(self, nombre_nora: str) -> List[str]:
        """
        Obtiene la lista de módulos activos para un cliente específico desde Supabase
        """
        try:
            response = supabase.table("configuracion_bot") \
                .select("modulos") \
                .eq("nombre_nora", nombre_nora) \
                .execute()
            
            if response.data:
                modulos = response.data[0].get('modulos', [])
                if isinstance(modulos, list):
                    return modulos
                elif isinstance(modulos, dict):
                    return list(modulos.keys())
            
            return []
            
        except Exception as e:
            print(f"⚠️ Error al obtener módulos activos para {nombre_nora}: {e}")
            return []
    
    def generar_ejemplo_uso(self, nombre_funcion: str, parametros: Dict) -> Dict[str, Any]:
        """
        Genera un ejemplo de uso para la función
        """
        ejemplo = {
            'modulo': None,  # Se llenará al registrar
            'funcion': nombre_funcion,
            'parametros': {}
        }
        
        # Generar valores de ejemplo para parámetros
        for param_name, param_info in parametros.items():
            if param_info['requerido']:
                tipo = param_info.get('tipo', 'Any')
                
                if 'str' in tipo or tipo == 'Any':
                    ejemplo['parametros'][param_name] = f"ejemplo_{param_name}"
                elif 'int' in tipo:
                    ejemplo['parametros'][param_name] = 30
                elif 'bool' in tipo:
                    ejemplo['parametros'][param_name] = True
                elif 'list' in tipo:
                    ejemplo['parametros'][param_name] = []
                elif 'dict' in tipo:
                    ejemplo['parametros'][param_name] = {}
                else:
                    ejemplo['parametros'][param_name] = f"valor_{param_name}"
        
        return ejemplo
    
    def escanear_archivos_js(self, directorio_base: str, nombre_modulo: str) -> List[Dict[str, Any]]:
        """
        Escanea archivos JavaScript en busca de funciones automatizables
        """
        import os
        import re
        
        funciones_encontradas = []
        
        try:
            # Buscar archivos .js en el directorio
            for root, dirs, files in os.walk(directorio_base):
                for file in files:
                    if file.endswith('.js'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                                # Buscar funciones con expresiones regulares
                                # Patrones para function, async function, arrow functions
                                patterns = [
                                    r'function\s+(\w+)\s*\(',
                                    r'async\s+function\s+(\w+)\s*\(',
                                    r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',
                                    r'let\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',
                                    r'var\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',
                                    r'const\s+(\w+)\s*=\s*async\s*\([^)]*\)\s*=>\s*{',
                                    r'(\w+):\s*function\s*\(',
                                    r'(\w+):\s*async\s*function\s*\('
                                ]
                                
                                for pattern in patterns:
                                    matches = re.findall(pattern, content, re.MULTILINE)
                                    for match in matches:
                                        nombre_funcion = match
                                        if self.es_automatizable(nombre_funcion):
                                            # Buscar comentarios o documentación cerca de la función
                                            descripcion = self.extraer_descripcion_js(content, nombre_funcion)
                                            
                                            info_funcion = {
                                                'nombre_funcion': nombre_funcion,
                                                'descripcion': descripcion or f"Función JavaScript: {nombre_funcion}",
                                                'parametros': {},  # Sería complejo extraer parámetros de JS
                                                'docstring': descripcion or "",
                                                'categoria': self.determinar_categoria(nombre_funcion),
                                                'envia_notificacion': self.determinar_si_envia_notificacion(nombre_funcion, descripcion or ""),
                                                'ejemplo_uso': {
                                                    'modulo': nombre_modulo,
                                                    'funcion': nombre_funcion,
                                                    'parametros': {},
                                                    'tipo': 'javascript',
                                                    'archivo': file
                                                },
                                                'es_automatizable': True,
                                                'modulo': nombre_modulo,
                                                'tipo_archivo': 'javascript',
                                                'archivo_origen': file
                                            }
                                            
                                            funciones_encontradas.append(info_funcion)
                                            print(f"  ✅ {nombre_funcion} (JS) - {info_funcion['categoria']}")
                        
                        except Exception as e:
                            print(f"⚠️ Error leyendo {file}: {e}")
            
        except Exception as e:
            print(f"❌ Error escaneando archivos JS: {e}")
        
        return funciones_encontradas
    
    def extraer_descripcion_js(self, content: str, nombre_funcion: str) -> str:
        """
        Extrae descripción de una función JavaScript desde comentarios
        """
        import re
        
        # Buscar comentarios antes de la función
        pattern = rf'(//.*?\n|/\*.*?\*/)\s*.*?{re.escape(nombre_funcion)}'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            comment = match.group(1).strip()
            # Limpiar comentarios
            comment = re.sub(r'^(//|/\*|\*/)', '', comment, flags=re.MULTILINE)
            comment = comment.strip()
            return comment[:200]  # Limitar longitud
        
        return ""
    
    def escanear_archivos_python_directamente(self, directorio: str, nombre_modulo: str) -> List[Dict[str, Any]]:
        """
        Escanea archivos Python directamente buscando funciones def (como diagnostico_modulos)
        """
        import os
        import re
        
        funciones_encontradas = []
        
        try:
            if not os.path.exists(directorio):
                print(f"⚠️ Directorio no existe: {directorio}")
                return funciones_encontradas
                
            print(f"📁 Escaneando directorio: {directorio}")
            
            # Recorrer todos los archivos Python en el directorio
            for root, dirs, files in os.walk(directorio):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                                # Buscar todas las funciones def con regex
                                pattern = r'^def\s+(\w+)\s*\([^)]*\):'
                                matches = re.findall(pattern, content, re.MULTILINE)
                                
                                for nombre_funcion in matches:
                                    if self.es_automatizable(nombre_funcion):
                                        # Extraer docstring básico
                                        docstring = self.extraer_docstring_simple(content, nombre_funcion)
                                        descripcion = docstring.split('\n')[0] if docstring else f"Función {nombre_funcion}"
                                        
                                        # Extraer parámetros básicos
                                        parametros = self.extraer_parametros_simple(content, nombre_funcion)
                                        
                                        # NUEVO: Extraer el código fuente completo de la función
                                        codigo_fuente = self.extraer_codigo_funcion_completo(content, nombre_funcion)
                                        linea_inicio = self.obtener_linea_funcion(content, nombre_funcion)
                                        
                                        # Convertir ruta de archivo a ruta de módulo Python
                                        ruta_modulo_python = self.convertir_ruta_a_modulo(file_path)
                                        
                                        info_funcion = {
                                            'nombre_funcion': nombre_funcion,
                                            'descripcion': descripcion,
                                            'parametros': parametros,
                                            'docstring': docstring,
                                            'categoria': self.determinar_categoria(nombre_funcion),
                                            'envia_notificacion': self.determinar_si_envia_notificacion(nombre_funcion, docstring),
                                            'ejemplo_uso': {
                                                'modulo': nombre_modulo,
                                                'funcion': nombre_funcion,
                                                'parametros': {k: f"ejemplo_{k}" for k, v in parametros.items() if v.get('requerido', True)},
                                                'archivo': file
                                            },
                                            'es_automatizable': True,
                                            'modulo': nombre_modulo,
                                            'tipo_archivo': 'python',
                                            'archivo_origen': file,
                                            'ruta_completa': file_path,
                                            'ruta_modulo_python': ruta_modulo_python,
                                            'linea_inicio': linea_inicio,
                                            'codigo_fuente': codigo_fuente,
                                            'metodo_deteccion': 'escaneo_directo'
                                        }
                                        
                                        funciones_encontradas.append(info_funcion)
                                        emoji_notif = "📧" if info_funcion['envia_notificacion'] else ""
                                        print(f"  ✅ {nombre_funcion} ({file}) - {info_funcion['categoria']} {emoji_notif}")
                        
                        except Exception as e:
                            print(f"⚠️ Error leyendo {file}: {e}")
            
        except Exception as e:
            print(f"❌ Error escaneando directorio {directorio}: {e}")
        
        return funciones_encontradas
    
    def extraer_docstring_simple(self, content: str, nombre_funcion: str) -> str:
        """
        Extrae el docstring de una función usando regex simple
        """
        import re
        
        # Buscar el docstring después de la definición de la función
        pattern = rf'def\s+{re.escape(nombre_funcion)}\s*\([^)]*\):\s*"""([^"]*?)"""'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        # Buscar docstring con comillas simples
        pattern = rf"def\s+{re.escape(nombre_funcion)}\s*\([^)]*\):\s*'''([^']*?)'''"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        return ""
    
    def extraer_parametros_simple(self, content: str, nombre_funcion: str) -> Dict[str, Any]:
        """
        Extrae parámetros de una función usando regex simple
        """
        import re
        
        # Buscar la definición de la función y sus parámetros
        pattern = rf'def\s+{re.escape(nombre_funcion)}\s*\(([^)]*)\):'
        match = re.search(pattern, content)
        
        if match:
            param_string = match.group(1).strip()
            if not param_string:
                return {}
            
            parametros = {}
            # Dividir parámetros por coma (simple)
            params = [p.strip() for p in param_string.split(',')]
            
            for param in params:
                if param and param != 'self':
                    # Extraer nombre del parámetro (antes de = o :)
                    param_name = param.split('=')[0].split(':')[0].strip()
                    if param_name:
                        parametros[param_name] = {
                            'tipo': 'Any',
                            'requerido': '=' not in param,
                            'valor_defecto': param.split('=')[1].strip() if '=' in param else None
                        }
            
            return parametros
        
        return {}
    
    def extraer_codigo_funcion_completo(self, content: str, nombre_funcion: str) -> str:
        """
        Extrae el código fuente completo de una función incluyendo def y todo su cuerpo
        """
        try:
            lines = content.split('\n')
            func_start = None
            func_end = None
            base_indent = None
            
            # Buscar el inicio de la función
            for i, line in enumerate(lines):
                if re.match(rf'^\s*def\s+{re.escape(nombre_funcion)}\s*\(', line):
                    func_start = i
                    # Determinar la indentación base de la función
                    base_indent = len(line) - len(line.lstrip())
                    break
            
            if func_start is None:
                return f"# Función {nombre_funcion} no encontrada"
            
            # Buscar el final de la función
            for i in range(func_start + 1, len(lines)):
                line = lines[i]
                
                # Si encontramos una línea vacía, continuar
                if not line.strip():
                    continue
                
                # Si encontramos una línea con comentario al mismo nivel o menos indentada, continuar
                if line.strip().startswith('#') and base_indent is not None and len(line) - len(line.lstrip()) <= base_indent:
                    continue
                
                # Si encontramos código con indentación menor o igual a la función, terminamos
                if line.strip() and base_indent is not None and len(line) - len(line.lstrip()) <= base_indent:
                    # A menos que sea una continuación de decoradores o docstrings
                    if not (line.strip().startswith('@') or line.strip().startswith('"""') or line.strip().startswith("'''")):
                        func_end = i
                        break
            
            # Si no encontramos final, tomar hasta el final del archivo
            if func_end is None:
                func_end = len(lines)
            
            # Extraer las líneas de la función
            func_lines = lines[func_start:func_end]
            return '\n'.join(func_lines)
            
        except Exception as e:
            return f"# Error extrayendo código de {nombre_funcion}: {e}"
    
    def obtener_linea_funcion(self, content: str, nombre_funcion: str) -> int:
        """
        Obtiene el número de línea donde empieza la función
        """
        try:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if re.match(rf'^\s*def\s+{re.escape(nombre_funcion)}\s*\(', line):
                    return i + 1  # Las líneas empiezan en 1, no en 0
            return 0
        except:
            return 0
    
    def convertir_ruta_a_modulo(self, file_path: str) -> str:
        """
        Convierte una ruta de archivo a ruta de módulo Python
        Ej: clientes/aura/routes/panel_cliente_meta_ads/panel_cliente_meta_ads.py
        -> clientes.aura.routes.panel_cliente_meta_ads.panel_cliente_meta_ads
        """
        try:
            # Normalizar la ruta y remover la extensión .py
            ruta = file_path.replace('\\', '/').replace('.py', '')
            
            # Convertir barras a puntos
            ruta_modulo = ruta.replace('/', '.')
            
            # Remover el directorio base si es necesario
            if ruta_modulo.startswith('./'):
                ruta_modulo = ruta_modulo[2:]
            
            return ruta_modulo
        except:
            return file_path
    
    def escanear_modulo(self, nombre_modulo: str, ruta_modulo: str) -> List[Dict[str, Any]]:
        """
        Escanea un módulo usando AMBOS métodos: importación y escaneo directo de archivos
        """
        funciones_encontradas = []
        
        try:
            print(f"🔍 Escaneando módulo: {nombre_modulo} (modo híbrido)")
            
            # MÉTODO 1: Escaneo directo de archivos (como diagnostico_modulos)
            if nombre_modulo in self.directorios_modulos:
                directorio = self.directorios_modulos[nombre_modulo]
                funciones_directas = self.escanear_archivos_python_directamente(directorio, nombre_modulo)
                funciones_encontradas.extend(funciones_directas)
                print(f"  📁 Archivos directos: {len(funciones_directas)} funciones")
            
            # MÉTODO 2: Importación tradicional (para utils)
            try:
                # Importar el módulo Python silenciosamente
                import sys
                from io import StringIO
                
                # Capturar la salida para evitar logs de inicialización
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                sys.stdout = StringIO()
                sys.stderr = StringIO()
                
                try:
                    modulo = importlib.import_module(ruta_modulo)
                    
                    # Obtener funciones del módulo importado
                    for nombre_attr in dir(modulo):
                        if not nombre_attr.startswith('__'):  # Solo excluir dunders
                            try:
                                attr = getattr(modulo, nombre_attr)
                                
                                # Verificar si es una función
                                if callable(attr) and (inspect.isfunction(attr) or inspect.ismethod(attr)):
                                    # Verificar origen del módulo
                                    modulo_origen = getattr(attr, '__module__', '')
                                    
                                    # Incluir si viene de este módulo
                                    if (modulo_origen == ruta_modulo or 
                                        ruta_modulo in modulo_origen or
                                        nombre_modulo in modulo_origen):
                                        
                                        # Verificar que no esté duplicada
                                        ya_existe = any(f['nombre_funcion'] == nombre_attr for f in funciones_encontradas)
                                        
                                        if not ya_existe and self.es_automatizable(nombre_attr):
                                            info_funcion = self.extraer_info_funcion(modulo, nombre_attr)
                                            
                                            if info_funcion:
                                                info_funcion['modulo'] = nombre_modulo
                                                info_funcion['ejemplo_uso']['modulo'] = nombre_modulo
                                                info_funcion['tipo_archivo'] = 'python'
                                                info_funcion['metodo_deteccion'] = 'importacion'
                                                
                                                # Verificar notificaciones
                                                if nombre_modulo == 'notificaciones' and not info_funcion['envia_notificacion']:
                                                    info_funcion['envia_notificacion'] = True
                                                
                                                funciones_encontradas.append(info_funcion)
                                                emoji_notif = "📧" if info_funcion['envia_notificacion'] else ""
                                                print(f"  ✅ {nombre_attr} (import) - {info_funcion['categoria']} {emoji_notif}")
                            
                            except Exception as e:
                                continue
                                
                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                    
                print(f"  🔗 Importación: {len([f for f in funciones_encontradas if f.get('metodo_deteccion') == 'importacion'])} funciones")
                
            except Exception as e:
                print(f"⚠️ Error en importación de {ruta_modulo}: {e}")
            
            print(f"  📊 Total encontradas: {len(funciones_encontradas)}")
            
        except Exception as e:
            print(f"❌ Error al escanear {nombre_modulo}: {e}")
        
        return funciones_encontradas
    
    def registrar_funciones_en_bd(self, funciones: List[Dict[str, Any]]):
        """
        Registra las funciones en la base de datos
        """
        try:
            print("💾 Registrando funciones en la base de datos...")
            
            for funcion in funciones:
                # Verificar si ya existe
                response_existente = supabase.table("funciones_automatizables") \
                    .select("id") \
                    .eq("modulo", funcion['modulo']) \
                    .eq("nombre_funcion", funcion['nombre_funcion']) \
                    .execute()
                
                datos_funcion = {
                    'modulo': funcion['modulo'],
                    'nombre_funcion': funcion['nombre_funcion'],
                    'descripcion': funcion['descripcion'],
                    'parametros': funcion['parametros'],
                    'docstring': funcion['docstring'],
                    'es_automatizable': funcion['es_automatizable'],
                    'categoria': funcion['categoria'],
                    'envia_notificacion': funcion['envia_notificacion'],
                    'ejemplo_uso': funcion['ejemplo_uso'],
                    'activa': True,
                    'actualizado_en': datetime.now().isoformat()
                }
                
                # Agregar campos nuevos si existen
                if 'codigo_fuente' in funcion:
                    datos_funcion['codigo_fuente'] = funcion['codigo_fuente']
                if 'linea_inicio' in funcion:
                    datos_funcion['linea_inicio'] = funcion['linea_inicio']
                if 'ruta_modulo_python' in funcion:
                    datos_funcion['ruta_modulo_python'] = funcion['ruta_modulo_python']
                if 'tipo_archivo' in funcion:
                    datos_funcion['tipo_archivo'] = funcion['tipo_archivo']
                if 'archivo_origen' in funcion:
                    datos_funcion['archivo_origen'] = funcion['archivo_origen']
                if 'ruta_completa' in funcion:
                    datos_funcion['ruta_completa'] = funcion['ruta_completa']
                if 'metodo_deteccion' in funcion:
                    datos_funcion['metodo_deteccion'] = funcion['metodo_deteccion']
                
                if response_existente.data:
                    # Actualizar existente
                    supabase.table("funciones_automatizables") \
                        .update(datos_funcion) \
                        .eq("modulo", funcion['modulo']) \
                        .eq("nombre_funcion", funcion['nombre_funcion']) \
                        .execute()
                    print(f"  🔄 Actualizada: {funcion['modulo']}.{funcion['nombre_funcion']}")
                else:
                    # Insertar nueva
                    datos_funcion['creado_en'] = datetime.now().isoformat()
                    supabase.table("funciones_automatizables") \
                        .insert(datos_funcion) \
                        .execute()
                    print(f"  ➕ Insertada: {funcion['modulo']}.{funcion['nombre_funcion']}")
            
            print(f"✅ {len(funciones)} funciones registradas correctamente")
            
        except Exception as e:
            print(f"❌ Error al registrar funciones: {e}")
    
    def ejecutar_descubrimiento_completo(self, nombre_nora: Optional[str] = None):
        """
        Ejecuta el proceso completo de descubrimiento
        """
        print("🤖 Iniciando descubrimiento automático de funciones...")
        
        if nombre_nora:
            print(f"👤 Cliente específico: {nombre_nora}")
            self.agregar_modulos_cliente(nombre_nora)
        
        print("=" * 60)
        
        todas_las_funciones = []
        
        for nombre_modulo, ruta_modulo in self.modulos_base.items():
            funciones_modulo = self.escanear_modulo(nombre_modulo, ruta_modulo)
            
            # Filtrar por cliente si se especifica
            if nombre_nora:
                funciones_filtradas = []
                for func in funciones_modulo:
                    if self.es_funcion_para_cliente(func, nombre_nora):
                        funciones_filtradas.append(func)
                funciones_modulo = funciones_filtradas
                
            todas_las_funciones.extend(funciones_modulo)
        
        print("\n" + "=" * 60)
        print(f"📊 RESUMEN:")
        print(f"   Total de funciones encontradas: {len(todas_las_funciones)}")
        
        if nombre_nora:
            print(f"   Filtradas para cliente: {nombre_nora}")
        
        # Agrupar por categoría
        categorias = {}
        for func in todas_las_funciones:
            cat = func['categoria']
            if cat not in categorias:
                categorias[cat] = []
            categorias[cat].append(func)
        
        for categoria, funcs in categorias.items():
            print(f"   {categoria.title()}: {len(funcs)} funciones")
        
        # Registrar en BD
        if todas_las_funciones:
            print("\n💾 Registrando en base de datos...")
            self.registrar_funciones_en_bd(todas_las_funciones)
        
        print("=" * 60)
        print("🎉 Descubrimiento completado!")
        
        return todas_las_funciones

def main():
    """
    Función principal
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Descubridor de funciones automatizables')
    parser.add_argument('--crear-tabla', action='store_true', help='Mostrar SQL para crear tabla')
    parser.add_argument('--escanear', action='store_true', help='Escanear y registrar funciones')
    parser.add_argument('--modulo', type=str, help='Escanear un módulo específico')
    parser.add_argument('--nora', type=str, help='Nombre del cliente (para filtrar por cliente específico)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Mostrar información detallada')
    parser.add_argument('--silencioso', '-s', action='store_true', help='Modo silencioso (solo resultados)')
    parser.add_argument('--agregar-manual', action='store_true', help='Agregar funciones manualmente por módulo')
    
    args = parser.parse_args()
    
    descubridor = DescubrirFunciones()
    
    if args.crear_tabla:
        descubridor.crear_tabla_funciones_automatizables()
    elif args.agregar_manual:
        agregar_funciones_manualmente(descubridor, args.nora)
    elif args.escanear:
        # Configurar modo silencioso
        if args.silencioso:
            import sys
            from io import StringIO
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                resultado = ejecutar_escaneo(descubridor, args)
            finally:
                sys.stdout = old_stdout
            print(f"✅ Escaneo completado. {resultado} funciones procesadas.")
        else:
            ejecutar_escaneo(descubridor, args)
    else:
        print("🤖 Descubridor de Funciones Automatizables")
        print("=" * 60)
        print("Uso:")
        print("  python descubrir_funciones.py --crear-tabla")
        print("  python descubrir_funciones.py --escanear")
        print("  python descubrir_funciones.py --escanear --silencioso")
        print("  python descubrir_funciones.py --escanear --modulo automatizaciones_ejecutor")
        print("  python descubrir_funciones.py --escanear --modulo notificaciones --nora aura")
        print("  python descubrir_funciones.py --escanear --nora aura")
        print("  python descubrir_funciones.py --agregar-manual --nora aura")
        print("")
        print("📋 Módulos disponibles:")
        for modulo in descubridor.modulos_base.keys():
            print(f"  - {modulo}")
        print("")
        print("👤 Clientes disponibles: aura, [otros...]")

def ejecutar_escaneo(descubridor, args):
    """Ejecuta el escaneo basado en los argumentos"""
    if args.modulo:
        if args.modulo in descubridor.modulos_base:
            print(f"🔍 Escaneando módulo específico: {args.modulo}")
            if args.nora:
                print(f"👤 Para cliente: {args.nora}")
            
            funciones = descubridor.escanear_modulo(args.modulo, descubridor.modulos_base[args.modulo])
            if funciones:
                # Filtrar por cliente si se especifica
                if args.nora:
                    funciones_filtradas = []
                    for func in funciones:
                        # Verificar si la función es específica del cliente
                        if descubridor.es_funcion_para_cliente(func, args.nora):
                            funciones_filtradas.append(func)
                    print(f"📊 Funciones encontradas para {args.nora}: {len(funciones_filtradas)}")
                    funciones = funciones_filtradas
                
                if funciones:
                    descubridor.registrar_funciones_en_bd(funciones)
                    return len(funciones)
                else:
                    print("ℹ️ No se encontraron funciones para el cliente especificado")
                    return 0
            else:
                print("⚠️ No se encontraron funciones en el módulo")
                return 0
        else:
            print(f"❌ Módulo '{args.modulo}' no encontrado en la lista de módulos base")
            print("📋 Módulos disponibles:", list(descubridor.modulos_base.keys()))
            return 0
    else:
        if args.nora:
            print(f"🔍 Escaneando todos los módulos para cliente: {args.nora}")
            funciones = descubridor.ejecutar_descubrimiento_completo(args.nora)
        else:
            funciones = descubridor.ejecutar_descubrimiento_completo()
        return len(funciones) if funciones else 0

def agregar_funciones_manualmente(descubridor, nombre_nora=None):
    """
    Permite agregar funciones manualmente por módulo
    """
    print("📝 Agregando funciones manualmente...")
    
    # Definir funciones conocidas por módulo
    funciones_por_modulo = {
        'meta_ads': [
            {
                'nombre_funcion': 'sincronizar_cuentas_publicitarias',
                'descripcion': 'Sincroniza las cuentas publicitarias de Meta Ads',
                'categoria': 'sincronizacion',
                'envia_notificacion': False,
                'parametros': {'access_token': {'tipo': 'str', 'requerido': True}}
            },
            {
                'nombre_funcion': 'obtener_metricas_campañas',
                'descripcion': 'Obtiene métricas de rendimiento de las campañas',
                'categoria': 'reportes',
                'envia_notificacion': False,
                'parametros': {'account_id': {'tipo': 'str', 'requerido': True}, 'fecha_inicio': {'tipo': 'str', 'requerido': True}}
            },
            {
                'nombre_funcion': 'generar_reporte_gastos',
                'descripcion': 'Genera reporte de gastos publicitarios',
                'categoria': 'reportes',
                'envia_notificacion': True,
                'parametros': {'periodo': {'tipo': 'str', 'requerido': True}}
            }
        ],
        'google_ads': [
            {
                'nombre_funcion': 'sincronizar_campañas_google',
                'descripcion': 'Sincroniza campañas de Google Ads',
                'categoria': 'sincronizacion',
                'envia_notificacion': False,
                'parametros': {'customer_id': {'tipo': 'str', 'requerido': True}}
            },
            {
                'nombre_funcion': 'obtener_datos_rendimiento',
                'descripcion': 'Obtiene datos de rendimiento de Google Ads',
                'categoria': 'reportes',
                'envia_notificacion': False,
                'parametros': {'campaign_id': {'tipo': 'str', 'requerido': True}}
            }
        ],
        'notificaciones': [
            {
                'nombre_funcion': 'enviar_reporte_whatsapp',
                'descripcion': 'Envía reporte por WhatsApp',
                'categoria': 'notificaciones',
                'envia_notificacion': True,
                'parametros': {'mensaje': {'tipo': 'str', 'requerido': True}, 'telefono': {'tipo': 'str', 'requerido': True}}
            },
            {
                'nombre_funcion': 'enviar_email_resumen',
                'descripcion': 'Envía resumen por email',
                'categoria': 'notificaciones',
                'envia_notificacion': True,
                'parametros': {'destinatario': {'tipo': 'str', 'requerido': True}, 'asunto': {'tipo': 'str', 'requerido': True}}
            }
        ],
        'tareas': [
            {
                'nombre_funcion': 'crear_tarea_automatica',
                'descripcion': 'Crea una tarea automáticamente',
                'categoria': 'general',
                'envia_notificacion': False,
                'parametros': {'titulo': {'tipo': 'str', 'requerido': True}, 'descripcion': {'tipo': 'str', 'requerido': False}}
            },
            {
                'nombre_funcion': 'marcar_tareas_vencidas',
                'descripcion': 'Marca tareas vencidas como pendientes',
                'categoria': 'mantenimiento',
                'envia_notificacion': True,
                'parametros': {}
            }
        ]
    }
    
    total_agregadas = 0
    
    for modulo, funciones in funciones_por_modulo.items():
        print(f"\n📦 Procesando módulo: {modulo}")
        
        for func_def in funciones:
            # Crear función completa
            funcion_completa = {
                'modulo': modulo,
                'nombre_funcion': func_def['nombre_funcion'],
                'descripcion': func_def['descripcion'],
                'parametros': func_def['parametros'],
                'docstring': func_def['descripcion'],
                'es_automatizable': True,
                'categoria': func_def['categoria'],
                'envia_notificacion': func_def['envia_notificacion'],
                'ejemplo_uso': {
                    'modulo': modulo,
                    'funcion': func_def['nombre_funcion'],
                    'parametros': {k: f"ejemplo_{k}" for k, v in func_def['parametros'].items() if v['requerido']}
                },
                'activa': True
            }
            
            # Filtrar por cliente si se especifica
            if nombre_nora and not descubridor.es_funcion_para_cliente(funcion_completa, nombre_nora):
                continue
                
            print(f"  ➕ {func_def['nombre_funcion']} - {func_def['categoria']}")
            total_agregadas += 1
    
    # Registrar todas las funciones
    todas_funciones = []
    for modulo, funciones in funciones_por_modulo.items():
        for func_def in funciones:
            funcion_completa = {
                'modulo': modulo,
                'nombre_funcion': func_def['nombre_funcion'],
                'descripcion': func_def['descripcion'],
                'parametros': func_def['parametros'],
                'docstring': func_def['descripcion'],
                'es_automatizable': True,
                'categoria': func_def['categoria'],
                'envia_notificacion': func_def['envia_notificacion'],
                'ejemplo_uso': {
                    'modulo': modulo,
                    'funcion': func_def['nombre_funcion'],
                    'parametros': {k: f"ejemplo_{k}" for k, v in func_def['parametros'].items() if v['requerido']}
                },
                'activa': True
            }
            
            if not nombre_nora or descubridor.es_funcion_para_cliente(funcion_completa, nombre_nora):
                todas_funciones.append(funcion_completa)
    
    if todas_funciones:
        descubridor.registrar_funciones_en_bd(todas_funciones)
        print(f"\n✅ {len(todas_funciones)} funciones agregadas manualmente")
    else:
        print("\n⚠️ No se agregaron funciones")
        
    return len(todas_funciones)

if __name__ == "__main__":
    main()
