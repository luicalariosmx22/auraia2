import os
from datetime import datetime, timedelta
from supabase import create_client
from dotenv import load_dotenv

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def cargar_historial(numero):
    """
    Carga el historial de conversaciones desde la tabla `historial_conversaciones` en Supabase.
    """
    try:
        response = supabase.table("historial_conversaciones").select("*").eq("telefono", numero).order("hora", desc=True).execute()
        if not response.data:
            print(f"❌ Error al cargar historial para {numero}: {not response.data}")
            return []
        return response.data
    except Exception as e:
        print(f"❌ Error al cargar historial para {numero}: {str(e)}")
        return []

def ya_saludo(historial):
    """
    Verifica si el bot ya saludó en el historial.
    """
    for mensaje in historial:
        if mensaje["origen"] == "bot" and "hola" in mensaje["mensaje"].lower():
            return True
    return False

def tiempo_ultima_interaccion(historial):
    """
    Obtiene la hora de la última interacción en el historial.
    """
    if not historial:
        return None
    ultimo = historial[0]  # El historial ya está ordenado por hora descendente
    try:
        hora = datetime.strptime(ultimo["hora"], "%Y-%m-%d %H:%M:%S")
        return hora
    except Exception as e:
        print(f"❌ Error al parsear la hora de la última interacción: {str(e)}")
        return None

def debe_saludar(numero):
    """
    Determina si el bot debe saludar al usuario.
    """
    historial = cargar_historial(numero)
    return not ya_saludo(historial)

def debe_preguntar_si_hay_duda(numero):
    """
    Determina si el bot debe preguntar al usuario si tiene alguna duda.
    """
    historial = cargar_historial(numero)
    ultima_hora = tiempo_ultima_interaccion(historial)

    if not ultima_hora:
        return False

    ahora = datetime.now()
    diferencia = ahora - ultima_hora

    if diferencia > timedelta(hours=1):
        return True
    return False
