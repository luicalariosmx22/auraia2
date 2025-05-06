print("✅ registro_admin.py cargado correctamente")

from clientes.aura.utils.blueprint_utils import safe_register_blueprint  # ✅ Import from blueprint_utils
from clientes.aura.routes.admin_dashboard import admin_dashboard_bp
from clientes.aura.routes.admin_noras import admin_noras_bp
from clientes.aura.routes.admin_nora import admin_nora_bp
from clientes.aura.routes.admin_envios_programados import envios_programados_bp

def registrar_blueprints_admin(app):
    """
    ✅ Registra TODOS los blueprints de administración de forma segura.
    """
    try:
        print("🔍 Registrando blueprints de administración...")

        safe_register_blueprint(app, admin_noras_bp, url_prefix="/admin/noras")
        safe_register_blueprint(app, admin_dashboard_bp, url_prefix="/admin/dashboard")
        safe_register_blueprint(app, admin_nora_bp, url_prefix="/admin/nora/<nombre_nora>/editar")
        safe_register_blueprint(app, envios_programados_bp, url_prefix="/panel/envios-programados")

        print("✅ Todos los blueprints de administración registrados correctamente.")

    except Exception as e:
        print(f"❌ Error en registrar_blueprints_admin: {str(e)}")
