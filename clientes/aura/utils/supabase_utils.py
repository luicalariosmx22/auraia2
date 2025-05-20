# ✅ Archivo: clientes/aura/utils/supabase_utils.py
# 👉 Utilidades para gestionar tareas en Supabase

from supabase import create_client
import os

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def obtener_tareas_por_nora(nombre_nora):
    res = supabase.table("tareas").select("*").eq("nombre_nora", nombre_nora).execute()
    return res.data

def crear_tarea(data):
    supabase.table("tareas").insert(data).execute()

def obtener_templates_tarea():
    res = supabase.table("templates_tarea").select("*").execute()
    return res.data
