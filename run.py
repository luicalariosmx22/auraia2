# run.py
import os
from clientes.aura import create_app
from gunicorn.app.wsgiapp import run
import sys
import time
from flask import send_file

app = create_app()

# Ruta de prueba para servir el archivo de test
@app.route('/test_importacion_google_ads.html')
def test_importacion():
    return send_file('test_importacion_google_ads.html')

# Ruta de prueba para el test simple
@app.route('/test_simple_insert.html')
def test_simple_insert():
    return send_file('test_simple_insert.html')

if __name__ == '__main__':
    # Para desarrollo local con el servidor de Flask
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
else:
    try:
        run()
    except Exception as e:
        sys.exit(str(e))
        time.sleep(0.1)