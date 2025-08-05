from supabase import create_client
import logging

logger = logging.getLogger(__name__)

SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-secret-api-key"

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table("usuarios").select("*").execute()
    logger.info(f"✅ Supabase respuesta: {response.data}")
except Exception as e:
    logger.error(f"❌ Error al conectar o consultar Supabase: {e}")
