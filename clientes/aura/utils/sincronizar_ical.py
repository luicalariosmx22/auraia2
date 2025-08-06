# ✅ Archivo: clientes/aura/utils/sincronizar_ical.py
# 👉 Descarga y parsea un .ics de Airbnb/Booking para insertar en Supabase
import requests
import uuid
from datetime import datetime
try:
    from icalendar import Calendar
except ImportError:
    print("⚠️ Librería icalendar no instalada. Ejecuta: pip install icalendar")
    Calendar = None

from clientes.aura.utils.supabase_client import supabase

def sincronizar_ical(nombre_nora, url_ical, fuente="airbnb"):
    """
    Descarga y sincroniza eventos desde un archivo .ics (Airbnb/Booking)
    """
    print(f"🔄 Sincronizando calendario desde {fuente} para {nombre_nora}...")

    if Calendar is None:
        print("❌ Error: Librería icalendar no está instalada")
        return {"error": "icalendar no instalada"}

    try:
        # Verificar que la tabla existe
        tabla_nombre = "reservas_airbnb"  # Tabla que existe en Supabase
        
        response = requests.get(url_ical, timeout=30)
        if response.status_code != 200:
            error_msg = f"Error al descargar .ics: {response.status_code}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}

        gcal = Calendar.from_ical(response.content)

        eventos = []
        for component in gcal.walk():
            if component.name != "VEVENT":
                continue

            uid = str(component.get("UID", "")).strip()
            summary = str(component.get("SUMMARY", "")).strip()
            description = str(component.get("DESCRIPTION", "")).strip()
            dtstart = component.get("DTSTART")
            dtend = component.get("DTEND")

            if dtstart and dtend:
                # Manejar tanto datetime como date
                inicio = dtstart.dt
                fin = dtend.dt
                
                if hasattr(inicio, 'isoformat') and hasattr(fin, 'isoformat'):
                    evento = {
                        "id": str(uuid.uuid4()),
                        "nombre_nora": nombre_nora,
                        "fuente": fuente,
                        "url_ical": url_ical,
                        "evento_uid": uid,
                        "titulo": summary,
                        "descripcion": description,
                        "inicio": inicio.isoformat(),
                        "fin": fin.isoformat(),
                        "fecha_importacion": datetime.utcnow().isoformat(),
                        "activa": True,
                    }
                    eventos.append(evento)

        if not eventos:
            print("⚠️ No se encontraron eventos válidos en el calendario")
            return {"error": "No hay eventos válidos"}

        # Insertar eventos uno por uno para evitar errores de duplicados
        insertados = 0
        errores = []
        
        for evento in eventos:
            try:
                # Verificar si ya existe
                existing = supabase.table(tabla_nombre).select("id").eq("evento_uid", evento["evento_uid"]).eq("nombre_nora", nombre_nora).execute()
                
                if not existing.data:
                    # No existe, insertar
                    supabase.table(tabla_nombre).insert(evento).execute()
                    insertados += 1
                else:
                    # Ya existe, actualizar
                    supabase.table(tabla_nombre).update(evento).eq("evento_uid", evento["evento_uid"]).eq("nombre_nora", nombre_nora).execute()
                    
            except Exception as e:
                errores.append(f"Error con evento {evento.get('titulo', 'sin título')}: {str(e)}")
                continue

        resultado = f"✅ {insertados} eventos nuevos sincronizados de {len(eventos)} totales."
        print(resultado)
        
        if errores:
            print(f"⚠️ Errores: {'; '.join(errores[:3])}")  # Solo primeros 3 errores
            
        return {
            "ok": True, 
            "insertados": insertados, 
            "total": len(eventos),
            "errores": errores
        }

    except Exception as e:
        error_msg = f"Error al sincronizar .ics: {str(e)}"
        print(f"❌ {error_msg}")
        return {"error": error_msg}
