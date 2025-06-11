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
    import re
    fecha = datetime.now().strftime("%d%m%y")
    iniciales = ''.join(filter(str.isalnum, iniciales_usuario.upper()))[:3]
    base_codigo = f"{iniciales}-{fecha}"
    # Buscar solo el máximo correlativo existente
    max_codigo = supabase.table("tareas") \
        .select("codigo_tarea") \
        .ilike("codigo_tarea", f"{base_codigo}-%") \
        .order("codigo_tarea", desc=True) \
        .limit(1) \
        .execute()
    if max_codigo.data:
        last = max_codigo.data[0]["codigo_tarea"]
        m = re.match(rf"{base_codigo}-(\\d+)", last)
        correlativo = int(m.group(1)) + 1 if m else 1
    else:
        correlativo = 1
    return f"{base_codigo}-{str(correlativo).zfill(3)}"

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

# ✅ Listar tareas por usuario (PAGINADO)
def listar_tareas_paginado(usuario_empresa_id, page=1, page_size=20):
    try:
        page = int(page) if page else 1
        page_size = int(page_size) if page_size else 20
        offset = (page - 1) * page_size
        # Consulta paginada
        res = supabase.table("tareas").select("*", count="exact") \
            .eq("usuario_empresa_id", usuario_empresa_id) \
            .eq("activo", True) \
            .order("fecha_limite", desc=False) \
            .range(offset, offset + page_size - 1) \
            .execute()
        return {
            "tareas": res.data or [],
            "total": res.count or 0,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        print(f"❌ Error en paginación: {e}")
        return {"tareas": [], "total": 0, "page": page, "page_size": page_size, "error": str(e)}

# ✅ Actualizar una tarea
def actualizar_tarea(tarea_id, data):
    data["updated_at"] = datetime.now().isoformat()
    # evitamos clave vacía que rompe la FK
    if data.get("empresa_id") == "":
        data.pop("empresa_id")
    result = supabase.table("tareas").update(data).eq("id", tarea_id).execute()
    return result.data

# ✅ Eliminar (desactivar) una tarea
# def eliminar_tarea(tarea_id):
#     result = supabase.table("tareas").update({
#         "activo": False,
#         "updated_at": datetime.now().isoformat()
#     }).eq("id", tarea_id).execute()
#     return result.data

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

@panel_tareas_crud_bp.route("/panel_cliente/<nombre_nora>/tareas/crear", methods=["POST"])
def crear_tarea_backend(nombre_nora):
    """
    Punto de entrada desde el modal moderno (JS) para crear una nueva tarea o subtarea.
    """
    from flask import request, jsonify
    datos = request.get_json() if request.is_json else request.form.to_dict()
    if not datos:
        return jsonify({"error": "No se recibió payload válido"}), 400

    usuario_empresa_id = (datos.get("usuario_empresa_id") or "").strip()
    titulo = (datos.get("titulo") or "").strip()
    hoy = datetime.now().strftime("%Y-%m-%d")

    try:
        # Verifica si ya existe la tarea con el mismo título hoy
        hoy = datetime.now().strftime("%Y-%m-%d")
        existe = supabase.table("tareas").select("id").eq("usuario_empresa_id", usuario_empresa_id) \
            .eq("titulo", titulo).gte("created_at", f"{hoy}T00:00:00").lte("created_at", f"{hoy}T23:59:59").execute()
        if existe.data:
            print("⚠️ Ya existe una tarea con ese título hoy. No se crea duplicado.")
            return jsonify({"ok": True, "id": existe.data[0]["id"]}), 200

        # Generación única de código_tarea
        while True:
            codigo_generado = generar_codigo_tarea(datos.get("iniciales_usuario", "NN"))
            existe_codigo = supabase.table("tareas").select("id").eq("codigo_tarea", codigo_generado).execute()
            if not existe_codigo.data:
                break

        nueva = {
            "id": str(uuid.uuid4()),
            "codigo_tarea": codigo_generado,
            "titulo": titulo,
            "descripcion": datos.get("descripcion", "").strip(),
            "prioridad": (datos.get("prioridad") or "media").strip().lower(),
            "estatus": datos.get("estatus", "pendiente"),
            "fecha_limite": datos.get("fecha_limite") or None,
            "usuario_empresa_id": usuario_empresa_id,
            "empresa_id": datos.get("empresa_id") or None,
            "creado_por": datos.get("creado_por"),
            "nombre_nora": datos.get("nombre_nora"),
            "activo": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        print("🚨 Intentando insertar tarea nueva:", nueva)
        try:
            result = supabase.table("tareas").insert(nueva).execute()
            tarea_creada = result.data[0]
        except Exception as e:
            if 'duplicate key value violates unique constraint' in str(e) and 'tareas_codigo_tarea_key' in str(e):
                print("⚠️ Código duplicado detectado en último paso. Reintentando generación...")
                while True:
                    codigo_generado = generar_codigo_tarea(datos.get("iniciales_usuario", "NN"))
                    existe_codigo = supabase.table("tareas").select("id").eq("codigo_tarea", codigo_generado).execute()
                    if not existe_codigo.data:
                        break
                nueva["codigo_tarea"] = codigo_generado
                result = supabase.table("tareas").insert(nueva).execute()
                tarea_creada = result.data[0]
            else:
                raise e

        # Si es recurrente
        if str(datos.get("is_recurrente", "")).lower() in ("1", "true", "on", "yes"):
            datos_recurrente = {
                "id": str(uuid.uuid4()),
                "tarea_id": tarea_creada["id"],
                "dtstart": f"{datos.get('dtstart')}T00:00:00" if datos.get('dtstart') else None,
                "rrule": datos.get("rrule"),
                "until": f"{datos.get('until')}T23:59:59" if datos.get('until') else None,
                "count": int(datos.get("count")) if datos.get("count") else None,
                "active": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            supabase.table("tareas_recurrentes").insert(datos_recurrente).execute()

        return jsonify({"ok": True, "id": tarea_creada["id"], "tarea": tarea_creada})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

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
    if not datos:
        return jsonify({"ok": False, "error": "No se recibió payload válido"})

    # Si viene 'campo' y 'valor', modo antiguo (compatibilidad)
    if "campo" in datos and "valor" in datos:
        campo = datos["campo"]
        valor = datos["valor"]
        if campo == "tarea_padre_id" and (valor is None or valor == ""):
            valor = None
        try:
            supabase.table("tareas").update({campo: valor}).eq("id", tarea_id).execute()
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)})

    # Modo nuevo: actualizar varios campos a la vez
    try:
        datos["updated_at"] = datetime.now().isoformat()
        if datos.get("empresa_id") == "":
            datos.pop("empresa_id")
        supabase.table("tareas").update(datos).eq("id", tarea_id).execute()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

