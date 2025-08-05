# ✅ Archivo: clientes/aura/scheduler_jobs.py
# 👉 Registro centralizado de tareas programadas para APScheduler

from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

# 🧠 Funciones programadas
from clientes.aura.routes.panel_cliente_tareas.whatsapp import (
    enviar_tareas_del_dia_por_whatsapp,
    enviar_resumen_6pm_por_whatsapp
)
from clientes.aura.routes.panel_cliente_tareas.reportes import enviar_reporte_meta_ads
from clientes.aura.utils.twilio_sender import enviar_mensaje

zona = timezone("America/Hermosillo")

def inicializar_cron_jobs(scheduler):
    """
    Inicializa los trabajos programados con APScheduler.
    """
    try:
        from apscheduler.triggers.cron import CronTrigger
        from datetime import datetime
        import logging
        logger = logging.getLogger(__name__)
        
        # Evitamos inicializar dos veces
        if getattr(inicializar_cron_jobs, 'initialized', False):
            logger.info("Los cron jobs ya fueron inicializados, omitiendo...")
            return
        
        logger.info("Inicializando cron jobs...")

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
            func=enviar_reporte_meta_ads,
            trigger=CronTrigger(day_of_week="sun", hour=9, minute=0, timezone=zona),
            id="reporte_meta_ads",
            name="Reporte semanal PDF por WhatsApp",
            replace_existing=True
        )

        # Marcar como inicializado
        inicializar_cron_jobs.initialized = True
        logger.info("Cron jobs inicializados correctamente")
        
    except Exception as e:
        print(f"❌ Error al inicializar cron jobs: {str(e)}")
        # No propagamos la excepción para evitar que la aplicación falle
