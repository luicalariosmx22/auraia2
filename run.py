# run.py
import os
from clientes.aura import create_app

app = create_app()

if __name__ == '__main__':
    # Para desarrollo local con el servidor de Flask
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)