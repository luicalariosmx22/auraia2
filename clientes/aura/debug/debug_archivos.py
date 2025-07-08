print("✅ debug_archivos.py cargado correctamente")

from flask import Blueprint, jsonify
from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

debug_archivos_bp = Blueprint("debug_archivos", __name__, url_prefix="/debug")

@debug_archivos_bp.route("/archivos")
def verificar_archivos():
    # Tablas esperadas en Supabase
    tablas_esperadas = {
        "bot_data": "Tabla de datos del bot",
        "historial_conversaciones": "Tabla de historial de conversaciones",
        "configuracion_bot": "Tabla de configuración del bot",
        "categorias": "Tabla de categorías",
        "base_conocimiento": "Tabla de servicios de conocimiento"
    }

    faltantes = []

    # Verificar si las tablas contienen datos
    for tabla, descripcion in tablas_esperadas.items():
        response = supabase.table(tabla).select("*").limit(1).execute()
        if not response.data:
            faltantes.append({"tabla": tabla, "descripcion": descripcion})

    if faltantes:
        print("❌ Tablas faltantes o vacías:", faltantes)
        return jsonify({
            "ok": False,
            "faltantes": faltantes
        })

    print("✅ Todas las tablas requeridas contienen datos")
    return jsonify({
        "ok": True,
        "mensaje": "Todas las tablas requeridas contienen datos"
    })