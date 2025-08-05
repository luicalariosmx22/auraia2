# ✅ Archivo: gunicorn_patch.py
# 👉 Aplica monkey.patch_all() ANTES de cualquier import que use SSL

from gevent import monkey
monkey.patch_all()  # ⚠️ Esto debe ir antes que cualquier otra importación

"""
Parche para permitir que Gunicorn use la aplicación Flask aunque parte de la inicialización sea asíncrona.
"""
import os
import sys
from clientes.aura import create_app  # Importa la función factory

# Inicializar la aplicación
print("🚀 Inicializando aplicación AuraAI para Gunicorn")

# Desempaquetar la tupla
app, socketio = create_app()

print("✅ Aplicación AuraAI lista para ser servida por Gunicorn")
