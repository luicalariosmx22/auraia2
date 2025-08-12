"""
📊 SCHEMAS DE BD QUE USA ESTE ARCHIVO:

📋 TABLAS PRINCIPALES:
• configuracion_bot: Config de cada Nora (OBLIGATORIO EN TODOS LOS MÓDULOS)
  └ Campos: nombre_nora(text), modulos(json), ia_activa(boolean)

• landing_pages_config: Configuración de landing pages por Nora (si existe)
  └ Campos: nombre_nora(text), config_json(json), activa(boolean), creada_en(timestamptz)

• landing_pages_bloques: Bloques disponibles para landing pages (si existe)
  └ Campos: id(bigint), nombre(text), tipo(text), html_template(text), activo(boolean)

🔗 RELACIONES:
• configuracion_bot -> landing_pages_config via nombre_nora (filtro obligatorio)

💡 VERIFICACIÓN OBLIGATORIA:
from clientes.aura.utils.quick_schemas import existe, columnas
if existe('landing_pages_config'):
    campos = columnas('landing_pages_config')
"""

from flask import Blueprint, render_template, request, jsonify
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.supabase_schemas import SUPABASE_SCHEMAS
from clientes.aura.utils.quick_schemas import existe, columnas

# 🗄️ CONTEXTO BD PARA GITHUB COPILOT
# BD ACTUAL: Esquemas actualizados automáticamente

panel_cliente_lading_pages_bp = Blueprint(
    "panel_cliente_lading_pages_bp", 
    __name__, 
    url_prefix="/panel_cliente/<nombre_nora>/lading_pages"
)

@panel_cliente_lading_pages_bp.route("/")
def panel_cliente_lading_pages():
    """Vista principal del módulo Landing Pages"""
    # 🎯 PATRÓN OFICIAL: extracción de nombre_nora
    nombre_nora = request.path.split("/")[2]
    
    # ✅ VALIDACIÓN BD: Verificar que la Nora existe
    try:
        config = supabase.table('configuracion_bot') \
            .select('modulos') \
            .eq('nombre_nora', nombre_nora) \
            .single() \
            .execute()
        
        if not config.data:
            return "Nora no encontrada", 404
        
        # Verificar que el módulo landing_pages está activo
        modulos = config.data.get('modulos', {})
        if not modulos.get('lading_pages', False):
            return "Módulo Landing Pages no está activo", 403
        
    except Exception as e:
        print(f"Error verificando configuración: {e}")
        return "Error interno", 500
    
    # 🔹 Recuperar configuración de landing pages (si la tabla existe)
    landing_config = obtener_config_landing(nombre_nora)
    
    return render_template(
        "panel_cliente_lading_pages/index.html", 
        nombre_nora=nombre_nora,
        config=landing_config
    )

@panel_cliente_lading_pages_bp.route("/editor")
def vista_editor_landing():
    """Editor para diseñar y configurar landing pages"""
    nombre_nora = request.path.split("/")[2]
    
    # Obtener configuración actual y bloques disponibles
    config = obtener_config_landing(nombre_nora)
    bloques = obtener_bloques_disponibles()
    
    return render_template(
        "panel_cliente_lading_pages/editor.html",
        nombre_nora=nombre_nora,
        config=config,
        bloques=bloques,
    )

@panel_cliente_lading_pages_bp.route("/vista_publica")
def vista_landing_publica():
    """Vista pública de la landing page (sin header/footer de panel)"""
    nombre_nora = request.path.split("/")[2]
    
    # 🔹 Recupera la config activa de esta landing
    config = obtener_config_landing(nombre_nora)
    
    return render_template(
        "panel_cliente_lading_pages/vista_publica.html",
        nombre_nora=nombre_nora,
        config=config,
    )

@panel_cliente_lading_pages_bp.route("/api/landing/guardar", methods=["POST"])
def api_guardar_landing():
    """API para guardar configuración de landing page"""
    try:
        payload = request.get_json(silent=True) or {}
        nombre_nora = request.path.split("/")[2]
        
        # Validar payload básico
        if not payload:
            return jsonify({
                "success": False, 
                "message": "Datos requeridos"
            }), 400
        
        # Guardar configuración
        ok, msg = guardar_config_landing(nombre_nora=nombre_nora, payload=payload)
        status = 200 if ok else 400
        
        return jsonify({
            "success": ok, 
            "message": msg
        }), status
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error interno: {str(e)}"
        }), 500

@panel_cliente_lading_pages_bp.route("/api/landing/config", methods=["GET"])
def api_obtener_config():
    """API para obtener configuración actual de landing page"""
    try:
        nombre_nora = request.path.split("/")[2]
        config = obtener_config_landing(nombre_nora)
        
        return jsonify({
            "success": True,
            "config": config
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error obteniendo configuración: {str(e)}"
        }), 500

