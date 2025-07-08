# 📁 Archivo: clientes/aura/utils/startup_check.py

import os
from supabase import create_client
from dotenv import load_dotenv

# Configurar Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def verificar_tabla(tabla, descripcion):
    """
    Verifica si una tabla existe en Supabase y contiene datos.
    :param tabla: Nombre de la tabla en Supabase.
    :param descripcion: Descripción de la tabla para los mensajes de salida.
    """
    try:
        response = supabase.table(tabla).select("*").limit(1).execute()
        if not response.data:
            print(f"⚠️ Tabla '{tabla}' ({descripcion}) no encontrada o vacía.")
        else:
            print(f"✅ Tabla '{tabla}' ({descripcion}) verificada.")
    except Exception as e:
        print(f"❌ Error al verificar tabla '{tabla}': {e}")

def verificar_entorno():
    """
    Verifica que las variables de entorno necesarias estén configuradas.
    """
    claves = [
        "OPENAI_API_KEY",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER"
    ]
    for clave in claves:
        if not os.getenv(clave):
            print(f"⚠️ Falta variable de entorno: {clave}")
        else:
            print(f"🔐 {clave} configurada")

def inicializar_nora():
    """
    Verifica la configuración inicial de Nora AI, incluyendo tablas en Supabase y variables de entorno.
    """
    print("🧩 Iniciando verificación de entorno y estructura para Nora AI...")

    # Verificar tablas necesarias en Supabase
    tablas = {
        "logs_errores": "Registro de errores",
        "historial_conversaciones": "Historial de conversaciones",
        "contactos": "Información de contactos",
        "settings": "Configuración del sistema",
        "bot_data": "Respuestas automáticas",
        "conocimiento": "Base de conocimiento"
    }

    for tabla, descripcion in tablas.items():
        verificar_tabla(tabla, descripcion)

    # Verificar variables de entorno
    verificar_entorno()

    print("✅ Inicialización completa.")

# Llamar esta función desde app.py o manualmente si se desea
if __name__ == "__main__":
    inicializar_nora()