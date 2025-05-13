# run.py
import os
from clientes.aura import create_app  # Importa tu factory

# Llama a create_app para obtener la instancia de la aplicación
app = create_app()

if __name__ == '__main__':
    # Corre con el servidor de desarrollo de Flask
    # debug=True es útil para desarrollo, pero NO lo uses en producción.
    # Railway usará Gunicorn, así que este bloque if __name__ == '__main__'
    # no será ejecutado por Gunicorn en Railway.
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)