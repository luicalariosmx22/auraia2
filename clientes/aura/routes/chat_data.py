from flask import Blueprint, jsonify
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

chat_data_bp = Blueprint('chat_data_aura', __name__)

@chat_data_bp.route("/chat/<numero>")
def chat_historial(numero):
    try:
        # Consultar historial desde la tabla historial_conversaciones
        response = supabase.table("historial_conversaciones").select("*").eq("telefono", numero).execute()
        if not response.data:
            print(f"❌ Error al cargar historial para {numero}: {response.error}")
            return jsonify({"nombre": "Desconocido", "historial": []})

        historial = response.data
        nombre = historial[0]["nombre"] if historial and "nombre" in historial[0] else "Sin nombre"

        return jsonify({"nombre": nombre, "historial": historial})
    except Exception as e:
        print(f"❌ Error al cargar historial para {numero}: {str(e)}")
        return jsonify({"nombre": "Desconocido", "historial": []})
