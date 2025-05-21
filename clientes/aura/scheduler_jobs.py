# ✅ Archivo: clientes/aura/scheduler_jobs.py
# 👉 Registro centralizado de tareas programadas para APScheduler

from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

# 🧠 Funciones programadas
from clientes.aura.routes.panel_cliente_tareas.whatsapp import (
    enviar_tareas_del_dia_por_whatsapp,
    enviar_resumen_6pm_por_whatsapp
)
from clientes.aura.routes.panel_cliente_tareas.panel_cliente_tareas import (
    enviar_reporte_semanal
)

zona = timezone("America/Hermosillo")

def inicializar_cron_jobs(scheduler):
    print("🕒 Inicializando cron jobs...")

    # ✅ Job: Enviar tareas del día por WhatsApp (8:00 AM)
    scheduler.add_job(
        func=enviar_tareas_del_dia_por_whatsapp,
        trigger=CronTrigger(hour=8, minute=0, timezone=zona),
        id="tareas_whatsapp_8am",
        name="Enviar tareas del día por WhatsApp (8AM)",
        replace_existing=True
    )

    # ✅ Job: Enviar resumen diario por WhatsApp (6:00 PM)
    scheduler.add_job(
        func=enviar_resumen_6pm_por_whatsapp,
        trigger=CronTrigger(hour=18, minute=0, timezone=zona),
        id="tareas_whatsapp_6pm",
        name="Enviar resumen diario por WhatsApp (6PM)",
        replace_existing=True
    )

    # ✅ Job: Enviar reporte semanal (Domingo 9:00 AM)
    scheduler.add_job(
        func=enviar_reporte_semanal,
        trigger=CronTrigger(day_of_week="sun", hour=9, minute=0, timezone=zona),
        id="reporte_semanal",
        name="Reporte semanal PDF por WhatsApp",
        replace_existing=True
    )

    print("✅ Cron jobs registrados.")
