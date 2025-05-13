# run.py
import os
from clientes.aura import create_app # Importa tu factory
# Importa tu GunicornApplication si la mueves a un archivo utils o la defines aquí
# from alguna_parte import GunicornApplication 

app = create_app()

# Define GunicornApplication aquí o impórtala
# (Si la mantienes, asegúrate de que 'BaseApplication' y 'Config' se importen donde se define)
# from gunicorn.app.base import BaseApplication
# from gunicorn.config import Config
# class GunicornApplication(BaseApplication): ... (tu clase) ...

if __name__ == '__main__':
    # Aquí puedes poner tu lógica de GunicornApplication
    # app.logger.info("Iniciando Gunicorn desde run.py...")
    # options = { ... }
    # gunicorn_app = GunicornApplication(app, options)
    # gunicorn_app.run()

    # O para desarrollo local simple sin tu GunicornApplication:
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True) # El debug=True no es para producción