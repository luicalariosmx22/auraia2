print("✅ debug_mensaje_hola.py cargado correctamente")

from flask import Blueprint, jsonify
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

debug_mensaje_hola_bp = Blueprint("debug_mensaje_hola", __name__, url_prefix="/debug")

@debug_mensaje_hola_bp.route("/mensaje_hola")
def verificar_mensaje_hola():
    try:
        # Consultar datos desde la tabla bot_data en Supabase
        response = supabase.table("bot_data").select("*").execute()
        if not response.data:
            print("❌ No se encontraron datos en la tabla bot_data")
            return jsonify({"ok": False, "error": "No se encontraron datos en la tabla bot_data"})

        # Buscar la clave "hola" en los datos
        data = response.data[0]  # Suponiendo que solo hay un registro
        if "hola" not in data:
            print("❌ Clave 'hola' no encontrada en la tabla bot_data")
            return jsonify({"ok": False, "error": "La clave 'hola' no fue encontrada en la tabla bot_data"})

        print("✅ La tabla bot_data contiene la clave 'hola'")
        return jsonify({
            "ok": True,
            "mensaje": "La tabla bot_data contiene la clave 'hola'",
            "respuesta": data["hola"]
        })

    except Exception as e:
        print(f"❌ Error al consultar la tabla bot_data: {str(e)}")
        return jsonify({"ok": False, "error": f"Error al consultar la tabla bot_data: {str(e)}"})
