print("✅ registro_cliente.py cargado correctamente")

# ✅ Esta función espera que le pases una instancia `app` ya creada desde app.py

def registrar_blueprints_cliente(app):
    try:
        from clientes.aura.routes.contactos import contactos_bp

        # Evitar registrar varias veces el mismo blueprint
        if "contactos" not in app.blueprints:
            app.register_blueprint(contactos_bp, url_prefix="/panel/cliente")
            print("✅ Blueprint 'contactos_bp' registrado correctamente con prefijo '/panel/cliente'.")
        else:
            print("⚠️ Blueprint 'contactos_bp' ya estaba registrado.")
    except Exception as e:
        print(f"❌ Error en registrar_blueprints_cliente: {e}")

# ❌ Este bloque no se necesita aquí:
# if __name__ == '__main__':
#     registrar_blueprints_cliente(app)
#     app.run(debug=True)
