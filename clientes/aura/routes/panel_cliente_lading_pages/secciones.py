"""
📊 SCHEMAS DE BD QUE USA ESTE ARCHIVO:

📋 TABLAS PRINCIPALES:
• landing_pages_config: Configuración principal de landing pages
  └ Campos: id(bigint), nombre_nora(varchar), titulo(varchar), subtitulo(text), 
            cta_texto(varchar), cta_url(varchar), color_primario(varchar), 
            color_secundario(varchar), color_texto(varchar), bloques(json),
            seo_descripcion(text), seo_keywords(text), publicada(boolean)

• landing_pages_bloques: Bloques/secciones personalizadas  
  └ Campos: id(bigint), config_id(bigint), tipo_bloque(varchar), titulo(varchar),
            subtitulo(text), contenido(json), orden(integer), visible(boolean)

• configuracion_bot: Config de cada Nora (OBLIGATORIO EN TODOS LOS MÓDULOS)
  └ Campos: nombre_nora(text), modulos(json), ia_activa(boolean)

🔗 RELACIONES:
• landing_pages_config -> configuracion_bot via nombre_nora
• landing_pages_bloques -> landing_pages_config via config_id

💡 VERIFICAR SCHEMAS:
from clientes.aura.utils.quick_schemas import existe, columnas
if existe('landing_pages_config'):
    campos = columnas('landing_pages_config')
    # Resultado: ['id', 'nombre_nora', 'titulo', 'subtitulo', ...]
"""

from typing import Dict, Any, List, Optional
import json

# Catálogo de bloques disponibles
_CATALOGO_BLOQUES = {
    'hero': {
        'nombre': 'Hero / Encabezado',
        'descripcion': 'Sección principal con título, subtítulo y llamada a la acción',
        'icono': '🎯',
        'campos': ['titulo', 'subtitulo', 'cta_texto', 'cta_url', 'imagen_fondo']
    },
    'caracteristicas': {
        'nombre': 'Características',
        'descripcion': 'Lista de características o beneficios con iconos',
        'icono': '⭐',
        'campos': ['titulo', 'subtitulo', 'items']
    },
    'servicios': {
        'nombre': 'Servicios',
        'descripcion': 'Catálogo de servicios o productos',
        'icono': '🛍️',
        'campos': ['titulo', 'subtitulo', 'items', 'mostrar_precios']
    },
    'testimonios': {
        'nombre': 'Testimonios',
        'descripcion': 'Opiniones y casos de éxito de clientes',
        'icono': '💬',
        'campos': ['titulo', 'subtitulo', 'items']
    },
    'contacto': {
        'nombre': 'Contacto',
        'descripcion': 'Formulario de contacto y información',
        'icono': '📞',
        'campos': ['titulo', 'subtitulo', 'mostrar_formulario', 'info_contacto']
    },
    'galeria': {
        'nombre': 'Galería',
        'descripcion': 'Galería de imágenes o portafolio',
        'icono': '🖼️',
        'campos': ['titulo', 'subtitulo', 'imagenes', 'columnas']
    },
    'precios': {
        'nombre': 'Planes y Precios',
        'descripcion': 'Tabla de precios y planes',
        'icono': '💰',
        'campos': ['titulo', 'subtitulo', 'planes', 'destacar_plan']
    },
    'faq': {
        'nombre': 'Preguntas Frecuentes',
        'descripcion': 'Sección de preguntas y respuestas',
        'icono': '❓',
        'campos': ['titulo', 'subtitulo', 'preguntas']
    }
}

# Configuración por defecto
_DEFAULT_CONFIG = {
    'titulo': 'Bienvenido a Nuestro Sitio',
    'subtitulo': 'Ofrecemos soluciones increíbles para tu negocio',
    'cta': {
        'texto': 'Contáctanos',
        'url': '#contacto'
    },
    'colores': {
        'primario': '#3B82F6',
        'secundario': '#1E40AF', 
        'texto': '#1F2937'
    },
    'bloques': ['hero', 'caracteristicas', 'servicios', 'testimonios', 'contacto'],
    'seo': {
        'descripcion': 'Página de aterrizaje profesional para generar leads y conversiones',
        'keywords': 'landing page, conversiones, leads, marketing digital'
    }
}

