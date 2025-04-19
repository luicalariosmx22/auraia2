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

@contactos_bp.route('/contactos', methods=['GET'])
def ver_contactos():
    try:
        # Obtener parámetros de filtro
        busqueda = request.args.get('busqueda', '').strip()
        orden = request.args.get('orden', 'desc')
        etiqueta = request.args.get('etiqueta', '').strip()

        # Obtener todos los contactos
        response_contactos = supabase.table("contactos").select("*").execute()
        contactos = response_contactos.data or []
        print(f"🔍 Contactos base: {len(contactos)}")

        # Filtro manual (por nombre o número)
        if busqueda:
            contactos = [
                c for c in contactos if
                busqueda.lower() in c.get("nombre", "").lower() or
                busqueda in c.get("numero", "")
            ]

        # Filtro por etiqueta
        if etiqueta:
            contactos = [
                c for c in contactos if
                etiqueta in (c.get("etiquetas") or [])
            ]

        # Ordenar por fecha de primer mensaje
        contactos.sort(
            key=lambda c: c.get("primer_mensaje", ""),
            reverse=(orden == "desc")
        )

        # Agregar historial a cada contacto
        for contacto in contactos:
            telefono = contacto.get("telefono") or contacto.get("numero")
            if not telefono:
                continue
            contacto["numero"] = telefono
            historial = leer_historial(telefono)
            ultimo = historial[0] if historial else {}
            contacto["ultimo_mensaje"] = ultimo.get("mensaje", "")
            contacto["fecha_ultimo_mensaje"] = ultimo.get("timestamp", "")

        # Depuración: Imprimir contactos procesados
        print(f"🧪 Lista final de contactos a enviar al template:")
        for c in contactos:
            print(f"📇 {c.get('nombre')} | {c.get('numero')} | Último: {c.get('ultimo_mensaje')}")

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

@contactos_bp.route("/editar/<telefono>", methods=["GET", "POST"])
def editar_contacto(telefono):
    if request.method == "POST":
        nombre = request.form.get("nombre")
        nota = request.form.get("nota")
        correo = request.form.get("correo")
        celular = request.form.get("celular")
        etiquetas = request.form.get("etiquetas")

        print(f"📝 Editando {telefono} con: nombre={nombre}, etiquetas={etiquetas}")
        try:
            response = supabase.table("contactos").update({
                "nombre": nombre,
                "nota": nota,
                "correo": correo,
                "celular": celular,
                "etiquetas": etiquetas
            }).eq("numero", telefono).execute()
            print(f"✅ Contacto actualizado: {response.data}")
            return redirect(url_for("contactos.ver_contactos"))
        except Exception as e:
            print(f"❌ Error al editar contacto: {str(e)}")
            return jsonify({"success": False, "error": "Error al editar contacto"}), 500

    try:
        response = supabase.table("contactos").select("*").eq("numero", telefono).execute()
        if not response.data:
            return jsonify({"success": False, "error": "Contacto no encontrado"}), 404
        contacto = response.data[0]
        return render_template("editar_contacto.html", contacto=contacto)
    except Exception as e:
        print(f"❌ Error al cargar contacto: {str(e)}")
        return jsonify({"success": False, "error": "Error al cargar contacto"}), 500

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
            print(f"✏️ Contactos seleccionados para editar: {seleccionados}")
            return jsonify({"success": True, "message": "Función de edición no implementada"})

        return jsonify({"success": False, "error": "Acción no válida"}), 400
    except Exception as e:
        print(f"❌ Error en acción múltiple: {str(e)}")
        return jsonify({"success": False, "error": "Error al procesar acción"}), 500
