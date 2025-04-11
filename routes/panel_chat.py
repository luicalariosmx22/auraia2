from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from .services import agregar_contacto_service, editar_contacto_service, eliminar_contacto_service, toggle_ia_service
from .utils import cargar_json, guardar_json, normalizar_numero
from datetime import datetime
from collections import defaultdict
import os

panel_chat_bp = Blueprint('panel_chat', __name__)

# ========== RUTAS PRINCIPALES ==========

@panel_chat_bp.route('/panel/chat', methods=['GET', 'POST'])
def panel_chat():
    numero_seleccionado = request.args.get('numero')
    etiqueta_seleccionada = request.args.get('etiqueta')

    # Cargar los datos de los contactos y del historial
    contactos_info = cargar_json('contactos_info.json', {})
    historial = cargar_json('historial_conversaciones.json', [])

    if request.method == 'POST':
        mensaje = request.form.get('respuesta', '').strip()
        numero = request.form.get('numero')
        archivo = request.files.get('archivo')

        # Validar que el número y mensaje no estén vacíos
        if not numero or (not mensaje and not archivo):
            flash("❌ El número y el mensaje son obligatorios", "error")
            return redirect(url_for('panel_chat.panel_chat', numero=numero))

        nuevo_mensaje = {
            "remitente": numero,
            "mensaje": mensaje,
            "timestamp": obtener_timestamp_actual()
        }

        if archivo and archivo.filename:
            nombre_archivo = secure_filename(archivo.filename)
            ruta_completa = os.path.join("static", "uploads", nombre_archivo)
            archivo.save(ruta_completa)
            nuevo_mensaje["archivo"] = nombre_archivo

        historial.append(nuevo_mensaje)
        guardar_json('historial_conversaciones.json', historial)
        return redirect(url_for('panel_chat.panel_chat', numero=numero))

    # Filtrar los contactos por etiqueta seleccionada
    if etiqueta_seleccionada:
        contactos_info = {
            k: v for k, v in contactos_info.items()
            if 'etiquetas' in v and etiqueta_seleccionada in v['etiquetas']
        }

    # Procesar los contactos y mensajes
    contactos, nombres_contactos, ia_estado_contactos = procesar_contactos(historial, contactos_info)

    # Normalizar el número del contacto seleccionado
    numero_normalizado = normalizar_numero(numero_seleccionado or "")

    return render_template(
        "panel_chat.html",
        contactos=sorted(contactos.keys()),
        mensajes=ordenar_mensajes(contactos.get(numero_normalizado, [])),
        seleccionado=numero_normalizado,
        nombres=nombres_contactos,
        ia_estado_contactos=ia_estado_contactos,
        etiquetas={k: v.get("etiquetas", []) for k, v in contactos_info.items()},
        etiquetas_disponibles=cargar_json('etiquetas.json', []),
        etiqueta_filtrada=etiqueta_seleccionada,
        notas=cargar_json('notas.json', {}),
        notas_modificadas=cargar_json('notas_modificadas.json', {})
    )

# ========== GESTIÓN DE CONTACTOS (NUEVO) ==========

@panel_chat_bp.route('/agregar-contacto', methods=['GET', 'POST'])
def agregar_contacto():
    return agregar_contacto_service(request)

@panel_chat_bp.route('/editar-contacto/<numero>', methods=['GET', 'POST'])
def editar_contacto(numero):
    return editar_contacto_service(numero, request)

@panel_chat_bp.route('/eliminar-contacto/<numero>', methods=['POST'])
def eliminar_contacto(numero):
    return eliminar_contacto_service(numero)

@panel_chat_bp.route('/toggle_ia/<numero>', methods=['POST'])
def toggle_ia(numero):
    return toggle_ia_service(numero)

# ========== FUNCIONES AUXILIARES ==========

def obtener_timestamp_actual():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def procesar_contactos(historial, contactos_info):
    contactos = defaultdict(list)
    nombres = {}
    estados_ia = {}

    for mensaje in historial:
        remitente = mensaje.get("remitente", "")
        numero = normalizar_numero(remitente.replace("whatsapp:", ""))

        contactos[numero].append(mensaje)

        if numero in contactos_info:
            if "nombre" in contactos_info[numero]:
                nombres[numero] = contactos_info[numero]["nombre"]
            estados_ia[numero] = contactos_info[numero].get("ia_activada", True)
        else:
            nombres[numero] = remitente
            estados_ia[numero] = True

    return contactos, nombres, estados_ia

def ordenar_mensajes(mensajes):
    return sorted(mensajes, key=lambda x: x.get("timestamp", ""))
