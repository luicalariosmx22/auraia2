# Archivo: clientes/aura/routes/reportes_meta_ads.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.meta_ads import listar_campañas_activas
from clientes.aura.handlers.handle_ai import manejar_respuesta_ai

# El blueprint y las rutas ahora se encuentran divididas en:
# - vistas.py (vistas generales de reportes)
# - carga_manual.py (carga manual de reportes)
# - automatizaciones.py (automatizaciones/configuración)
# - diseno.py (diseño y variables)
#
# Este archivo queda vacío o solo con comentarios de referencia.
# El blueprint se define y usa únicamente en __init__.py del paquete reportes_meta_ads.
