from flask import Blueprint, request, jsonify, render_template
import json
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Cargar el archivo de contactos
CONTACTOS_FILE = 'contactos_info.json'

# Ruta de contactos
contactos_bp = Blueprint('contactos', __name__)

# Función para leer los contactos del archivo
def leer_contactos():
    try:
        with open(CONTACTOS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Función para guardar contactos en el archivo
def guardar_contactos(contactos):
    with open(CONTACTOS_FILE, 'w', encoding='utf-8') as file:
        json.dump(contactos, file, ensure_ascii=False, indent=4)

# Mostrar contactos
@contactos_bp.route('/contactos', methods=['GET'])
def ver_contactos():
    contactos = leer_contactos()
    primeros_últimos_contactos = {
        'primer_contacto': min(contactos.items(), key=lambda x: x[1]['primer_mensaje'], default=None),
        'ultimo_contacto': max(contactos.items(), key=lambda x: x[1]['ultimo_mensaje'], default=None)
    }
    return render_template('contactos.html', contactos=contactos, primeros_últimos_contactos=primeros_últimos_contactos)

# Agregar un nuevo contacto
@contactos_bp.route('/contactos/agregar', methods=['POST'])
def agregar_contacto():
    datos = request.form
    numero = datos.get('numero')
    nombre = datos.get('nombre')
    correo = datos.get('correo')
    celular = datos.get('celular')
    etiqueta = datos.get('etiqueta')
    
    contactos = leer_contactos()

    if numero in contactos:
        return jsonify({"success": False, "error": "Este contacto ya existe."}), 400

    # Agregar nuevo contacto con la fecha actual como primer y último mensaje
    contactos[numero] = {
        "numero": numero,
        "nombre": nombre,
        "correo": correo,
        "celular": celular,
        "etiquetas": etiqueta,
        "primer_mensaje": datetime.now().isoformat(),
        "ultimo_mensaje": datetime.now().isoformat()
    }

    guardar_contactos(contactos)
    return jsonify({"success": True})

# Editar contacto
@contactos_bp.route('/contactos/editar/<numero>', methods=['PUT'])
def editar_contacto(numero):
    datos = request.form
    nombre = datos.get('nombre')
    correo = datos.get('correo')
    celular = datos.get('celular')
    etiqueta = datos.get('etiqueta')
    
    contactos = leer_contactos()

    if numero not in contactos:
        return jsonify({"success": False, "error": "Este contacto no existe."}), 400

    # Actualizar información del contacto
    contactos[numero].update({
        "nombre": nombre,
        "correo": correo,
        "celular": celular,
        "etiquetas": etiqueta,
        "ultimo_mensaje": datetime.now().isoformat()  # Actualizar última vez que se editó
    })

    guardar_contactos(contactos)
    return jsonify({"success": True})

# Eliminar contacto
@contactos_bp.route('/contactos/eliminar/<numero>', methods=['DELETE'])
def eliminar_contacto(numero):
    contactos = leer_contactos()

    if numero not in contactos:
        return jsonify({"success": False, "error": "Este contacto no existe."}), 400

    del contactos[numero]
    guardar_contactos(contactos)
    return jsonify({"success": True})

# Exportar contactos a Google Sheets
@contactos_bp.route('/contactos/exportar', methods=['GET'])
def exportar_a_sheets():
    # Cargar credenciales para la API de Google
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = 'path_to_your_service_account.json'  # Cambiar a la ruta de tu archivo JSON de credenciales

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('sheets', 'v4', credentials=credentials)

    # ID de la hoja de cálculo de Google Sheets
    SPREADSHEET_ID = 'your_spreadsheet_id_here'  # Cambiar por el ID de tu hoja de cálculo
    range_ = 'Sheet1!A1'  # Cambiar si tienes otra hoja o rango específico

    # Leer contactos
    contactos = leer_contactos()

    # Convertir los contactos a un formato que Google Sheets pueda aceptar
    valores = []
    for numero, datos in contactos.items():
        valores.append([
            numero, 
            datos['nombre'], 
            datos['correo'], 
            datos['celular'], 
            datos['etiquetas'],
            datos['primer_mensaje'],
            datos['ultimo_mensaje']
        ])

    body = {
        'values': valores
    }

    # Hacer la actualización de los datos en la hoja de Google Sheets
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_,
        valueInputOption='RAW',
        body=body
    ).execute()

    return jsonify({"success": True})
