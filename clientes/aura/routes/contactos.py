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

def leer_historial(telefono):
    """
    Simula la lectura del historial de mensajes para un número de teléfono.
    Aquí puedes implementar la lógica para consultar la tabla `historial_conversaciones`.
    """
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

# Mostrar contactos
@contactos_bp.route('/contactos', methods=['GET'])
def ver_contactos():
    try:
        # Obtener parámetros de filtro
        busqueda = request.args.get('busqueda', '').strip()
        orden = request.args.get('orden', 'desc')
        etiqueta = request.args.get('etiqueta', '').strip()

        # Construir consulta
        query = supabase.table("contactos").select("*")
        if busqueda:
            query = query.ilike("nombre", f"%{busqueda}%").ilike("numero", f"%{busqueda}%")
        if etiqueta:
            query = query.contains("etiquetas", [etiqueta])
        query = query.order("primer_mensaje", desc=(orden == 'desc'))

        # Ejecutar consulta
        response_contactos = query.execute()
        if not response_contactos.data:
            print(f"❌ Error al cargar contactos: {not response_contactos.data}")
            return jsonify({"success": False, "error": "Error al cargar contactos"}), 500

        contactos = response_contactos.data
        print(f"🔍 Contactos obtenidos: {contactos}")

        # Obtener el historial y el último mensaje para cada contacto
        for contacto in contactos:
            historial = leer_historial(contacto["numero"])
            ultimo = historial[0] if historial else {}
            contacto["ultimo_mensaje"] = ultimo.get("mensaje", "")
            contacto["fecha_ultimo_mensaje"] = ultimo.get("timestamp", "")

        # Obtener etiquetas únicas
        etiquetas = supabase.table("contactos").select("etiquetas").execute()
        etiquetas = list(set(et for c in etiquetas.data for et in c.get("etiquetas", [])))

        return render_template('panel_cliente_contactos.html', contactos=contactos, etiquetas=etiquetas)
    except Exception as e:
        print(f"❌ Error al cargar contactos: {str(e)}")
        return jsonify({"success": False, "error": "Error al cargar contactos"}), 500

# Agregar un nuevo contacto
@contactos_bp.route('/contactos/agregar', methods=['POST'])
def agregar_contacto():
    datos = request.form
    numero = datos.get('numero').strip()
    nombre = datos.get('nombre').strip()
    correo = datos.get('correo')
    celular = datos.get('celular')
    etiqueta = datos.get('etiqueta')

    if not numero or not nombre:
        return jsonify({"success": False, "error": "El número y el nombre son obligatorios"}), 400

    # Asegurarse de que el número tenga el prefijo 521
    if not numero.startswith("521"):
        numero = f"521{numero[-10:]}"  # Agregar prefijo y truncar a los últimos 10 dígitos
    print(f"🔍 Número con prefijo 521: {numero}")  # Depuración: Verificar el número con prefijo

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
        print(f"✅ Respuesta al agregar contacto: {response.data}")  # Depuración: Verificar la respuesta de Supabase
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

# Acciones con contactos seleccionados
@contactos_bp.route('/contactos/acciones', methods=['POST'])
def acciones_contactos():
    try:
        accion = request.form.get('accion')
        contactos_seleccionados = request.form.getlist('contactos_seleccionados')

        if not contactos_seleccionados:
            return jsonify({"success": False, "error": "No se seleccionaron contactos"}), 400

        if accion == "eliminar":
            # Eliminar contactos seleccionados
            response = supabase.table("contactos").delete().in_("numero", contactos_seleccionados).execute()
            print(f"✅ Contactos eliminados: {response.data}")
            return jsonify({"success": True, "message": "Contactos eliminados correctamente"})

        elif accion == "editar":
            # Aquí puedes redirigir a un formulario de edición o implementar la lógica de edición
            print(f"✏️ Contactos seleccionados para editar: {contactos_seleccionados}")
            return jsonify({"success": True, "message": "Función de edición no implementada aún"})

        else:
            return jsonify({"success": False, "error": "Acción no válida"}), 400
    except Exception as e:
        print(f"❌ Error al realizar acción: {str(e)}")
        return jsonify({"success": False, "error": "Error al realizar acción"}), 500
