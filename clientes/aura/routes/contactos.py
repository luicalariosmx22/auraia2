from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Ruta de contactos
contactos_bp = Blueprint('contactos', __name__)

# Mostrar contactos
@contactos_bp.route('/contactos', methods=['GET'])
def ver_contactos():
    try:
        response = supabase.table("contactos").select("*").execute()
        if not response.data:
            print(f"❌ Error al cargar contactos: {not response.data}")
            return jsonify({"success": False, "error": "Error al cargar contactos"}), 500

        contactos = {c["numero"]: c for c in response.data}

        primeros_últimos_contactos = {
            'primer_contacto': min(contactos.items(), key=lambda x: x[1]['primer_mensaje'], default=None),
            'ultimo_contacto': max(contactos.items(), key=lambda x: x[1]['ultimo_mensaje'], default=None)
        }
        return render_template('contactos.html', contactos=contactos, primeros_últimos_contactos=primeros_últimos_contactos)
    except Exception as e:
        print(f"❌ Error al cargar contactos: {str(e)}")
        return jsonify({"success": False, "error": "Error al cargar contactos"}), 500

# Agregar un nuevo contacto
@contactos_bp.route('/contactos/agregar', methods=['POST'])
def agregar_contacto():
    datos = request.form
    numero = datos.get('numero')
    nombre = datos.get('nombre')
    correo = datos.get('correo')
    celular = datos.get('celular')
    etiqueta = datos.get('etiqueta')

    if not numero or not nombre:
        return jsonify({"success": False, "error": "El número y el nombre son obligatorios"}), 400

    try:
        response = supabase.table("contactos").insert({
            "numero": numero,
            "nombre": nombre,
            "correo": correo,
            "celular": celular,
            "etiquetas": etiqueta,
            "primer_mensaje": datetime.now().isoformat(),
            "ultimo_mensaje": datetime.now().isoformat()
        }).execute()
        if not response.data:
            print(f"❌ Error al agregar contacto: {not response.data}")
            return jsonify({"success": False, "error": "Error al agregar contacto"}), 400
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error al agregar contacto: {str(e)}")
        return jsonify({"success": False, "error": "Error al agregar contacto"}), 500

# Editar contacto
@contactos_bp.route('/contactos/editar/<numero>', methods=['PUT'])
def editar_contacto(numero):
    datos = request.form
    nombre = datos.get('nombre')
    correo = datos.get('correo')
    celular = datos.get('celular')
    etiqueta = datos.get('etiqueta')

    if not nombre:
        return jsonify({"success": False, "error": "El nombre es obligatorio"}), 400

    try:
        response = supabase.table("contactos").update({
            "nombre": nombre,
            "correo": correo,
            "celular": celular,
            "etiquetas": etiqueta,
            "ultimo_mensaje": datetime.now().isoformat()
        }).eq("numero", numero).execute()
        if not response.data:
            print(f"❌ Error al editar contacto: {not response.data}")
            return jsonify({"success": False, "error": "Error al editar contacto"}), 400
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error al editar contacto: {str(e)}")
        return jsonify({"success": False, "error": "Error al editar contacto"}), 500

# Eliminar contacto
@contactos_bp.route('/contactos/eliminar/<numero>', methods=['DELETE'])
def eliminar_contacto(numero):
    try:
        response = supabase.table("contactos").delete().eq("numero", numero).execute()
        if not response.data:
            print(f"❌ Error al eliminar contacto: {not response.data}")
            return jsonify({"success": False, "error": "Error al eliminar contacto"}), 400
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error al eliminar contacto: {str(e)}")
        return jsonify({"success": False, "error": "Error al eliminar contacto"}), 500

# Exportar contactos a Google Sheets
@contactos_bp.route('/contactos/exportar', methods=['GET'])
def exportar_a_sheets():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = 'path_to_your_service_account.json'  # Cambiar a la ruta de tu archivo JSON de credenciales

    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)

        SPREADSHEET_ID = 'your_spreadsheet_id_here'  # Cambiar por el ID de tu hoja de cálculo
        range_ = 'Sheet1!A1'  # Cambiar si tienes otra hoja o rango específico

        # Leer contactos desde Supabase
        response = supabase.table("contactos").select("*").execute()
        if not response.data:
            print(f"❌ Error al cargar contactos: {not response.data}")
            return jsonify({"success": False, "error": "Error al cargar contactos"}), 500

        contactos = response.data
        valores = [
            [c["numero"], c["nombre"], c["correo"], c["celular"], c["etiquetas"], c["primer_mensaje"], c["ultimo_mensaje"]]
            for c in contactos
        ]

        body = {'values': valores}
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_,
            valueInputOption='RAW',
            body=body
        ).execute()

        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error al exportar contactos: {str(e)}")
        return jsonify({"success": False, "error": "Error al exportar contactos"}), 500
