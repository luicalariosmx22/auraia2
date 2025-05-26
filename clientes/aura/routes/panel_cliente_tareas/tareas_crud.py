from flask import request, jsonify, redirect, session
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
    print("🔵 endpoint_crear_tarea llamado")
    data = request.json
    print(f"🔵 Datos recibidos: {data}")
    tarea, status = crear_tarea(data)
    print(f"🔵 Resultado crear_tarea: {tarea}, status: {status}")
    return jsonify(tarea), status

@panel_cliente_tareas_bp.route("/guardar-tarea", methods=["POST"])
def guardar_tarea_html():
    print("🔵 guardar_tarea_html llamado")
    form = request.form
    print(f"🔵 Formulario recibido: {form}")
    user = session.get("user", {})
    print(f"🔵 Usuario de sesión: {user}")
    nombre_nora = user.get("nombre_nora", "aura")
    cliente_id = user.get("cliente_id", "")
    creado_por = user.get("nombre", "Desconocido")
    iniciales_usuario = "".join([w[0] for w in user.get("nombre", "NN").split()]) if user.get("nombre") else "NN"

    tarea_data = {
        "titulo": form.get("titulo"),
        "descripcion": form.get("descripcion"),
        "prioridad": form.get("prioridad"),
        "fecha_limite": form.get("fecha_limite"),
        "asignado_a": form.get("asignado_a"),
        "empresa_id": form.get("empresa_id"),
        "usuario_empresa_id": form.get("asignado_a"),  # temporalmente igual a asignado
        "cliente_id": cliente_id,
        "nombre_nora": nombre_nora,
        "creado_por": creado_por,
        "iniciales_usuario": iniciales_usuario,
        "origen": "manual"
    }
    print(f"🔵 tarea_data a crear: {tarea_data}")

    resultado, status = crear_tarea(tarea_data)
    print(f"🔵 Resultado de creación: status={status}, resultado={resultado}")

    if status != 200:
        return f"❌ Error al crear tarea: {resultado}", 500

    return redirect(request.referrer or f"/panel_cliente/{nombre_nora}/tareas")