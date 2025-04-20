print("✅ registro_cliente.py cargado correctamente")

# ❌ NO DEBES crear otra app
# NO hagas: app = Flask(__name__)

def registrar_blueprints_cliente(app):
    try:
        from clientes.aura.routes.contactos import contactos_bp
        if "contactos" not in app.blueprints:
            app.register_blueprint(contactos_bp, url_prefix="/panel/cliente")
            print("✅ Blueprint 'contactos_bp' registrado correctamente con prefijo '/panel/cliente'.")
        else:
            print("⚠️ Blueprint 'contactos_bp' ya estaba registrado.")
    except Exception as e:
        print("❌ Error en registrar_blueprints_cliente:", str(e))

# ❌ Este bloque tampoco se necesita, porque `app` no existe aquí de forma global
# if __name__ == '__main__':
#     registrar_blueprints_cliente(app)
#     app.run(debug=True)