def obtener_config_landing(nombre_nora: str) -> Dict[str, Any]:
    """
    Obtiene la configuración de landing page para una Nora específica
    """
    try:
        from clientes.aura.utils.supabase_client import supabase
        from clientes.aura.utils.quick_schemas import existe
        
        # Verificar que las tablas existan
        if not existe('landing_pages_config'):
            print(f"⚠️ Tabla landing_pages_config no existe, usando defaults")
            config = _DEFAULT_CONFIG.copy()
            config['nombre_nora'] = nombre_nora
            return config
        
        # Obtener configuración desde Supabase
        result = supabase.table('landing_pages_config') \
            .select('*') \
            .eq('nombre_nora', nombre_nora) \
            .eq('activa', True) \
            .single() \
            .execute()
        
        if result.data:
            data = result.data
            
            # Convertir datos de BD a formato esperado
            config = {
                'id': data.get('id'),
                'nombre_nora': nombre_nora,
                'titulo': data.get('titulo', _DEFAULT_CONFIG['titulo']),
                'subtitulo': data.get('subtitulo', _DEFAULT_CONFIG['subtitulo']),
                'cta': {
                    'texto': data.get('cta_texto', _DEFAULT_CONFIG['cta']['texto']),
                    'url': data.get('cta_url', _DEFAULT_CONFIG['cta']['url'])
                },
                'colores': {
                    'primario': data.get('color_primario', _DEFAULT_CONFIG['colores']['primario']),
                    'secundario': data.get('color_secundario', _DEFAULT_CONFIG['colores']['secundario']),
                    'texto': data.get('color_texto', _DEFAULT_CONFIG['colores']['texto'])
                },
                'bloques': data.get('bloques', _DEFAULT_CONFIG['bloques']),
                'seo': {
                    'descripcion': data.get('seo_descripcion', _DEFAULT_CONFIG['seo']['descripcion']),
                    'keywords': data.get('seo_keywords', _DEFAULT_CONFIG['seo']['keywords'])
                },
                'publicada': data.get('publicada', False),
                'creada_en': data.get('creada_en'),
                'actualizada_en': data.get('actualizada_en')
            }
            
            print(f"✅ Configuración obtenida desde BD para {nombre_nora}")
            return config
        else:
            print(f"⚠️ No hay configuración para {nombre_nora}, usando defaults")
            config = _DEFAULT_CONFIG.copy()
            config['nombre_nora'] = nombre_nora
            return config
            
    except Exception as e:
        print(f"❌ Error obteniendo configuración para {nombre_nora}: {e}")
        # Fallback a configuración por defecto
        config = _DEFAULT_CONFIG.copy()
        config['nombre_nora'] = nombre_nora
        return config

def guardar_config_landing(nombre_nora: str, config: Dict[str, Any]) -> bool:
    """
    Guarda o actualiza la configuración de landing page
    """
    try:
        from clientes.aura.utils.supabase_client import supabase
        from clientes.aura.utils.quick_schemas import existe
        
        # Verificar que las tablas existan
        if not existe('landing_pages_config'):
            print(f"❌ Tabla landing_pages_config no existe")
            return False
        
        # Preparar datos para inserción/actualización
        data_config = {
            'nombre_nora': nombre_nora,
            'titulo': config.get('titulo'),
            'subtitulo': config.get('subtitulo'),
            'cta_texto': config.get('cta', {}).get('texto'),
            'cta_url': config.get('cta', {}).get('url'),
            'color_primario': config.get('colores', {}).get('primario'),
            'color_secundario': config.get('colores', {}).get('secundario'),
            'color_texto': config.get('colores', {}).get('texto'),
            'bloques': json.dumps(config.get('bloques', [])) if isinstance(config.get('bloques'), list) else config.get('bloques'),
            'seo_descripcion': config.get('seo', {}).get('descripcion'),
            'seo_keywords': config.get('seo', {}).get('keywords'),
            'publicada': config.get('publicada', False)
        }
        
        # Verificar si ya existe configuración
        existing = supabase.table('landing_pages_config') \
            .select('id') \
            .eq('nombre_nora', nombre_nora) \
            .execute()
        
        if existing.data:
            # Actualizar configuración existente
            result = supabase.table('landing_pages_config') \
                .update(data_config) \
                .eq('nombre_nora', nombre_nora) \
                .execute()
        else:
            # Crear nueva configuración
            result = supabase.table('landing_pages_config') \
                .insert(data_config) \
                .execute()
        
        if result.data:
            print(f"✅ Configuración guardada para {nombre_nora}")
            return True
        else:
            print(f"❌ Error guardando configuración para {nombre_nora}")
            return False
            
    except Exception as e:
        print(f"❌ Error guardando configuración para {nombre_nora}: {e}")
        return False

def obtener_bloques_personalizados(config_id: int) -> List[Dict[str, Any]]:
    """
    Obtiene bloques personalizados para una configuración específica
    """
    try:
        from clientes.aura.utils.supabase_client import supabase
        from clientes.aura.utils.quick_schemas import existe
        
        if not existe('landing_pages_bloques'):
            print(f"⚠️ Tabla landing_pages_bloques no existe")
            return []
        
        result = supabase.table('landing_pages_bloques') \
            .select('*') \
            .eq('config_id', config_id) \
            .eq('visible', True) \
            .order('orden') \
            .execute()
        
        if result.data:
            print(f"✅ {len(result.data)} bloques personalizados obtenidos")
            return result.data
        else:
            return []
            
    except Exception as e:
        print(f"❌ Error obteniendo bloques personalizados: {e}")
        return []

