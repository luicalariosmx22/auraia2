from flask import Blueprint, render_template
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

admin_debug_rutas_bp = Blueprint("admin_debug_rutas", __name__)

def extraer_rutas_desde_templates(templates_path):
    """
    Extrae rutas desde los archivos de plantilla HTML.

    Args:
        templates_path (str): Ruta al directorio de plantillas.

    Returns:
        list: Lista de rutas extraídas.
    """
    rutas = []
    try:
        for root, _, files in os.walk(templates_path):
            for file in files:
                if file.endswith(".html"):
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        contenido = f.read()
                        # Aquí puedes usar expresiones regulares para buscar rutas en el contenido
                        if "href=" in contenido:
                            rutas.append(file)  # Ejemplo: agrega el nombre del archivo como ruta
    except Exception as e:
        print(f"❌ Error al extraer rutas desde plantillas: {str(e)}")
    return rutas

@admin_debug_rutas_bp.route("/admin/debug/rutas")
def ver_rutas_registradas():
    try:
        response = supabase.table("rutas_registradas").select("*").order("registrado_en", desc=True).execute()
        rutas = response.data if response.data else []
        return render_template("admin_debug_rutas.html", rutas=rutas)
    except Exception as e:
        return f"<h3>❌ Error al obtener rutas: {e}</h3>"
