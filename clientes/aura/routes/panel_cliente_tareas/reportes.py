from datetime import datetime
import os
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.twilio_sender import twilio_client

def enviar_reporte_semanal():
    print("📤 Enviando reporte semanal...")

    nora_configs = supabase.table("configuracion_bot").select("nombre_nora, cliente_id").execute().data

    for config in nora_configs:
        nombre_nora = config["nombre_nora"]
        cliente_id = config["cliente_id"]

        completadas = supabase.table("tareas").select("*") \
            .eq("cliente_id", cliente_id).eq("estatus", "completada").eq("activo", True).execute().data

        if not completadas:
            print(f"📭 No hay tareas completadas esta semana para {nombre_nora}")
            continue

        texto = f"📈 Reporte semanal de tareas completadas para {nombre_nora}:\n\n"
        for tarea in completadas:
            texto += f"✅ {tarea['codigo_tarea']}: {tarea['titulo']}\n"

        try:
            twilio_client.messages.create(
                body=texto,
                from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}",
                to=f"whatsapp:{os.getenv('WHATSAPP_ADMIN_DEFAULT', '+521234567890')}"
            )
            print(f"✅ Reporte enviado a admin para {nombre_nora}")
        except Exception as e:
            print(f"❌ Error al enviar reporte a {nombre_nora}: {e}")
