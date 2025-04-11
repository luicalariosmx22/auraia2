from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import json
from collections import defaultdict
import os
from utils.normalizador import normalizar_numero
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
from werkzeug.utils import secure_filename

panel_chat_bp = Blueprint('panel_chat', __name__)
ARCHIVO_HISTORIAL = "historial_conversaciones.json"
CONTACTOS_INFO = "contactos_info.json"
ETIQUETAS_DISPONIBLES = "etiquetas.json"
UPLOAD_FOLDER = os.path.join("static", "uploads")

csrf = CSRFProtect()

# ========== RUTAS PRINCIPALES ==========

@panel_chat_bp.route('/panel/chat', methods=['GET', 'POST'])
def panel_chat():
    numero_seleccionado = request.args.get('numero')
    etiqueta_seleccionada = request.args.get('etiqueta')

    # Cargar los datos de los contactos y del historial
    contactos_info = cargar_json(CONTACTOS_INFO, {})
    historial = cargar_json(ARCHIVO_HISTORIAL, [])

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
            ruta_completa = os.path.join(UPLOAD_FOLDER, nombre_archivo)
            archivo.save(ruta_completa)
            nuevo_mensaje["archivo"] = nombre_archivo

        historial.append(nuevo_mensaje)
        guardar_json(ARCHIVO_HISTORIAL, historial)
        return redirect(url_for('panel_chat.panel_chat', numero=numero))

    # Filtrar contactos si se selecciona una etiqueta
    if etiqueta_seleccionada:
        contactos_info = {
            k: v for k, v in contactos_info.items() 
            if 'etiquetas' in v and etiqueta_seleccionada in v['etiquetas']
        }

    contactos, nombres_contactos, ia_estado_contactos = procesar_contactos(historial, contactos_info)

    numero_normalizado = normalizar_numero(numero_seleccionado or "")

    return render_template(
        "panel_chat.html",
        contactos=sorted(contactos.keys()),
        mensajes=ordenar_mensajes(contactos.get(numero_normalizado, [])),
        seleccionado=numero_normalizado,
        nombres=nombres_contactos,
        ia_estado_contactos=ia_estado_contactos,
        etiquetas={k: v.get("etiquetas", []) for k, v in contactos_info.items()},
        etiquetas_disponibles=cargar_json(ETIQUETAS_DISPONIBLES, []),
        etiqueta_filtrada=etiqueta_seleccionada,
        notas=cargar_notas(),
        notas_modificadas=cargar_notas_modificadas()
    )

# ========== GESTIÓN DE CONTACTOS (NUEVO) ==========

@panel_chat_bp.route('/agregar-contacto', methods=['GET', 'POST'])
def agregar_contacto():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        numero = request.form.get('numero', '').strip()
        etiquetas = [e.strip() for e in request.form.get('etiquetas', '').split(',') if e.strip()]
        
        if not nombre or not numero:
            flash('❌ Nombre y número son obligatorios', 'error')
            return redirect(url_for('panel_chat.agregar_contacto'))
        
        numero = normalizar_numero(numero)
        contactos_info = cargar_json(CONTACTOS_INFO, {})
        
        if numero in contactos_info:
            flash('❌ El número ya está registrado', 'error')
        else:
            contactos_info[numero] = {
                "nombre": nombre,
                "ia_activada": True,
                "etiquetas": etiquetas,
                "fecha_registro": obtener_timestamp_actual()
            }
            guardar_json(CONTACTOS_INFO, contactos_info)
            flash('✅ Contacto agregado correctamente', 'success')
            return redirect(url_for('panel_chat.panel_chat'))
    
    return render_template('agregar_contacto.html', 
                         etiquetas_disponibles=cargar_json(ETIQUETAS_DISPONIBLES, []))

@panel_chat_bp.route('/editar-contacto/<numero>', methods=['GET', 'POST'])
def editar_contacto(numero):
    contactos_info = cargar_json(CONTACTOS_INFO, {})
    contacto = contactos_info.get(numero)
    
    if not contacto:
        flash('❌ Contacto no encontrado', 'error')
        return redirect(url_for('panel_chat.panel_chat'))
    
    if request.method == 'POST':
        nuevo_nombre = request.form.get('nombre', '').strip()
        nuevas_etiquetas = [e.strip() for e in request.form.get('etiquetas', '').split(',') if e.strip()]
        
        if nuevo_nombre:
            contacto['nombre'] = nuevo_nombre
        contacto['etiquetas'] = nuevas_etiquetas
        
        guardar_json(CONTACTOS_INFO, contactos_info)
        flash('✅ Contacto actualizado', 'success')
        return redirect(url_for('panel_chat.panel_chat', numero=numero))
    
    return render_template('editar_contacto.html', 
                         contacto=contacto,
                         numero=numero,
                         etiquetas_disponibles=cargar_json(ETIQUETAS_DISPONIBLES, []))

# ========== FUNCIONES EXISTENTES ==========

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

# ========== FUNCIONES AUXILIARES ==========

def cargar_json(archivo, default=None):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}

def guardar_json(archivo, data):
    os.makedirs(os.path.dirname(archivo), exist_ok=True)
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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

def cargar_notas():
    return cargar_json("notas.json", {})

def cargar_notas_modificadas():
    return cargar_json("notas_modificadas.json", {})

def obtener_timestamp_actual():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
