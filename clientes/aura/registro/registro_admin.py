print("✅ registro_admin.py cargado correctamente")

from clientes.aura.utils.blueprint_utils import safe_register_blueprint
from clientes.aura.routes.admin_dashboard import admin_dashboard_bp
from clientes.aura.routes.admin_noras import admin_noras_bp
from clientes.aura.routes.admin_nora import admin_nora_bp
from clientes.aura.routes.admin_nora_dashboard import admin_nora_dashboard_bp
from clientes.aura.routes.admin_debug_master import admin_debug_master_bp
# from clientes.aura.routes.admin_envios_programados import envios_programados_bp  # ❌ Comentado

def registrar_blueprints_admin(app):
    """
    ✅ Registra TODOS los blueprints de administración de forma segura.
    """
    try:
        print("🔍 Registrando blueprints de administración...")

        safe_register_blueprint(app, admin_noras_bp, url_prefix="/admin/noras")
        safe_register_blueprint(app, admin_dashboard_bp, url_prefix="/admin/dashboard")
        safe_register_blueprint(app, admin_nora_bp, url_prefix="/admin/nora")
        safe_register_blueprint(app, admin_nora_dashboard_bp, url_prefix="/admin/nora/dashboard")
        safe_register_blueprint(app, admin_debug_master_bp, url_prefix="/admin/debug")
        # safe_register_blueprint(app, envios_programados_bp, url_prefix="/admin/envios")  # ❌ Comentado

        print("✅ Todos los blueprints de administración registrados correctamente.")

    except Exception as e:
        print(f"❌ Error en registrar_blueprints_admin: {str(e)}")
