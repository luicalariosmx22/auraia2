from flask import Blueprint, request, jsonify, render_template, redirect, url_for
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

contactos_bp = Blueprint('contactos', __name__)

def leer_historial(telefono):
    try:
        response_historial = supabase.table("historial_conversaciones") \
            .select("mensaje, timestamp") \
            .eq("telefono", telefono) \
            .order("timestamp", desc=True) \
            .execute()
        return response_historial.data
    except Exception as e:
        print(f"❌ Error al leer historial para {telefono}: {str(e)}")
        return []

def actualizar_contacto(telefono, data):
    try:
        response = supabase.table("contactos").update(data).eq("numero", telefono).execute()
        print(f"✅ Contacto actualizado: {response.data}")
        return True
    except Exception as e:
        print(f"❌ Error al actualizar contacto: {str(e)}")
        return False

def obtener_contacto(telefono):
    try:
        response = supabase.table("contactos").select("*").eq("numero", telefono).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"❌ Error al obtener contacto: {str(e)}")
        return None

@contactos_bp.route('/contactos', methods=['GET'])
def ver_contactos():
    try:
        # Obtener parámetros de búsqueda
        busqueda = request.args.get('busqueda', '').strip().lower()
        fecha_inicio = request.args.get('fecha_inicio', None)
        fecha_fin = request.args.get('fecha_fin', None)
        etiqueta = request.args.get('etiqueta', '').strip()

        # Construir la consulta base
        query = supabase.table("contactos").select("*")

        # Filtro por nombre o teléfono
        if busqueda:
            query = query.or_(
                f"nombre.ilike.%{busqueda}%,telefono.ilike.%{busqueda}%"
            )

        # Filtro por rango de fechas
        if fecha_inicio:
            query = query.gte("ultimo_mensaje", fecha_inicio)
        if fecha_fin:
            query = query.lte("ultimo_mensaje", fecha_fin)

        # Filtro por etiqueta
        if etiqueta:
            query = query.contains("etiquetas", [etiqueta])

        # Ejecutar la consulta
        response = query.execute()
        contactos = response.data or []

        # Obtener etiquetas únicas
        etiquetas_response = supabase.table("contactos").select("etiquetas").execute()
        etiquetas = list(set(
            et for c in etiquetas_response.data for et in c.get("etiquetas", []) if et
        ))

        return render_template('panel_cliente_contactos.html', contactos=contactos, etiquetas=etiquetas)
    except Exception as e:
        print(f"❌ Error al cargar contactos: {str(e)}")
        return jsonify({"success": False, "error": "Error al cargar contactos"}), 500

@contactos_bp.route('/contactos/agregar', methods=['POST'])
def agregar_contacto():
    datos = request.form
    numero = datos.get('numero', '').strip()
    nombre = datos.get('nombre', '').strip()
    correo = datos.get('correo')
    celular = datos.get('celular')
    etiqueta = datos.get('etiqueta')

    if not numero or not nombre:
        return jsonify({"success": False, "error": "El número y el nombre son obligatorios"}), 400

    if not numero.startswith("521"):
        numero = f"521{numero[-10:]}"
    print(f"🔍 Número normalizado: {numero}")

    try:
        response = supabase.table("contactos").insert({
            "numero": numero,
            "nombre": nombre,
            "correo": correo,
            "celular": celular,
            "etiquetas": [etiqueta] if etiqueta else [],
            "primer_mensaje": datetime.now().isoformat(),
            "ultimo_mensaje": datetime.now().isoformat()
        }).execute()
        print(f"✅ Contacto agregado: {response.data}")
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error al agregar contacto: {str(e)}")
        return jsonify({"success": False, "error": "Error al agregar contacto"}), 500

@contactos_bp.route('/contactos/editar/<telefono>', methods=['GET', 'POST'])
def editar_contacto(telefono):
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        celular = request.form.get('celular')
        etiquetas = request.form.get('etiquetas').split(',')  # Convertir etiquetas en lista

        # Actualizar el contacto en la base de datos
        data = {
            "nombre": nombre,
            "correo": correo,
            "celular": celular,
            "etiquetas": etiquetas
        }
        response = actualizar_contacto(telefono, data)
        if response:
            return redirect(url_for('contactos.ver_contactos'))
        else:
            return jsonify({"success": False, "error": "Error al actualizar el contacto"}), 500

    # Si es una solicitud GET, obtener los datos del contacto
    contacto = obtener_contacto(telefono)
    if not contacto:
        return jsonify({"success": False, "error": "Contacto no encontrado"}), 404

    return render_template('editar_contacto.html', contacto=contacto)

@contactos_bp.route('/contactos/eliminar/<numero>', methods=['DELETE'])
def eliminar_contacto(numero):
    try:
        response = supabase.table("contactos").delete().eq("numero", numero).execute()
        print(f"🗑️ Contacto eliminado: {numero}")
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error al eliminar contacto: {str(e)}")
        return jsonify({"success": False, "error": "Error al eliminar contacto"}), 500

@contactos_bp.route('/contactos/exportar', methods=['GET'])
def exportar_a_sheets():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = 'path_to_your_service_account.json'
    SPREADSHEET_ID = 'your_spreadsheet_id_here'
    RANGE_ = 'Sheet1!A1'

    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)

        response = supabase.table("contactos").select("*").execute()
        contactos = response.data or []
        valores = [
            [c.get("numero"), c.get("nombre"), c.get("correo"), c.get("celular"), c.get("etiquetas"), c.get("primer_mensaje"), c.get("ultimo_mensaje")]
            for c in contactos
        ]

        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_,
            valueInputOption='RAW',
            body={'values': valores}
        ).execute()

        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error al exportar contactos: {str(e)}")
        return jsonify({"success": False, "error": "Error al exportar contactos"}), 500

@contactos_bp.route('/contactos/acciones', methods=['POST'])
def acciones_contactos():
    try:
        accion = request.form.get('accion')
        seleccionados = request.form.getlist('contactos_seleccionados')
        if not seleccionados:
            return jsonify({"success": False, "error": "No se seleccionaron contactos"}), 400

        if accion == "eliminar":
            response = supabase.table("contactos").delete().in_("numero", seleccionados).execute()
            print(f"✅ Contactos eliminados: {response.data}")
            return jsonify({"success": True})

        elif accion == "editar":
            if len(seleccionados) != 1:
                return jsonify({"success": False, "error": "Selecciona un solo contacto para editar"}), 400
            telefono = seleccionados[0]
            return redirect(url_for('contactos.editar_contacto', telefono=telefono))

        return jsonify({"success": False, "error": "Acción no válida"}), 400
    except Exception as e:
        print(f"❌ Error en acción múltiple: {str(e)}")
        return jsonify({"success": False, "error": "Error al procesar acción"}), 500
