# run.py
import os
from clientes.aura import create_app
from gunicorn.app.wsgiapp import run
import sys
import time

app = create_app()

if __name__ == '__main__':
    # Para desarrollo local con el servidor de Flask
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
else:
    try:
        run()
    except Exception as e:
        sys.exit(str(e))
        time.sleep(0.1)