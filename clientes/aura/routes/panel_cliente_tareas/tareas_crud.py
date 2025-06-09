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

    # --- ANTI-DUPLICADO: Verifica si ya existe una tarea igual para hoy ---
    hoy = datetime.now().strftime("%Y-%m-%d")
    existe = supabase.table("tareas").select("id").eq("usuario_empresa_id", usuario_empresa_id) \
        .eq("titulo", titulo).gte("created_at", f"{hoy}T00:00:00").lte("created_at", f"{hoy}T23:59:59").execute()
    if existe.data:
        print("⚠️ Ya existe una tarea igual hoy, no se inserta duplicado.")
        return existe.data, 200

    try:
        # 1️⃣ Insertamos la tarea base
        result = supabase.table("tareas").insert(nueva).execute()
        print(f"🟢 Resultado insert tarea base: {result}")
        # ────────────────────────────────────────────────────────────────
        # 📌 AQUÍ se inserta la recurrencia cuando se crea la tarea
        #    (bloque 2️⃣).  Si el checkbox «is_recurrente» viene activo
        #    se arma `rec_payload` y se hace:
        #        supabase.table("tareas_recurrentes").insert(rec_payload)
        # ────────────────────────────────────────────────────────────────
        es_recurrente = str(data.get("is_recurrente", "")).lower() in ("1", "true", "on", "yes")
        print(f"🔎 ¿Es recurrente? {es_recurrente}")
        if es_recurrente:
            dtstart_val = data.get("dtstart")           # YYYY-MM-DD
            rrule_val   = data.get("rrule") or ""       # Ej. "FREQ=DAILY"
            until_val   = data.get("until") or None     # YYYY-MM-DD (opcional)
            count_val   = data.get("count") or None     # entero (opcional)
            print(f"🔎 Datos recurrencia: dtstart={dtstart_val}, rrule={rrule_val}, until={until_val}, count={count_val}")
            if dtstart_val and rrule_val:
                rec_payload = {
                    "id":        str(uuid.uuid4()),
                    "tarea_id":  nueva["id"],
                    "dtstart":   f"{dtstart_val}T00:00:00",
                    "rrule":     rrule_val,
                    "until":     f"{until_val}T23:59:59" if until_val else None,
                    "count":     int(count_val) if count_val else None,
                    "active":    True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }
                print("🟠 Intentando insertar en tareas_recurrentes:", rec_payload)
                try:
                    rec_result = supabase.table("tareas_recurrentes").insert(rec_payload).execute()
                    print("🟢 Resultado insert tareas_recurrentes:", rec_result)
                    if hasattr(rec_result, 'data'):
                        print(f"🟢 Data insertada en tareas_recurrentes: {rec_result.data}")
                    if getattr(rec_result, 'error', None):
                        print("🔴 Error devuelto por Supabase:", rec_result.error)
                except Exception as e:
                    print("⚠️ Error insertando tareas_recurrentes:", e)

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

    # Lógica especial para mover entre tareas y subtareas
    if campo == "tarea_padre_id":
        from datetime import datetime
        print(f"[DEBUG] Actualizando tarea_padre_id para id={tarea_id}, valor={valor}")
        tarea = supabase.table("tareas").select("*").eq("id", tarea_id).single().execute().data
        subtarea = supabase.table("subtareas").select("*").eq("id", tarea_id).single().execute().data
        print(f"[DEBUG] ¿Existe en tareas? {bool(tarea)} | ¿Existe en subtareas? {bool(subtarea)}")
        if tarea:
            print(f"[DEBUG] Datos tarea: {tarea}")
            if valor not in (None, "", "null"):  # Asignar tarea padre
                subtarea_data = dict(tarea)
                subtarea_data["id"] = tarea_id
                subtarea_data["tarea_padre_id"] = valor
                subtarea_data["created_at"] = datetime.utcnow().isoformat()
                subtarea_data["updated_at"] = datetime.utcnow().isoformat()
                subtarea_data.pop("codigo_tarea", None)
                print(f"[DEBUG] Insertando en subtareas: {subtarea_data}")
                # Primero elimina de subtareas si existe (por seguridad de duplicados)
                supabase.table("subtareas").delete().eq("id", tarea_id).execute()
                # Luego inserta en subtareas
                supabase.table("subtareas").insert(subtarea_data).execute()
                # Finalmente elimina de tareas
                supabase.table("tareas").delete().eq("id", tarea_id).execute()
                print(f"[DEBUG] Movido a subtareas y eliminado de tareas")
                return jsonify({"ok": True, "movido": "a_subtareas"})
        elif subtarea:
            print(f"[DEBUG] Datos subtarea: {subtarea}")
            if valor in (None, "", "null"):
                tarea_data = dict(subtarea)
                tarea_data["id"] = tarea_id
                tarea_data["tarea_padre_id"] = None
                tarea_data["created_at"] = datetime.utcnow().isoformat()
                tarea_data["updated_at"] = datetime.utcnow().isoformat()
                tarea_data["codigo_tarea"] = generar_codigo_tarea("NN")
                print(f"[DEBUG] Insertando en tareas: {tarea_data}")
                supabase.table("tareas").insert(tarea_data).execute()
                supabase.table("subtareas").delete().eq("id", tarea_id).execute()
                print(f"[DEBUG] Movido a tareas y eliminado de subtareas")
                return jsonify({"ok": True, "movido": "a_tareas"})
            else:
                print(f"[DEBUG] Actualizando tarea_padre_id en subtareas a {valor}")
                supabase.table("subtareas").update({"tarea_padre_id": valor, "updated_at": datetime.utcnow().isoformat()}).eq("id", tarea_id).execute()
                return jsonify({"ok": True, "actualizado": "subtarea"})
        print(f"[DEBUG] No se encontró la tarea ni en tareas ni en subtareas para id={tarea_id}")
        # Si no es un movimiento especial, solo actualizar el campo en tareas
        if campo == "tarea_padre_id" and (valor is None or valor == ""):
            valor = None
        try:
            supabase.table("tareas").update({campo: valor}).eq("id", tarea_id).execute()
            print(f"[DEBUG] Solo se actualizó el campo en tareas")
            return jsonify({"ok": True})
        except Exception as e:
            print(f"[DEBUG] Error al actualizar campo en tareas: {e}")
            return jsonify({"ok": False, "error": str(e)})

    # Lógica normal para otros campos
    try:
        supabase.table("tareas").update({campo: valor}).eq("id", tarea_id).execute()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

# ✅ Ruta DELETE para eliminar tarea
@panel_tareas_crud_bp.route("/tareas/gestionar/eliminar/<tarea_id>", methods=["DELETE"])
def eliminar_tarea(tarea_id):
    try:
        # Borra primero los registros relacionados para acelerar el borrado
        supabase.table("subtareas").delete().eq("tarea_padre_id", tarea_id).execute()
        supabase.table("tarea_comentarios").delete().eq("tarea_id", tarea_id).execute()
        supabase.table("tareas_recurrentes").delete().eq("tarea_id", tarea_id).execute()
        # Ahora sí borra la tarea principal
        supabase.table("tareas").delete().eq("id", tarea_id).execute()
        # --- OPTIMIZACIÓN: devolver la página actual de tareas paginadas ---
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