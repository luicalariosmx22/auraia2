# clientes/aura/utils/schema_config.py

"""
Configuración para mantener los esquemas de Supabase actualizados.
Este archivo define cuándo y cómo actualizar los esquemas automáticamente.
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# Configuración de actualización automática
SCHEMA_CONFIG = {
    # Intervalo de actualización en horas
    "update_interval_hours": 24,
    
    # Archivo donde se almacena la última actualización
    "last_update_file": "clientes/aura/utils/.schema_last_update",
    
    # Archivo de esquemas generado
    "schema_file": "clientes/aura/utils/supabase_schemas.py",
    
    # Script generador
    "generator_script": "clientes/aura/scripts/generar_supabase_schema.py",
    
    # Tablas críticas que siempre deben estar presentes
    "critical_tables": [
        "meta_ads_cuentas", 
        "meta_ads_anuncios_detalle", 
        "meta_ads_reportes_semanales",
        "configuracion_bot", 
        "contactos", 
        "clientes",
        "google_ads_cuentas"
    ],
    
    # Configuración de logging
    "log_schema_updates": True,
    "log_file": "clientes/aura/logs/schema_updates.log"
}

def necesita_actualizacion():
    """Verifica si los esquemas necesitan ser actualizados"""
    last_update_file = Path(SCHEMA_CONFIG["last_update_file"])
    
    if not last_update_file.exists():
        return True
    
    try:
        with open(last_update_file, 'r') as f:
            data = json.load(f)
            last_update = datetime.fromisoformat(data["last_update"])
            
        # Verificar si ha pasado el intervalo de actualización
        now = datetime.now()
        time_diff = now - last_update
        
        return time_diff.total_seconds() > (SCHEMA_CONFIG["update_interval_hours"] * 3600)
        
    except Exception:
        return True

def marcar_actualizado():
    """Marca que los esquemas fueron actualizados recientemente"""
    last_update_file = Path(SCHEMA_CONFIG["last_update_file"])
    last_update_file.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        "last_update": datetime.now().isoformat(),
        "schema_file": SCHEMA_CONFIG["schema_file"],
        "tables_count": 0  # Se actualizará después
    }
    
    with open(last_update_file, 'w') as f:
        json.dump(data, f, indent=2)

def verificar_esquemas_disponibles():
    """Verifica que el archivo de esquemas existe y está actualizado"""
    schema_file = Path(SCHEMA_CONFIG["schema_file"])
    
    if not schema_file.exists():
        return False, "Archivo de esquemas no existe"
    
    # Verificar que el archivo no esté vacío
    try:
        with open(schema_file, 'r') as f:
            content = f.read()
            if "SUPABASE_SCHEMAS" not in content:
                return False, "Archivo de esquemas está corrupto"
    except Exception as e:
        return False, f"Error leyendo esquemas: {e}"
    
    return True, "Esquemas disponibles"

def obtener_info_esquemas():
    """Obtiene información sobre el estado actual de los esquemas"""
    schema_file = Path(SCHEMA_CONFIG["schema_file"])
    last_update_file = Path(SCHEMA_CONFIG["last_update_file"])
    
    info = {
        "schema_file_exists": schema_file.exists(),
        "last_update_file_exists": last_update_file.exists(),
        "needs_update": necesita_actualizacion(),
        "last_update": None,
        "tables_count": 0
    }
    
    if last_update_file.exists():
        try:
            with open(last_update_file, 'r') as f:
                data = json.load(f)
                info["last_update"] = data.get("last_update")
                info["tables_count"] = data.get("tables_count", 0)
        except Exception:
            pass
    
    return info
