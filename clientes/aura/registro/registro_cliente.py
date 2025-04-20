print("✅ registro_cliente.py cargado correctamente")

from flask import Flask
from clientes.aura.routes.contactos import contactos_bp

app = Flask(__name__)

# Registrar el Blueprint de contactos
if "contactos_bp" not in app.blueprints:
    app.register_blueprint(contactos_bp)
    print("✅ Blueprint 'contactos_bp' registrado correctamente.")
else:
    print("⚠️ Blueprint 'contactos_bp' ya estaba registrado.")

def registrar_blueprints_cliente(app):
    try:
        # Importar y registrar el Blueprint de contactos
        from clientes.aura.routes.contactos import contactos_bp
        if "contactos_bp" not in app.blueprints:
            app.register_blueprint(contactos_bp, url_prefix="/panel/cliente")
            print("✅ Blueprint 'contactos_bp' registrado correctamente con prefijo '/panel/cliente'.")
        else:
            print("⚠️ Blueprint 'contactos_bp' ya estaba registrado.")
    except Exception as e:
        print("❌ Error en registrar_blueprints_cliente:", str(e))

if __name__ == '__main__':
    app.run(debug=True)
