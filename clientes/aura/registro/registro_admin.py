print("✅ registro_admin.py cargado correctamente")

from clientes.aura.routes.admin_dashboard import admin_dashboard_bp
from clientes.aura.routes.admin_noras import admin_noras_bp
from clientes.aura.routes.admin_nora import admin_nora_bp
from clientes.aura.routes.admin_nora_dashboard import admin_nora_dashboard_bp
from clientes.aura.routes.admin_debug_master import admin_debug_master_bp
from clientes.aura.routes.admin_actualizar_contactos import admin_actualizar_contactos_bp
from clientes.aura.routes.admin_modulos.admin_modulos import admin_modulos_bp
from clientes.aura.routes.admin_modulos.creador_modulos import admin_creador_modulos_bp
from clientes.aura.routes.admin_modulos.verificador import verificador_modulos_bp
from clientes.aura.routes.admin_modulos.gestor_modulos import gestor_modulos_bp
from clientes.aura.routes.admin_modulos.registro_dinamico_frontend import registro_dinamico_frontend_bp
# from clientes.aura.routes.admin_envios_programados import envios_programados_bp  # ❌ Comentado

def registrar_blueprints_admin(app, safe_register_blueprint):
    """
    ✅ Registra TODOS los blueprints de administración de forma segura.
    """
    try:
        safe_register_blueprint(app, admin_noras_bp, url_prefix="")
        safe_register_blueprint(app, admin_dashboard_bp, url_prefix="/admin")
        safe_register_blueprint(app, admin_nora_bp, url_prefix="/admin/nora")
        safe_register_blueprint(app, admin_nora_dashboard_bp, url_prefix="/admin/nora/dashboard")
        safe_register_blueprint(app, admin_debug_master_bp, url_prefix="/admin/debug")
        # Panel de módulos: restaurar lógica original, el verificador de módulos es el panel principal
        safe_register_blueprint(app, verificador_modulos_bp, url_prefix="/admin/modulos")
        safe_register_blueprint(app, admin_creador_modulos_bp, url_prefix="/admin/creador_modulos")
        safe_register_blueprint(app, admin_actualizar_contactos_bp, url_prefix="/admin/actualizar_contactos")
        # safe_register_blueprint(app, envios_programados_bp, url_prefix="/admin/envios")  # ❌ Comentado
        # Registrar el gestor de módulos
        safe_register_blueprint(app, gestor_modulos_bp)
        # Registrar el frontend de registro dinámico
        safe_register_blueprint(app, registro_dinamico_frontend_bp)
    except Exception as e:
        print(f"❌ Error en registrar_blueprints_admin: {e}")
