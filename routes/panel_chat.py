from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import json
from collections import defaultdict
import os
from utils.normalizador import normalizar_numero
from flask_wtf.csrf import CSRFProtect

panel_chat_bp = Blueprint('panel_chat', __name__)
ARCHIVO_HISTORIAL = "historial_conversaciones.json"
CONTACTOS_INFO = "contactos_info.json"
ETIQUETAS_DISPONIBLES = "etiquetas.json"

# Configuración CSRF
csrf = CSRFProtect()

@panel_chat_bp.route('/panel/chat')
def panel_chat():
    numero_seleccionado = request.args.get('numero')
    etiqueta_seleccionada = request.args.get('etiqueta')

    contactos_info = cargar_json(CONTACTOS_INFO, {})
    historial = cargar_json(ARCHIVO_HISTORIAL, [])

    if etiqueta_seleccionada:
        contactos_info = {
            k: v for k, v in contactos_info.items() 
            if 'etiquetas' in v and etiqueta_seleccionada in v['etiquetas']
        }

    contactos, nombres_contactos, ia_estado_contactos = procesar_contactos(historial, contactos_info)

    return render_template(
        "panel_chat.html",
        contactos=sorted(contactos.keys()),
        mensajes=ordenar_mensajes(contactos.get(normalizar_numero(numero_seleccionado), [])),
        seleccionado=normalizar_numero(numero_seleccionado),
        nombres=nombres_contactos,
        ia_estado_contactos=ia_estado_contactos,
        etiquetas={k: v.get("etiquetas", []) for k, v in contactos_info.items()},
        etiquetas_disponibles=cargar_json(ETIQUETAS_DISPONIBLES, []),
        etiqueta_filtrada=etiqueta_seleccionada
    )

@panel_chat_bp.route('/filter_etiquetas', methods=['GET'])
def filter_etiquetas():
    etiqueta = request.args.get('etiqueta', '').strip()
    return redirect(url_for('panel_chat.panel_chat', etiqueta=etiqueta or None))

@panel_chat_bp.route('/toggle_ia/<numero>', methods=['POST'])
def toggle_ia(numero):
    try:
        contactos_info = cargar_json(CONTACTOS_INFO, {})
        numero = normalizar_numero(numero)
        estado_actual = contactos_info.get(numero, {}).get("ia_activada", True)
        nuevo_estado = not estado_actual

        if numero not in contactos_info:
            contactos_info[numero] = {"ia_activada": nuevo_estado}
        else:
            contactos_info[numero]["ia_activada"] = nuevo_estado

        guardar_json(CONTACTOS_INFO, contactos_info)
        flash(f'IA {"activada" if nuevo_estado else "desactivada"} correctamente', 'success')
        return jsonify({"success": True, "nuevo_estado": nuevo_estado})
        
    except Exception as e:
        flash(f'Error al cambiar estado de IA: {str(e)}', 'error')
        return jsonify({"success": False, "error": str(e)}), 500

@panel_chat_bp.route('/add_etiqueta/<numero>', methods=['POST'])
def add_etiqueta(numero):
    nueva_etiqueta = request.form.get('nueva_etiqueta', '').strip().lower()
    etiquetas_validas = cargar_json(ETIQUETAS_DISPONIBLES, [])

    if not nueva_etiqueta:
        flash('La etiqueta no puede estar vacía', 'error')
        return redirect(url_for('panel_chat.panel_chat', numero=numero))

    if nueva_etiqueta not in etiquetas_validas:
        flash(f'La etiqueta "{nueva_etiqueta}" no es válida.', 'error')
        return redirect(url_for('panel_chat.panel_chat', numero=numero))

    try:
        contactos_info = cargar_json(CONTACTOS_INFO, {})
        numero = normalizar_numero(numero)

        if numero not in contactos_info:
            contactos_info[numero] = {
                "ia_activada": True,
                "etiquetas": []
            }

        if nueva_etiqueta not in contactos_info[numero].get('etiquetas', []):
            contactos_info[numero].setdefault('etiquetas', []).append(nueva_etiqueta)
            flash(f'Etiqueta "{nueva_etiqueta}" agregada', 'success')
        else:
            flash('Esta etiqueta ya existe', 'warning')

        guardar_json(CONTACTOS_INFO, contactos_info)

    except Exception as e:
        flash(f'Error al agregar etiqueta: {str(e)}', 'error')

    return redirect(url_for('panel_chat.panel_chat', numero=numero))

# Funciones auxiliares
def cargar_json(archivo, default=None):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}

def guardar_json(archivo, data):
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def procesar_contactos(historial, contactos_info):
    contactos = defaultdict(list)
    nombres = {}
    estados_ia = {}

    for mensaje in historial:
        numero = normalizar_numero(mensaje.get("remitente", ""))
        if numero in contactos_info:
            contactos[numero].append(mensaje)
            if "nombre" in mensaje and mensaje["nombre"]:
                nombres[numero] = mensaje["nombre"]
            estados_ia[numero] = contactos_info.get(numero, {}).get("ia_activada", True)

    return contactos, nombres, estados_ia

def ordenar_mensajes(mensajes):
    return sorted(mensajes, key=lambda x: x.get("timestamp", ""))
