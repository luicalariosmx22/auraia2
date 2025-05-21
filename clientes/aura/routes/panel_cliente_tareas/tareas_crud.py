from flask import request, jsonify
from .panel_cliente_tareas import panel_cliente_tareas_bp
from datetime import datetime
from supabase import create_client
import os
import uuid

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# ✅ Generar código único para tareas
def generar_codigo_tarea(iniciales_usuario):
    fecha = datetime.now().strftime("%d%m%y")
    iniciales = ''.join(filter(str.isalnum, iniciales_usuario.upper()))[:3]
    base_codigo = f"{iniciales}-{fecha}"
    existentes = supabase.table("tareas").select("id").ilike("codigo_tarea", f"{base_codigo}-%").execute()
    correlativo = len(existentes.data) + 1
    return f"{base_codigo}-{str(correlativo).zfill(3)}"

# ✅ Crear tarea
def crear_tarea(data):
    if not data.get("usuario_empresa_id"):
        return {"error": "La tarea debe estar asignada a un usuario"}, 400

    iniciales = data.get("iniciales_usuario", "NN")
    codigo = generar_codigo_tarea(iniciales)
    fecha_limite = data.get("fecha_limite")

    if fecha_limite and fecha_limite < datetime.now().strftime("%Y-%m-%d"):
        fecha_limite = datetime.now().strftime("%Y-%m-%d")

    nueva = {
        "id": str(uuid.uuid4()),
        "codigo_tarea": codigo,
        "titulo": data.get("titulo"),
        "descripcion": data.get("descripcion"),
        "fecha_limite": fecha_limite,
        "prioridad": data.get("prioridad", "media"),
        "estatus": data.get("estatus", "pendiente"),
        "usuario_empresa_id": data["usuario_empresa_id"],
        "asignado_a": data.get("asignado_a"),
        "empresa_id": data.get("empresa_id"),
        "cliente_id": data.get("cliente_id"),
        "origen": data.get("origen", "manual"),
        "creado_por": data.get("creado_por"),
        "activo": True,
        "nombre_nora": data.get("nombre_nora"),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    result = supabase.table("tareas").insert(nueva).execute()
    return result.data, 200

# ✅ Obtener una tarea por ID
def obtener_tarea_por_id(tarea_id):
    result = supabase.table("tareas").select("*").eq("id", tarea_id).single().execute()
    return result.data

# ✅ Listar tareas por usuario
def listar_tareas_por_usuario(usuario_empresa_id):
    result = supabase.table("tareas").select("*") \
        .eq("usuario_empresa_id", usuario_empresa_id) \
        .eq("activo", True) \
        .order("fecha_limite", desc=False).execute()
    return result.data

# ✅ Actualizar una tarea
def actualizar_tarea(tarea_id, data):
    data["updated_at"] = datetime.now().isoformat()
    result = supabase.table("tareas").update(data).eq("id", tarea_id).execute()
    return result.data

# ✅ Eliminar (desactivar) una tarea
def eliminar_tarea(tarea_id):
    result = supabase.table("tareas").update({
        "activo": False,
        "updated_at": datetime.now().isoformat()
    }).eq("id", tarea_id).execute()
    return result.data

@panel_cliente_tareas_bp.route("/crear_tarea", methods=["POST"])
def endpoint_crear_tarea():
    data = request.json
    tarea, status = crear_tarea(data)
    return jsonify(tarea), status