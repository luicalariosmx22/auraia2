# ✅ Archivo: gunicorn_config.py
# 👉 Parcheo obligatorio de gevent SSL antes de todo

from gevent import monkey
monkey.patch_all()  # ✅ Este debe ejecutarse antes de cualquier otro import

import clientes.aura  # o el módulo raíz que inicializa tu app Flask
