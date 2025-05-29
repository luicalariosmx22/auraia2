from apscheduler.schedulers.background import BackgroundScheduler
from dateutil.rrule import rrulestr
from datetime import datetime, timedelta
import uuid
import pytz
import logging
from clientes.aura.utils.supabase_client import supabase

logger = logging.getLogger("cron_tareas_recurrentes")

def crear_instancia_tarea(original, nueva_fecha):
    nueva_tarea = {
        "id": str(uuid.uuid4()),
        "codigo_tarea": original["codigo_tarea"],
        "titulo": original["titulo"],
        "descripcion": original.get("descripcion", ""),
        "fecha_limite": nueva_fecha.date().isoformat(),
        "prioridad": original.get("prioridad", "media"),
        "estatus": "pendiente",
        "empresa_id": original.get("empresa_id"),
        "usuario_empresa_id": original.get("usuario_empresa_id"),
        "creado_por": original.get("creado_por"),
        "nombre_nora": original["nombre_nora"],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }

    try:
        supabase.table("tareas").insert(nueva_tarea).execute()
        logger.info(f"✅ Tarea recurrente generada para fecha {nueva_fecha}")
    except Exception as e:
        logger.error(f"❌ Error al crear tarea recurrente: {e}")

def verificar_tareas_recurrentes():
    try:
        resp = supabase.table("tareas_recurrentes").select("*").eq("active", True).execute()
        recurrentes = resp.data or []

        for rec in recurrentes:
            tarea_id = rec["tarea_id"]
            rrule_str = rec["rrule"]
            dtstart = datetime.fromisoformat(rec["dtstart"])

            # Obtener la última tarea activa asociada
            tarea_resp = supabase.table("tareas").select("*") \
                .eq("id", tarea_id).limit(1).execute()

            if not tarea_resp.data:
                continue

            original = tarea_resp.data[0]
            if original["estatus"] != "completada":
                continue

            # Generar reglas RRULE y obtener la siguiente fecha
            rule = rrulestr(rrule_str, dtstart=dtstart)
            now = datetime.now(pytz.utc)

            siguiente = rule.after(now - timedelta(minutes=1), inc=True)
            if not siguiente:
                continue

            # Buscar si ya existe una tarea con esa fecha_limite
            ya_creada = supabase.table("tareas").select("id") \
                .eq("codigo_tarea", original["codigo_tarea"]) \
                .eq("fecha_limite", siguiente.date().isoformat()) \
                .execute()

            if not ya_creada.data:
                crear_instancia_tarea(original, siguiente)

    except Exception as e:
        logger.error(f"❌ Error general en verificación de tareas recurrentes: {e}")

def iniciar_cron_recurrentes():
    scheduler = BackgroundScheduler()
    scheduler.add_job(verificar_tareas_recurrentes, "interval", minutes=10)
    scheduler.start()
