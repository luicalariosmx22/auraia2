# ✅ Archivo: gunicorn_patch.py
# 👉 Aplica monkey.patch_all() ANTES de cualquier import que use SSL

from gevent import monkey
monkey.patch_all()  # ⚠️ Esto debe ir antes que cualquier otra importación

from clientes.aura import create_app  # Importa tu app Flask correctamente
app = create_app()  # Gunicorn espera una variable global `app`
