# 👉 Detecta si un bloque debe vincularse a un servicio de pagos

from clientes.aura.utils.supabase_client import supabase
import uuid
from datetime import datetime

def vincular_bloque_a_servicio(nombre_nora, bloque_id, etiquetas):
    for etiqueta in etiquetas:
        match = supabase.table("pagos_servicios") \
            .select("id") \
            .eq("nombre_nora", nombre_nora) \
            .ilike("nombre_servicio", f"%{etiqueta}%") \
            .eq("activo", True) \
            .maybe_single().execute()

        if match.data:
            servicio_id = match.data["id"]
            supabase.table("conocimiento_por_servicio").insert({
                "id": str(uuid.uuid4()),
                "nombre_nora": nombre_nora,
                "servicio_id": servicio_id,
                "bloque_id": bloque_id,
                "fecha_vinculo": datetime.utcnow().isoformat()
            }).execute()
