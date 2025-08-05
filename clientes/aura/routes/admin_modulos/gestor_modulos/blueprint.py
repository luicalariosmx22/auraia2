from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app, session
from clientes.aura.utils.supabase_client import supabase
import logging

logger = logging.getLogger(__name__)

# Crear blueprint
gestor_modulos_bp = Blueprint('gestor_modulos', __name__, url_prefix='/admin/modulos')

@gestor_modulos_bp.route('/')
def index():
    """Vista principal del gestor de módulos."""
    try:
        # Obtener todas las instancias de Nora
        response = supabase.table("configuracion_bot").select("nombre_nora, numero_nora").execute()
        # Obtener módulos disponibles desde la base de datos
        modulos_query = supabase.table("modulos_disponibles").select("id, nombre, descripcion").execute()

        noras = []
        modulos_disponibles = []

        if hasattr(response, 'error') and response.error:
            logger.error(f"Error al consultar instancias de Nora: {response.error}")
            flash("Error al cargar instancias de Nora", "danger")
        else:
            noras = response.data if hasattr(response, 'data') else []

        if hasattr(modulos_query, 'error') and modulos_query.error:
            logger.error(f"Error al consultar módulos disponibles: {modulos_query.error}")
            flash("Error al cargar módulos disponibles", "danger")
        else:
            modulos_disponibles = modulos_query.data if hasattr(modulos_query, 'data') else []

        return render_template('admin_modulos/index.html', noras=noras, modulos_disponibles=modulos_disponibles)
    
    except Exception as e:
        logger.error(f"Error al cargar página del gestor de módulos: {str(e)}")
        flash(f"Ha ocurrido un error: {str(e)}", "danger")
        return render_template('admin_modulos/index.html', noras=[], modulos_disponibles=[])

@gestor_modulos_bp.route('/nora/<nombre_nora>')
def configurar_nora(nombre_nora):
    """Vista de configuración para una Nora específica."""
    try:
        # Obtener configuración de la Nora
        resultado = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).execute()

        if not resultado.data or len(resultado.data) == 0:
            print(f"❌ No se encontró configuración para la Nora: {nombre_nora}")
            return None  # o manejarlo como error

        configuracion = resultado.data[0]
        
        # Obtener lista de módulos disponibles desde la base de datos
        modulos_query = supabase.table("modulos_disponibles").select("id, nombre, descripcion").execute()
        if hasattr(modulos_query, 'error') and modulos_query.error:
            logger.error(f"Error al consultar módulos disponibles: {modulos_query.error}")
            flash("Error al cargar módulos disponibles", "danger")
            modulos_disponibles = []
        else:
            modulos_disponibles = modulos_query.data if hasattr(modulos_query, 'data') else []
        
        # Determinar qué módulos están activos
        modulos_activos = configuracion.get("modulos", {})
        
        # Si módulos es una lista (formato antiguo), convertir a diccionario
        if isinstance(modulos_activos, list):
            modulos_activos = {modulo: True for modulo in modulos_activos}
            
        return render_template(
            'admin_modulos/gestor/configurar.html',
            nora=configuracion,
            modulos_disponibles=modulos_disponibles,
            modulos_activos=modulos_activos
        )
    
    except Exception as e:
        logger.error(f"Error al cargar configuración de {nombre_nora}: {str(e)}")
        flash(f"Ha ocurrido un error: {str(e)}", "danger")
        return redirect(url_for('gestor_modulos.index'))

@gestor_modulos_bp.route('/nora/<nombre_nora>/actualizar', methods=['POST'])
def actualizar_modulos(nombre_nora):
    """Actualiza los módulos activos para una Nora específica."""
    try:
        # Obtener los módulos seleccionados del formulario
        modulos_seleccionados = request.form.getlist('modulos')
        modulos_activos = {modulo: True for modulo in modulos_seleccionados}
        
        # Actualizar en la base de datos
        response = supabase.table("configuracion_bot").update(
            {"modulos": modulos_activos}
        ).eq("nombre_nora", nombre_nora).execute()
        
        if hasattr(response, 'error') and response.error:
            logger.error(f"Error al actualizar módulos de {nombre_nora}: {response.error}")
            flash(f"Error al guardar cambios: {response.error}", "danger")
        else:
            flash(f"Módulos de {nombre_nora} actualizados correctamente", "success")
            
        return redirect(url_for('gestor_modulos.configurar_nora', nombre_nora=nombre_nora))
    
    except Exception as e:
        logger.error(f"Error al actualizar módulos de {nombre_nora}: {str(e)}")
        flash(f"Ha ocurrido un error: {str(e)}", "danger")
        return redirect(url_for('gestor_modulos.configurar_nora', nombre_nora=nombre_nora))

@gestor_modulos_bp.route('/registro_dinamico')
def redirigir_registro_dinamico():
    """
    Redirige al usuario hacia el frontend de registro dinámico.
    Esta ruta sirve como acceso directo.
    """
    return redirect(url_for('registro_dinamico_frontend.index'))