# ✅ Ruta DELETE para eliminar tarea
@panel_tareas_crud_bp.route("/tareas/gestionar/eliminar/<tarea_id>", methods=["DELETE"])
def eliminar_tarea(tarea_id):
    try:
        # Soft delete: marcar como inactiva la tarea y sus subtareas
        supabase.table("subtareas").update({"activo": False, "updated_at": datetime.utcnow().isoformat()}).eq("tarea_padre_id", tarea_id).execute()
        supabase.table("tareas").update({"activo": False, "updated_at": datetime.utcnow().isoformat()}).eq("id", tarea_id).execute()
        # (Opcional) también puedes marcar como inactivos los comentarios y recurrencias si tu modelo lo soporta
        # supabase.table("tarea_comentarios").update({"activo": False, "updated_at": datetime.utcnow().isoformat()}).eq("tarea_id", tarea_id).execute()
        # supabase.table("tareas_recurrentes").update({"activo": False, "updated_at": datetime.utcnow().isoformat()}).eq("tarea_id", tarea_id).execute()
        usuario_empresa_id = request.args.get("usuario_empresa_id")
        page = request.args.get("page", 1)
        page_size = request.args.get("page_size", 20)
        if usuario_empresa_id:
            result = listar_tareas_paginado(usuario_empresa_id, page, page_size)
            return jsonify({"ok": True, "tareas": result["tareas"], "total": result["total"], "page": result["page"], "page_size": result["page_size"]})
        else:
            return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

@panel_cliente_tareas_bp.route("/<nombre_nora>/tareas/<tarea_id>/comentarios", methods=["GET"])
def obtener_comentarios_tarea(nombre_nora, tarea_id):
    res = supabase.table("tarea_comentarios").select("*", count="exact").eq("tarea_id", tarea_id).order("created_at", desc=False).execute()
    return jsonify(res.data or [])

@panel_cliente_tareas_bp.route("/<nombre_nora>/tareas/<tarea_id>/comentarios", methods=["POST"])
def agregar_comentario_tarea(nombre_nora, tarea_id):
    user = session.get("user")
    if not user:
        return jsonify({"ok": False, "error": "No autenticado"}), 401
    data = request.get_json() or {}
    texto = (data.get("texto") or "").strip()
    if not texto:
        return jsonify({"ok": False, "error": "Comentario vacío"}), 400
    comentario = {
        "id": str(uuid.uuid4()),
        "tarea_id": tarea_id,
        "usuario_id": user.get("id"),
        "usuario_nombre": user.get("nombre", "Usuario"),
        "texto": texto,
        "created_at": datetime.utcnow().isoformat()
    }
    try:
        supabase.table("tarea_comentarios").insert(comentario).execute()
        return jsonify({"ok": True, "comentario": comentario})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

@panel_tareas_crud_bp.route("/tareas/gestionar/listar", methods=["GET"])
def listar_tareas_gestionar():
    usuario_empresa_id = request.args.get("usuario_empresa_id")
    page = request.args.get("page", 1)
    page_size = request.args.get("page_size", 20)
    if not usuario_empresa_id:
        return jsonify({"error": "usuario_empresa_id es obligatorio"}), 400
    result = listar_tareas_paginado(usuario_empresa_id, page, page_size)
    return jsonify(result)