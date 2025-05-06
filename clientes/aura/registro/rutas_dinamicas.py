"""
✅ Registro de rutas dinámicas por Nora
Esto asegura que los módulos con rutas dinámicas (como Ads) estén disponibles por cada Nora.
"""

def registrar_blueprints_por_nora(app, nombre_nora):
    from clientes.aura.modules.ads import ads_bp  # ✅ Import del módulo Ads dinámico

    # ✅ Registrar la ruta dinámica del módulo Ads
    if 'ads_bp' in app.blueprints:  # Ensure the correct blueprint name is checked
        app.add_url_rule(
            f"/panel_cliente/{nombre_nora}/ads",
            view_func=ads_bp.view_functions['panel_cliente_ads'],
            endpoint=f"{nombre_nora}_ads"
        )
