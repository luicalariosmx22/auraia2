from flask import current_app
from clientes.aura.handlers.insertar_rutas import insertar_ruta
from datetime import datetime

# 👇 Importamos la función safe_register_blueprint
from app import safe_register_blueprint

def registrar_rutas_en_supabase():
    """
    Registra las rutas activas de la aplicación en Supabase.
    """
    rutas = []
    for rule in current_app.url_map.iter_rules():
        rutas.append({
            "ruta": rule.rule,
            "blueprint": rule.endpoint.split(".")[0] if "." in rule.endpoint else "default",
            "metodo": ", ".join(rule.methods - {"HEAD", "OPTIONS"})
        })
    try:
        response = insertar_ruta(rutas)
        print(f"✅ Rutas registradas en Supabase: {response}")
    except Exception as e:
        print(f"❌ Error al registrar rutas en Supabase: {str(e)}")

def registrar_rutas_base(app):
    """
    Registra los blueprints base usando safe_register_blueprint.
    """
    try:
        from clientes.aura.routes.panel_chat import panel_chat_bp
        from clientes.aura.routes.webhook import webhook_bp
        # ... otros imports base

        safe_register_blueprint(app, panel_chat_bp)
        safe_register_blueprint(app, webhook_bp)
        # ... registrar los demás igual

        print("✅ Rutas base registradas correctamente.")
    except Exception as e:
        print(f"❌ Error al registrar rutas base: {e}")