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
        # Obtener todos los contactos desde Supabase
        response_contactos = supabase.table("contactos").select("*").execute()
        if not response_contactos.data:
            print(f"❌ Error al cargar contactos: {not response_contactos.data}")
            return jsonify({"success": False, "error": "Error al cargar contactos"}), 500

        contactos = []
        for contacto in response_contactos.data:
            # Obtener el último mensaje del historial para este contacto
            response_historial = supabase.table("historial_conversaciones") \
                .select("mensaje, timestamp") \
                .eq("telefono", contacto["numero"]) \
                .order("timestamp", desc=True) \
                .limit(1) \
                .execute()

            ultimo_mensaje = response_historial.data[0] if response_historial.data else {"mensaje": "Sin mensajes", "timestamp": "N/A"}

            # Agregar los datos del contacto junto con el último mensaje
            contactos.append({
                "numero": contacto["numero"],
                "nombre": contacto["nombre"],
                "correo": contacto.get("correo", "N/A"),
                "celular": contacto.get("celular", "N/A"),
                "ultimo_mensaje": ultimo_mensaje["timestamp"],
                "cantidad_mensajes": contacto.get("cantidad_mensajes", 0),
                "ultimo_texto": ultimo_mensaje["mensaje"]
            })

        # Depuración: Verificar los datos procesados
        print(f"🔍 Contactos procesados: {contactos}")

        return render_template('contactos.html', contactos=contactos)
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
