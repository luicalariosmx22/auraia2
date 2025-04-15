```python
print("✅ registro_cliente.py cargado correctamente")

def registrar_blueprints_cliente(app):
    try:
        # Solo el panel base del cliente (los demás se registran dinámicamente según módulos)
        from clientes.aura.routes.panel_cliente import panel_cliente_bp
        app.register_blueprint(panel_cliente_bp)

        print("✅ Blueprints cliente registrados")

    except Exception as e:
        print("❌ Error en registrar_blueprints_cliente:", str(e))
```