# ✅ Archivo: clientes/aura/routes/panel_cliente_conocimiento/handlers.py
# 👉 Define los handlers para las rutas del panel de conocimiento

from flask import jsonify
from clientes.aura.utils.supabase_client import supabase
from datetime import datetime
import uuid

def handle_listar_bloques(nombre_nora):
    res = supabase.table("conocimiento_nora").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).execute()
    return jsonify(res.data), 200

def handle_crear_bloque(nombre_nora, data):
    contenido = data.get("contenido", "").strip()
    etiquetas = data.get("etiquetas", [])
    prioridad = data.get("prioridad", False)

    if not contenido or len(contenido) > 500:
        return jsonify({"error": "El contenido es obligatorio y debe tener máximo 500 caracteres"}), 400
    if not etiquetas or not isinstance(etiquetas, list) or len(etiquetas) == 0:
        return jsonify({"error": "Debes incluir al menos una etiqueta"}), 400

    nuevo = {
        "id": str(uuid.uuid4()),
        "nombre_nora": nombre_nora,
        "contenido": contenido,
        "etiquetas": etiquetas,
        "origen": "manual",
        "prioridad": bool(prioridad),
        "activo": True,
        "fecha_creacion": datetime.utcnow().isoformat()
    }
    res = supabase.table("conocimiento_nora").insert(nuevo).execute()
    return jsonify(res.data), 201

def handle_editar_bloque(bloque_id, data):
    contenido = data.get("contenido", "").strip()
    etiquetas = data.get("etiquetas", [])
    prioridad = data.get("prioridad", False)

    if not contenido or len(contenido) > 500:
        return jsonify({"error": "El contenido es obligatorio y debe tener máximo 500 caracteres"}), 400
    if not etiquetas or not isinstance(etiquetas, list) or len(etiquetas) == 0:
        return jsonify({"error": "Debes incluir al menos una etiqueta"}), 400

    update = {
        "contenido": contenido,
        "etiquetas": etiquetas,
        "prioridad": bool(prioridad)
    }
    res = supabase.table("conocimiento_nora").update(update).eq("id", bloque_id).execute()
    return jsonify(res.data), 200

def handle_eliminar_bloque(bloque_id):
    supabase.table("conocimiento_nora").update({"activo": False}).eq("id", bloque_id).execute()
    return jsonify({"ok": True}), 200

def handle_listar_por_etiqueta(nombre_nora, etiqueta):
    res = supabase.table("conocimiento_nora").select("*").eq("nombre_nora", nombre_nora).contains("etiquetas", [etiqueta]).eq("activo", True).execute()
    return jsonify(res.data), 200

def handle_listar_tipo_menu(nombre_nora):
    res = supabase.table("conocimiento_nora").select("*").eq("nombre_nora", nombre_nora).eq("origen", "menu").eq("activo", True).execute()
    return jsonify(res.data), 200

def handle_conocimiento_por_servicio(nombre_nora, servicio_id):
    # Paso 1: Obtener todos los bloque_id vinculados a ese servicio
    vinculos = supabase.table("conocimiento_por_servicio") \
        .select("bloque_id") \
        .eq("nombre_nora", nombre_nora) \
        .eq("servicio_id", servicio_id) \
        .execute()
    
    bloque_ids = [v["bloque_id"] for v in vinculos.data]

    if not bloque_ids:
        return jsonify([]), 200

    # Paso 2: Traer los bloques activos con esos IDs
    bloques = supabase.table("conocimiento_nora") \
        .select("*") \
        .in_("id", bloque_ids) \
        .eq("activo", True) \
        .execute()

    return jsonify(bloques.data), 200