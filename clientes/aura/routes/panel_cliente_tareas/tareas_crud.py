from flask import request, jsonify, redirect, session, render_template, Blueprint
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
    usuario_empresa_id = (data.get("usuario_empresa_id") or "").strip()
    titulo = (data.get("titulo") or "").strip()
    if not usuario_empresa_id:
        return {"error": "usuario_empresa_id es obligatorio"}, 400
    if not titulo:
        return {"error": "titulo es obligatorio"}, 400

    def sanea_uuid(val):
        return val.strip() or None if isinstance(val, str) else val

    nueva = {
        "id": str(uuid.uuid4()),
        "codigo_tarea": generar_codigo_tarea(data.get("iniciales_usuario", "NN")),
        "titulo": titulo,
        "descripcion": data.get("descripcion") or "",
        "fecha_limite": data.get("fecha_limite") or None,
        #  ➜ guardamos la prioridad ya normalizada
        # ─────────────────────────── prioridad ────────────────────────────
        "prioridad": (data.get("prioridad") or "media").strip().lower(),
        "estatus": data.get("estatus", "pendiente"),
        "usuario_empresa_id": usuario_empresa_id,
        "empresa_id": sanea_uuid(data.get("empresa_id", "")),
        "origen": data.get("origen", "manual"),
        "creado_por": sanea_uuid(data.get("creado_por") or usuario_empresa_id),
        "activo": True,
        "nombre_nora": data.get("nombre_nora"),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    print("🚀 Payload a insertar:", nueva)

    try:
        result = supabase.table("tareas").insert(nueva).execute()
        return result.data, 200
    except Exception as e:
        print("❌ Error insertando tarea:", e)
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
    if data.get("empresa_id") == "":
        data.pop("empresa_id")
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

    es_supervisor = user.get("es_supervisor", False)

    empresa_id = form.get("empresa_id") if es_supervisor else user.get("empresa_id")
    usuario_empresa_id = form.get("usuario_empresa_id") if es_supervisor else user.get("usuario_empresa_id")

    creado_por_form = form.get("creado_por", "").strip()
    creado_por = creado_por_form if creado_por_form else user.get("id") or ""
    titulo = form.get("titulo") or ""
    prioridad = form.get("prioridad") or ""
    fecha_limite = form.get("fecha_limite") or ""
    iniciales_usuario = form.get("iniciales_usuario") or "NN"
    nombre_nora = form.get("nombre_nora") or user.get("nombre_nora", "aura")

    print(f"🧪 creado_por final={creado_por}")
    print(f"🧪 empresa_id={empresa_id}, creado_por={creado_por}, usuario_empresa_id={usuario_empresa_id}, titulo={titulo}")

    if not usuario_empresa_id.strip():
        return "❌ Falta usuario_empresa_id", 400
    if not empresa_id.strip():
        return "❌ Falta empresa_id", 400
    if not creado_por.strip():
        return "❌ Falta creado_por", 400
    if not titulo.strip():
        return "❌ Falta título", 400

    # Eliminada la función local generar_codigo_tarea, se usa la global
    tarea_data = {
        "id": str(uuid.uuid4()),
        "codigo_tarea": generar_codigo_tarea(iniciales_usuario),
        "titulo": titulo,
        "descripcion": form.get("descripcion", ""),
        "fecha_limite": fecha_limite,
        "prioridad": prioridad,
        "estatus": "pendiente",
        "usuario_empresa_id": usuario_empresa_id,
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

@panel_cliente_tareas_bp.route("/<nombre_nora>/tareas")
def panel_tareas(nombre_nora):
    if not session.get("email"):
        return redirect("/login")

    if session.get("nombre_nora") != nombre_nora:
        return "Acceso denegado", 403

    is_admin = session.get("is_admin", False)
    usuarios_disponibles = []

    if is_admin:
        usuarios_disponibles = supabase.table("usuarios_clientes").select("id,nombre")\
            .eq("nombre_nora", nombre_nora).execute().data or []

    return render_template("panel_cliente_tareas/panel.html",
                           nombre_nora=nombre_nora,
                           is_admin=is_admin,
                           usuarios_disponibles=usuarios_disponibles)

panel_tareas_crud_bp = Blueprint(
    "panel_tareas_crud", __name__,
    template_folder="../../../templates/panel_cliente_tareas"
)

# Aquí puedes agregar tus rutas
@panel_tareas_crud_bp.route("/panel_cliente/<nombre_nora>/tareas/prueba", methods=["GET"])
def prueba_crud(nombre_nora):
    return f"Vista de prueba CRUD para {nombre_nora}"

@panel_tareas_crud_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar/crear", methods=["POST"])
def crear_tarea_gestionar(nombre_nora):
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    tarea, status = crear_tarea(data)
    if status == 200:
        tarea_id = tarea[0].get("id") if isinstance(tarea, list) and tarea and isinstance(tarea[0], dict) else None
        return jsonify({"ok": True, "id": tarea_id})
    else:
        return jsonify({"ok": False, "error": tarea.get("error", "Error desconocido")}), status

@panel_cliente_tareas_bp.route("/<nombre_nora>/tareas/obtener/<tarea_id>")
def obtener_tarea(nombre_nora, tarea_id):
    tarea = obtener_tarea_por_id(tarea_id)
    if tarea:
        return jsonify(tarea)
    else:
        return jsonify({"error": "Tarea no encontrada"}), 404

@panel_cliente_tareas_bp.route("/<nombre_nora>/tareas/gestionar/actualizar/<tarea_id>", methods=["POST"])
def actualizar_tarea_inline(nombre_nora, tarea_id):
    datos = request.get_json()
    campo = datos.get("campo")
    valor = datos.get("valor")

    if not campo:
        return jsonify({"ok": False, "error": "Campo no especificado"})

    try:
        supabase.table("tareas").update({campo: valor}).eq("id", tarea_id).execute()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

# ✅ Ruta DELETE para eliminar tarea
@panel_tareas_crud_bp.route("/tareas/gestionar/eliminar/<tarea_id>", methods=["DELETE"])
def eliminar_tarea(tarea_id):
    try:
        supabase.table("tareas").delete().eq("id", tarea_id).execute()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})