def guardar_bloque_personalizado(config_id: int, bloque: Dict[str, Any]) -> bool:
    """
    Guarda un bloque personalizado
    """
    try:
        from clientes.aura.utils.supabase_client import supabase
        from clientes.aura.utils.quick_schemas import existe
        
        if not existe('landing_pages_bloques'):
            print(f"❌ Tabla landing_pages_bloques no existe")
            return False
        
        data_bloque = {
            'config_id': config_id,
            'tipo_bloque': bloque.get('tipo'),
            'titulo': bloque.get('titulo'),
            'subtitulo': bloque.get('subtitulo'),
            'contenido': json.dumps(bloque.get('contenido', {})) if isinstance(bloque.get('contenido'), dict) else bloque.get('contenido'),
            'orden': bloque.get('orden', 0),
            'visible': bloque.get('visible', True)
        }
        
        if bloque.get('id'):
            # Actualizar bloque existente
            result = supabase.table('landing_pages_bloques') \
                .update(data_bloque) \
                .eq('id', bloque['id']) \
                .execute()
        else:
            # Crear nuevo bloque
            result = supabase.table('landing_pages_bloques') \
                .insert(data_bloque) \
                .execute()
        
        if result.data:
            print(f"✅ Bloque guardado correctamente")
            return True
        else:
            print(f"❌ Error guardando bloque")
            return False
            
    except Exception as e:
        print(f"❌ Error guardando bloque: {e}")
        return False

def obtener_catalogo_bloques() -> Dict[str, Dict[str, Any]]:
    """
    Retorna el catálogo completo de bloques disponibles
    """
    return _CATALOGO_BLOQUES.copy()

def validar_configuracion(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida la configuración de landing page
    """
    errores = []
    
    # Validaciones básicas
    if not config.get('titulo'):
        errores.append('El título es obligatorio')
    
    if len(config.get('titulo', '')) > 200:
        errores.append('El título no puede tener más de 200 caracteres')
    
    if not config.get('bloques') or not isinstance(config.get('bloques'), list):
        errores.append('Debe seleccionar al menos un bloque')
    
    # Validar CTA
    cta = config.get('cta', {})
    if cta.get('texto') and len(cta.get('texto', '')) > 100:
        errores.append('El texto del CTA no puede tener más de 100 caracteres')
    
    # Validar colores (formato hexadecimal)
    colores = config.get('colores', {})
    for color_name, color_value in colores.items():
        if color_value and not color_value.startswith('#'):
            errores.append(f'Color {color_name} debe estar en formato hexadecimal (#FFFFFF)')
        if color_value and len(color_value) != 7:
            errores.append(f'Color {color_name} debe tener 7 caracteres (#FFFFFF)')
    
    # Validar bloques contra catálogo
    bloques_invalidos = []
    for bloque in config.get('bloques', []):
        if bloque not in _CATALOGO_BLOQUES:
            bloques_invalidos.append(bloque)
    
    if bloques_invalidos:
        errores.append(f'Bloques no válidos: {", ".join(bloques_invalidos)}')
    
    return {
        'valida': len(errores) == 0,
        'errores': errores
    }

def generar_preview_url(nombre_nora: str) -> str:
    """
    Genera URL de preview para la landing page
    """
    import os
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    return f"{base_url}/panel_cliente/{nombre_nora}/lading_pages/preview"

def generar_url_publica(nombre_nora: str) -> str:
    """
    Genera URL pública para la landing page
    """
    import os
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    return f"{base_url}/panel_cliente/{nombre_nora}/lading_pages/publica"

def obtener_estadisticas_landing(nombre_nora: str) -> Dict[str, Any]:
    """
    Obtiene estadísticas básicas de la landing page
    """
    try:
        from clientes.aura.utils.supabase_client import supabase
        from clientes.aura.utils.quick_schemas import existe
        
        if not existe('landing_pages_config'):
            return {
                'existe': False,
                'publicada': False,
                'total_bloques': 0,
                'ultima_actualizacion': None
            }
        
        # Obtener configuración
        config_result = supabase.table('landing_pages_config') \
            .select('id, publicada, actualizada_en') \
            .eq('nombre_nora', nombre_nora) \
            .eq('activa', True) \
            .single() \
            .execute()
        
        if not config_result.data:
            return {
                'existe': False,
                'publicada': False,
                'total_bloques': 0,
                'ultima_actualizacion': None
            }
        
        config_id = config_result.data['id']
        
        # Contar bloques personalizados
        bloques_result = supabase.table('landing_pages_bloques') \
            .select('id', count='exact') \
            .eq('config_id', config_id) \
            .eq('visible', True) \
            .execute()
        
        return {
            'existe': True,
            'publicada': config_result.data.get('publicada', False),
            'total_bloques': bloques_result.count or 0,
            'ultima_actualizacion': config_result.data.get('actualizada_en')
        }
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return {
            'existe': False,
            'publicada': False,
            'total_bloques': 0,
            'ultima_actualizacion': None,
            'error': str(e)
        }