@panel_cliente_lading_pages_bp.route("/api/bloques", methods=["GET"])
def api_obtener_bloques():
    """API para obtener bloques disponibles"""
    try:
        bloques = obtener_bloques_disponibles()
        
        return jsonify({
            "success": True,
            "bloques": bloques
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error obteniendo bloques: {str(e)}"
        }), 500

@panel_cliente_lading_pages_bp.route("/preview")
def preview_landing():
    """Vista previa de la landing page"""
    nombre_nora = request.path.split("/")[2]
    
    # Obtener configuración para preview
    config = obtener_config_landing(nombre_nora)
    
    return render_template(
        "panel_cliente_lading_pages/preview.html",
        nombre_nora=nombre_nora,
        config=config,
        preview_mode=True
    )

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def obtener_config_landing(nombre_nora):
    """Obtiene configuración de landing page para una Nora"""
    try:
        # ✅ VERIFICAR TABLA ANTES DE USAR (nueva buena práctica)
        if not existe('landing_pages_config'):
            print("⚠️ Tabla landing_pages_config no existe, usando configuración por defecto")
            return {
                "titulo": f"Landing Page - {nombre_nora.title()}",
                "bloques": ["hero", "servicios", "contacto"],
                "colores": {
                    "primario": "#3B82F6",
                    "secundario": "#1E40AF",
                    "texto": "#1F2937"
                }
            }
        
        # Obtener desde BD
        result = supabase.table('landing_pages_config') \
            .select('config_json') \
            .eq('nombre_nora', nombre_nora) \
            .eq('activa', True) \
            .single() \
            .execute()
        
        if result.data and result.data.get('config_json'):
            return result.data['config_json']
        else:
            # Configuración por defecto si no hay registro
            return {
                "titulo": f"Landing Page - {nombre_nora.title()}",
                "bloques": ["hero", "servicios", "contacto"],
                "colores": {
                    "primario": "#3B82F6",
                    "secundario": "#1E40AF", 
                    "texto": "#1F2937"
                }
            }
        
    except Exception as e:
        print(f"Error obteniendo configuración de landing: {e}")
        return {
            "titulo": f"Landing Page - {nombre_nora.title()}",
            "bloques": ["hero"],
            "error": str(e)
        }

def obtener_bloques_disponibles():
    """Obtiene bloques disponibles para landing pages"""
    try:
        # ✅ VERIFICAR TABLA ANTES DE USAR
        if not existe('landing_pages_bloques'):
            print("⚠️ Tabla landing_pages_bloques no existe, usando bloques por defecto")
            return [
                {
                    "id": "hero",
                    "nombre": "Hero Section",
                    "tipo": "header",
                    "descripcion": "Sección principal con título y llamada a la acción",
                    "activo": True
                },
                {
                    "id": "servicios",
                    "nombre": "Servicios", 
                    "tipo": "content",
                    "descripcion": "Grid de servicios o productos",
                    "activo": True
                },
                {
                    "id": "contacto",
                    "nombre": "Contacto",
                    "tipo": "footer",
                    "descripcion": "Formulario de contacto y información",
                    "activo": True
                },
                {
                    "id": "testimonios",
                    "nombre": "Testimonios",
                    "tipo": "content", 
                    "descripcion": "Testimonios de clientes",
                    "activo": True
                }
            ]
        
        # Obtener desde BD
        result = supabase.table('landing_pages_bloques') \
            .select('id, nombre, tipo, descripcion, activo') \
            .eq('activo', True) \
            .order('nombre') \
            .execute()
        
        return result.data if result.data else []
        
    except Exception as e:
        print(f"Error obteniendo bloques: {e}")
        return []

def guardar_config_landing(nombre_nora, payload):
    """Guarda configuración de landing page"""
    try:
        # ✅ VERIFICAR TABLA ANTES DE USAR
        if not existe('landing_pages_config'):
            print("⚠️ Tabla landing_pages_config no existe, no se puede guardar")
            return False, "Tabla de configuración no existe"
        
        # Verificar si ya existe configuración
        existing = supabase.table('landing_pages_config') \
            .select('id') \
            .eq('nombre_nora', nombre_nora) \
            .execute()
        
        if existing.data:
            # Actualizar existente
            result = supabase.table('landing_pages_config') \
                .update({
                    'config_json': payload,
                    'actualizada_en': 'now()'
                }) \
                .eq('nombre_nora', nombre_nora) \
                .execute()
        else:
            # Crear nueva
            result = supabase.table('landing_pages_config') \
                .insert({
                    'nombre_nora': nombre_nora,
                    'config_json': payload,
                    'activa': True
                }) \
                .execute()
        
        if result.data:
            return True, "Configuración guardada exitosamente"
        else:
            return False, "Error guardando configuración"
        
    except Exception as e:
        print(f"Error guardando configuración: {e}")
        return False, f"Error interno: {str(e)}"
