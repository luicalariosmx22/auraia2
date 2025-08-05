"""
Cliente Supabase para interactuar con la base de datos.
"""
import os
import time
from dotenv import load_dotenv
from supabase.lib.client_options import ClientOptions
from supabase import create_client, Client
import httpx  # 👈 Asegúrate de importar esto al inicio
import logging
from typing import Dict, Any

# Configurar logger
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Obtener credenciales
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Inicializar cliente con manejo de errores y reintentos
def initialize_supabase():
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            if not SUPABASE_URL or not SUPABASE_KEY:
                print("⚠️ Faltan credenciales de Supabase. Usando cliente dummy.")
                return DummySupabase()

            print(f"Conectando a Supabase... (intento {retry_count + 1})")

            # ✅ Cliente HTTP con timeout extendido
            http_client = httpx.Client(timeout=20.0)
            supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY, http_client=http_client)

            response = supabase_client.table("configuracion_bot").select("*", count="exact").execute()
            print(f"✅ Conexión a Supabase establecida: {len(response.data)} registros encontrados")
            return supabase_client

        except Exception as e:
            print(f"⚠️ Error al conectar a Supabase (intento {retry_count + 1}): {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                print("Reintentando en 2 segundos...")
                time.sleep(2)

    print("❌ No se pudo establecer conexión a Supabase después de múltiples intentos.")
    return DummySupabase()

# Cliente dummy para caso de fallo
class DummySupabase:
    def table(self, name):
        return DummyTable()
    
class DummyTable:
    def select(self, *args, **kwargs):
        return self
    def insert(self, *args, **kwargs):
        return self
    def update(self, *args, **kwargs):
        return self
    def delete(self, *args, **kwargs):
        return self
    def eq(self, *args, **kwargs):
        return self
    def execute(self):
        return type('obj', (object,), {'data': []})

# Inicializar el cliente (ahora con timeout implícito)
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    # Verificamos conexión con una tabla real
    supabase.table("modulos_disponibles").select("*").limit(1).execute()
except Exception as e:
    print(f"❌ Error en Supabase: {e}")
    supabase = DummySupabase()

def get_supabase_client():
    """
    Retorna el cliente de Supabase ya inicializado.
    
    Returns:
        Client: Cliente de Supabase configurado
    """
    return supabase

def get_modulo_config(nombre_modulo: str) -> Dict[str, Any]:
    """
    Obtiene la configuración de un módulo desde Supabase.
    
    Args:
        nombre_modulo: Nombre del módulo a consultar
        
    Returns:
        Configuración del módulo o diccionario vacío si no existe
    """
    try:
        # Corregir nombre de la tabla (usar modulos_disponibles en lugar de modulos_config)
        resultado = supabase.table('modulos_disponibles').select('*').eq('nombre', nombre_modulo).execute()
        return resultado.data[0] if resultado.data else {}
    except Exception as e:
        logger.warning(f"No se pudo consultar Supabase para módulo {nombre_modulo}: {str(e)}")
        return {}