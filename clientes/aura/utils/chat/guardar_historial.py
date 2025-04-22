# clientes/aura/utils/chat/guardar_historial.py
from datetime import datetime
from clientes.aura.utils.supabase import supabase

def guardar_historial(nombre_nora, telefono, mensajes):
    registros = [
        {
            "nombre_nora": nombre_nora,
            "telefono": telefono,
            "mensaje": m.get("texto") or m.get("mensaje"),
            "emisor": m["emisor"],
            "hora": m.get("hora", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "timestamp": datetime.now().isoformat()
        }
        for m in mensajes
    ]
    try:
        supabase.table("historial_conversaciones").insert(registros).execute()
    except Exception as e:
        print(f"❌ Error al guardar historial: {str(e)}")

