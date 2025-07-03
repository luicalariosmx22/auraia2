# Archivo: clientes/aura/routes/reportes_meta_ads/lazy_estadisticas.py
"""
Carga lazy del módulo de estadísticas para evitar cuelgues de inicialización
"""

from flask import Blueprint

# Blueprint lazy para estadísticas
lazy_estadisticas_bp = Blueprint('lazy_estadisticas', __name__)

@lazy_estadisticas_bp.route('/estadisticas')
def redirect_to_estadisticas():
    """Redirige a las estadísticas cargando el módulo bajo demanda"""
    try:
        from . import get_estadisticas_bp
        estadisticas_bp = get_estadisticas_bp()
        if estadisticas_bp:
            # Redirigir a la ruta real de estadísticas
            from flask import redirect, url_for
            return redirect(url_for('estadisticas_ads_bp.vista_estadisticas_ads'))
        else:
            return "Error: No se pudo cargar el módulo de estadísticas", 500
    except Exception as e:
        return f"Error cargando estadísticas: {e}", 500

@lazy_estadisticas_bp.route('/estadisticas/status')
def estadisticas_status():
    """Endpoint para verificar si las estadísticas están disponibles"""
    try:
        from . import get_estadisticas_bp
        estadisticas_bp = get_estadisticas_bp()
        return {
            "disponible": estadisticas_bp is not None,
            "mensaje": "Estadísticas cargadas" if estadisticas_bp else "Estadísticas no disponibles"
        }
    except Exception as e:
        return {"disponible": False, "error": str(e)}
