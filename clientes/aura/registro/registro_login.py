"""
Registro de rutas relacionadas con login y autenticación.
"""
import logging
from flask import Blueprint

logger = logging.getLogger(__name__)

def registrar_blueprints_login(app, safe_register_blueprint):
    """
    Registra los blueprints relacionados con el login en la aplicación Flask.
    """
    try:
        # Importar el blueprint del login
        from clientes.aura.auth.simple_login import simple_login_bp

        # Verificar si ya está registrado
        if 'simple_login_unique' in app.blueprints:
            logger.info("[OK] Blueprint de login ya registrado, omitiendo registro.")
            return

        # Verificar si endpoints relevantes ya existen
        for rule in app.url_map.iter_rules():
            if 'google_login' in rule.endpoint or 'simple_login_unique.google_login' in rule.endpoint:
                logger.info(f"✅ Endpoint Google ya registrado ({rule.endpoint}), omitiendo.")
                return
            elif 'auth_simple' in rule.endpoint or 'simple_login_unique.auth_simple' in rule.endpoint:
                logger.info(f"[OK] Endpoint de login ya registrado ({rule.endpoint}), omitiendo.")
                return

        # Registrar blueprint si no está aún
        safe_register_blueprint(app, simple_login_bp)
        logger.info("✅ Blueprint 'simple_login_unique' registrado con éxito.")

    except Exception as e:
        logger.error(f"❌ Error al registrar blueprints de login: {str(e)}", exc_info=True)
