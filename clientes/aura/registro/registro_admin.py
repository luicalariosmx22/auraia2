print("✅ registro_admin.py cargado correctamente")

from clientes.aura.routes.admin_dashboard import admin_dashboard_bp
from clientes.aura.routes.admin_noras import admin_noras_bp
from clientes.aura.routes.admin_nora import admin_nora_bp
from clientes.aura.routes.admin_nora_dashboard import admin_nora_dashboard_bp
from clientes.aura.routes.admin_debug_master import admin_debug_master_bp
from clientes.aura.routes.admin_actualizar_contactos import admin_actualizar_contactos_bp
# from clientes.aura.routes.admin_envios_programados import envios_programados_bp  # ❌ Comentado

def registrar_blueprints_admin(app, safe_register_blueprint):
    """
    ✅ Registra TODOS los blueprints de administración de forma segura.
    """
    try:
        safe_register_blueprint(app, admin_noras_bp, url_prefix="")
        safe_register_blueprint(app, admin_dashboard_bp, url_prefix="/admin/dashboard")
        safe_register_blueprint(app, admin_nora_bp, url_prefix="/admin/nora")
        safe_register_blueprint(app, admin_nora_dashboard_bp, url_prefix="/admin/nora/dashboard")
        safe_register_blueprint(app, admin_debug_master_bp, url_prefix="/admin/debug")
        safe_register_blueprint(app, admin_actualizar_contactos_bp, url_prefix="/admin/actualizar_contactos")
        # safe_register_blueprint(app, envios_programados_bp, url_prefix="/admin/envios")  # ❌ Comentado
    except Exception as e:
        print(f"❌ Error en registrar_blueprints_admin: {e}")
