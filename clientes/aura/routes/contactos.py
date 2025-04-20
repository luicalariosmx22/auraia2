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
        response = supabase.table("contactos").update(data).eq("telefono", telefono).execute()
        print(f"✅ Contacto actualizado: {response.data}")
        return True
    except Exception as e:
        print(f"❌ Error al actualizar contacto: {str(e)}")
        return False

def obtener_contacto(telefono):
    try:
        response = supabase.table("contactos").select("*").eq("telefono", telefono).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"❌ Error al obtener contacto: {str(e)}")
        return None

@contactos_bp.route('/<nombre_nora>/contactos', methods=['GET'])
def ver_contactos(nombre_nora):
    try:
        print(f"📍 Ruta con Nora: {nombre_nora}")

        # Obtener parámetros de búsqueda
        busqueda = request.args.get('busqueda', '').strip().lower()
        fecha_inicio = request.args.get('fecha_inicio', None)
        fecha_fin = request.args.get('fecha_fin', None)
        etiqueta = request.args.get('etiqueta', '').strip()

        # Imprimir los parámetros recibidos
        print(f"📩 Parámetros recibidos: busqueda={busqueda}, fecha_inicio={fecha_inicio}, fecha_fin={fecha_fin}, etiqueta={etiqueta}")

        # Construir la consulta base
        query = supabase.table("contactos").select("*").eq("nombre_nora", nombre_nora)

        # Filtro por nombre o teléfono
        if busqueda:
            query = query.or_("nombre.ilike.*{0}*,telefono.ilike.*{0}*".format(busqueda))

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
        if response.status_code != 200:
            raise Exception(f"Error en la consulta de contactos: {response.error_message}")

        contactos = response.data or []

        # Si la solicitud es AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": True, "contactos": contactos})

        # Obtener etiquetas únicas
        etiquetas_response = supabase.table("contactos").select("etiquetas").execute()
        if etiquetas_response.status_code != 200:
            raise Exception(f"Error en la consulta de etiquetas: {etiquetas_response.error_message}")

        etiquetas = list(set(
            et for c in etiquetas_response.data for et in c.get("etiquetas", []) if et
        ))

        return render_template('panel_cliente_contactos.html', contactos=contactos, etiquetas=etiquetas, nombre_nora=nombre_nora)
    except Exception as e:
        print(f"❌ Error al cargar contactos: {str(e)}")
        return jsonify({"success": False, "error": "Error al cargar contactos"}), 500

@contactos_bp.route('/contactos/agregar', methods=['POST'])
def agregar_contacto():
    datos = request.form
    telefono = datos.get('telefono', '').strip()
    nombre = datos.get('nombre', '').strip()
    correo = datos.get('correo')
    celular = datos.get('celular')
    etiqueta = datos.get('etiqueta')

    if not telefono or not nombre:
        return jsonify({"success": False, "error": "El teléfono y el nombre son obligatorios"}), 400

    if not telefono.startswith("521"):
        telefono = f"521{telefono[-10:]}"
    print(f"🔍 Teléfono normalizado: {telefono}")

    try:
        response = supabase.table("contactos").insert({
            "telefono": telefono,
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

@contactos_bp.route('/contactos/eliminar/<telefono>', methods=['DELETE'])
def eliminar_contacto(telefono):
    try:
        response = supabase.table("contactos").delete().eq("telefono", telefono).execute()
        print(f"🗑️ Contacto eliminado: {telefono}")
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
            [c.get("telefono"), c.get("nombre"), c.get("correo"), c.get("celular"), c.get("etiquetas"), c.get("primer_mensaje"), c.get("ultimo_mensaje")]
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
            response = supabase.table("contactos").delete().in_("telefono", seleccionados).execute()
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
