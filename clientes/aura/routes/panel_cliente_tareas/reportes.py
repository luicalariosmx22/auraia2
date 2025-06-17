from datetime import datetime
import os
from pytz import timezone
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.twilio_sender import enviar_mensaje  # ✅ Corrección aquí

zona = timezone("America/Hermosillo")

def enviar_reporte_meta_ads():
    print("📤 Enviando reporte semanal...")

    # Obtener todas las configuraciones de bots
    nora_configs = supabase.table("configuracion_bot").select("nombre_nora, cliente_id").execute().data or []

    for config in nora_configs:
        nombre_nora = config["nombre_nora"]
        cliente_id = config["cliente_id"]

        completadas = supabase.table("tareas").select("*") \
            .eq("cliente_id", cliente_id) \
            .eq("estatus", "completada") \
            .eq("activo", True).execute().data or []

        if not completadas:
            print(f"📭 No hay tareas completadas esta semana para {nombre_nora}")
            continue

        numero_admin = os.getenv("WHATSAPP_ADMIN_DEFAULT", "+521234567890")

        texto = f"📈 Reporte semanal de tareas completadas para {nombre_nora}:\n\n"
        for tarea in completadas:
            texto += f"✅ {tarea['codigo_tarea']}: {tarea['titulo']}\n"

        try:
            respuesta = enviar_mensaje(numero_admin, texto)
            print(f"✅ Reporte enviado a {numero_admin} ({nombre_nora}) - Status: {respuesta.get('status')}")
        except Exception as e:
            print(f"❌ Error al enviar reporte a {nombre_nora}: {e}")
