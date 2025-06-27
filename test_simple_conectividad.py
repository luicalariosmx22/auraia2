#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

print("🔄 Iniciando diagnóstico simple...")

# Cargar variables de entorno
load_dotenv(".env.local")

# Verificar variables
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

print(f"SUPABASE_URL: {'✅ OK' if supabase_url else '❌ NO'}")
print(f"SUPABASE_KEY: {'✅ OK' if supabase_key else '❌ NO'}")

try:
    from supabase import create_client
    supabase = create_client(supabase_url, supabase_key)
    print("✅ Cliente Supabase creado")
    
    # Test simple de conectividad
    res = supabase.table("conocimiento_nora").select("id").limit(1).execute()
    print(f"✅ Conectividad OK - Datos encontrados: {len(res.data)}")
    
    # Test específico para aura
    res_aura = supabase.table("conocimiento_nora") \
        .select("*") \
        .eq("nombre_nora", "aura") \
        .eq("activo", True) \
        .execute()
    
    print(f"📊 Bloques activos para aura: {len(res_aura.data)}")
    
    if res_aura.data:
        print("🔍 Primeros bloques:")
        for i, bloque in enumerate(res_aura.data[:3]):
            print(f"  {i+1}. {bloque.get('contenido', '')[:50]}...")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("✅ Diagnóstico simple completado")
