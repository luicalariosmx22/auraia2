from flask import current_app
from clientes.aura.handlers.insertar_rutas import insertar_ruta
from datetime import datetime

def registrar_rutas_en_supabase():
    """
    Recorre todas las rutas de Flask y las registra en la tabla 'rutas_registradas' en Supabase.
    """
    for rule in current_app.url_map.iter_rules():
        ruta = rule.rule
        metodo = ", ".join(rule.methods)
        blueprint = rule.endpoint.split(".")[0] if "." in rule.endpoint else "default"
        
        # Insertar cada ruta en Supabase
        respuesta = insertar_ruta(
            ruta=ruta,
            blueprint=blueprint,
            metodo=metodo,
            registrado_en=datetime.now().isoformat()
        )
        if "error" in respuesta:
            print(f"❌ Error al registrar la ruta {ruta}: {respuesta['error']}")
        else:
            print(f"✅ Ruta registrada: {ruta}")