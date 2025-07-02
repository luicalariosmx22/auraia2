#!/usr/bin/env python3
"""
Script para verificar y activar el módulo Google Ads para la Nora 'aura'
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables de entorno
load_dotenv()

# Configurar Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def verificar_y_activar_google_ads():
    """Verifica si Google Ads está activado para 'aura' y lo activa si no lo está"""
    nombre_nora = "aura"
    
    try:
        # Obtener configuración actual
        config = supabase.table("configuracion_bot") \
            .select("modulos") \
            .eq("nombre_nora", nombre_nora) \
            .single() \
            .execute()
        
        modulos_actuales = config.data.get("modulos", [])
        print(f"Módulos actuales para {nombre_nora}: {modulos_actuales}")
        
        # Verificar si google_ads ya está activado
        google_ads_activado = False
        for modulo in modulos_actuales:
            if isinstance(modulo, dict):
                if modulo.get("nombre", "").lower().strip() == "google_ads":
                    google_ads_activado = True
                    break
            elif isinstance(modulo, str):
                if modulo.lower().strip() == "google_ads":
                    google_ads_activado = True
                    break
        
        if google_ads_activado:
            print("✅ Google Ads ya está activado para 'aura'")
            return True
        
        # Activar Google Ads
        print("🚀 Activando Google Ads para 'aura'...")
        
        # Agregar el módulo a la lista existente
        nuevo_modulo = {"nombre": "google_ads"}
        modulos_actuales.append(nuevo_modulo)
        
        # Actualizar en Supabase
        result = supabase.table("configuracion_bot") \
            .update({"modulos": modulos_actuales}) \
            .eq("nombre_nora", nombre_nora) \
            .execute()
        
        print("✅ Google Ads activado exitosamente")
        print(f"Módulos actualizados: {modulos_actuales}")
        return True
        
    except Exception as e:
        print(f"❌ Error al verificar/activar Google Ads: {e}")
        return False

if __name__ == "__main__":
    verificar_y_activar_google_ads()
