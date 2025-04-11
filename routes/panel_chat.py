from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from .services import agregar_contacto_service, editar_contacto_service, eliminar_contacto_service, toggle_ia_service
from .utils import cargar_json, guardar_json, normalizar_numero

panel_chat_bp = Blueprint('panel_chat', __name__)

@panel_chat_bp.route('/panel/chat', methods=['GET', 'POST'])
def panel_chat():
    # Lógica de la ruta principal
    pass

@panel_chat_bp.route('/agregar-contacto', methods=['GET', 'POST'])
def agregar_contacto():
    # Llamada a la lógica del servicio para agregar un contacto
    return agregar_contacto_service(request)

@panel_chat_bp.route('/editar-contacto/<numero>', methods=['GET', 'POST'])
def editar_contacto(numero):
    # Llamada al servicio para editar el contacto
    return editar_contacto_service(numero, request)

@panel_chat_bp.route('/eliminar-contacto/<numero>', methods=['POST'])
def eliminar_contacto(numero):
    # Llamada al servicio para eliminar un contacto
    return eliminar_contacto_service(numero)

@panel_chat_bp.route('/toggle_ia/<numero>', methods=['POST'])
def toggle_ia(numero):
    # Llamada al servicio para activar/desactivar IA
    return toggle_ia_service(numero)

# Aquí puedes agregar más rutas según sea necesario
