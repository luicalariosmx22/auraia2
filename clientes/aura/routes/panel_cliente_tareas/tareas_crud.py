from flask import request, jsonify, redirect, session
from .panel_cliente_tareas import panel_cliente_tareas_bp
from datetime import datetime
from supabase import create_client
import os
import uuid

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

print("🧩 cargando tareas_crud.py...")  # 🔍 Diagnóstico en tiempo de arranque del servidor

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
        "fecha_limite": data.get("fecha_limite"),
        "prioridad": data.get("prioridad", "media"),
        "estatus": data.get("estatus", "pendiente"),
        # responsable ⇢ usa la misma columna; quitamos asignado_a porque ya no existe
        "usuario_empresa_id": data["usuario_empresa_id"],
        "empresa_id": data.get("empresa_id"),
        "origen": data.get("origen", "manual"),
        # Si viene vacío → usamos usuario_empresa_id (quien crea normalmente es el responsable)
        "creado_por": data.get("creado_por") or data["usuario_empresa_id"],
        "activo": True,
        "nombre_nora": data.get("nombre_nora"),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    # ─── Inserción ────────────────────────────────────────────────────────
    try:
        result = supabase.table("tareas").insert(nueva).execute()
        return result.data, 200
    except Exception as e:
        print("❌ ERROR insert tarea:", e)
        return {"error": str(e)}, 500

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
    # evitamos clave vacía que rompe la FK
    for k in ("empresa_id", "usuario_empresa_id", "creado_por"):
        if k in data and data[k] == "":
            data[k] = None
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

    usuario_empresa_id = form.get("usuario_empresa_id")
    empresa_id = form.get("empresa_id") or user.get("empresa_id") or ""
    creado_por = user.get("id") or form.get("creado_por") or ""
    titulo = form.get("titulo") or ""
    prioridad = form.get("prioridad") or ""
    fecha_limite = form.get("fecha_limite") or ""
    iniciales_usuario = form.get("iniciales_usuario") or "NN"
    nombre_nora = form.get("nombre_nora") or user.get("nombre_nora", "aura")

    print(f"🧪 creado_por desde form={form.get('creado_por')} | desde session={user.get('id')}")
    print(f"🧪 empresa_id={empresa_id}, creado_por={creado_por}, usuario_empresa_id={usuario_empresa_id}, titulo={titulo}")

    if not usuario_empresa_id or usuario_empresa_id.strip() == "":
        return "❌ Falta usuario_empresa_id", 400
    if not empresa_id or empresa_id.strip() == "":
        return "❌ Falta empresa_id", 400
    if not creado_por or str(creado_por).strip() == "":
        return "❌ Falta creado_por", 400
    if not titulo.strip():
        return "❌ Falta título", 400

    def generar_codigo_tarea(iniciales_usuario):
        fecha = datetime.now().strftime("%d%m%y")
        base_codigo = f"{iniciales_usuario.upper()}-{fecha}"
        existentes = supabase.table("tareas").select("id").ilike("codigo_tarea", f"{base_codigo}-%").execute()
        correlativo = len(existentes.data) + 1
        return f"{base_codigo}-{str(correlativo).zfill(3)}"

    tarea_data = {
        "id": str(uuid.uuid4()),
        "codigo_tarea": generar_codigo_tarea(iniciales_usuario),
        "titulo": titulo,
        "descripcion": form.get("descripcion", ""),
        "fecha_limite": fecha_limite,
        "prioridad": prioridad,
        "estatus": "pendiente",
        "usuario_empresa_id": usuario_empresa_id,  # se usa como “Asignado a”
        "empresa_id": empresa_id,
        "nombre_nora": nombre_nora,
        "creado_por": creado_por,
        "origen": "manual",
        "activo": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    try:
        result = supabase.table("tareas").insert(tarea_data).execute()
        print(f"✅ Tarea insertada desde vista principal: {result.data}")
        return redirect(request.referrer or f"/panel_cliente/{nombre_nora}/tareas")
    except Exception as e:
        print(f"❌ Error al insertar tarea: {e}")
        return f"❌ Error al crear tarea: {e}", 500