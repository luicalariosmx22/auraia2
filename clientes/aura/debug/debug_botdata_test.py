print("✅ debug_botdata_test.py cargado correctamente")

from flask import Blueprint, jsonify
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Prefijo correcto para que funcione con /debug/test_botdata
debug_test_bp = Blueprint("debug_test_bp", __name__, url_prefix="/debug")

@debug_test_bp.route("/test_botdata")
def test_botdata():
    try:
        # Consultar datos desde la tabla bot_data en Supabase
        response = supabase.table("bot_data").select("*").execute()
        if not response.data:
            return jsonify({
                "ok": False,
                "error": "No se encontraron datos en la tabla bot_data."
            })

        # Extraer las claves disponibles en los datos
        data = response.data
        claves_disponibles = list(data[0].keys()) if data else []

        return jsonify({
            "ok": True,
            "mensaje": "Datos cargados correctamente desde Supabase.",
            "claves_disponibles": claves_disponibles
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        })
