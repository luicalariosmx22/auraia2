from supabase import create_client
from dotenv import load_dotenv
import os

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def registrar_blueprints_por_nora(app, nombre_nora):
    try:
        print(f"🔍 Registrando blueprints dinámicos para la Nora: {nombre_nora}...")

        # Consultar módulos activos desde Supabase
        response = supabase.table("configuracion_bot").select("modulos").eq("nombre_nora", nombre_nora).execute()
        modulos = response.data[0].get("modulos", [])

        if "contactos" in modulos:
            from clientes.aura.routes.contactos import contactos_bp
            app.register_blueprint(contactos_bp, url_prefix=f'/{nombre_nora}/contactos')
            print(f"✅ Módulo: contactos registrado correctamente con prefijo dinámico '/{nombre_nora}/contactos'.")
    except Exception as e:
        print(f"❌ Error al registrar blueprints dinámicos: {str(e)}")