from flask import current_app
from clientes.aura.handlers.insertar_rutas import insertar_ruta
from datetime import datetime

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