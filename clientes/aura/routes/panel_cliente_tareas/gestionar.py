from datetime import datetime
import uuid
import logging

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    jsonify,
)

from utils.validar_modulo_activo import modulo_activo_para_nora
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.generar_codigo_tarea import generar_codigo_tarea

panel_tareas_gestionar_bp = Blueprint("panel_tareas_gestionar_bp", __name__)

# -------------------------------------------------------------------
# VISTA PRINCIPAL: listado de tareas (gestión)
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar")
def vista_gestionar_tareas(nombre_nora):
    if not session.get("email"):
        return redirect("/login")

    if not modulo_activo_para_nora(nombre_nora, "tareas"):
        return "Módulo no activo", 403

    # --- Determinar tipo de usuario ---
    tipo = "usuario_cliente"
    if session.get("is_admin"):
        if session.get("nombre_nora") == "admin":
            tipo = "admin_global"
        else:
            tipo = "cliente_admin"
    print("🟢 Tipo de usuario:", tipo)
    print("🟢 Correo:", session.get("email"))
    print("🟢 Nombre:", session.get("name"))

    # -----------------------------------------------------------------
    # Permisos del usuario actual
    # -----------------------------------------------------------------
    usuario_id = session.get("usuario_empresa_id")
    # Permisos por defecto
    permisos = {
        "ver_todas_tareas": False,
        "reasignar_tareas": False,
        "es_supervisor": False,
    }
    if usuario_id:
        try:
            resp = (
                supabase.table("usuarios_clientes")
                .select(
                    "ver_todas_tareas, reasignar_tareas, "
                    "es_supervisor, es_supervisor_tareas"
                )
                .eq("id", usuario_id)
                .limit(1)  # evita PGRST116 cuando no hay filas
                .execute()
            )
            if resp.data:
                fila = resp.data[0]
                permisos.update(
                    {
                        "ver_todas_tareas": fila.get("ver_todas_tareas", False),
                        "reasignar_tareas": fila.get("reasignar_tareas", False),
                        "es_supervisor": fila.get("es_supervisor", False)
                        or fila.get("es_supervisor_tareas", False),
                    }
                )
        except Exception:
            # Si falla la consulta, conservamos los permisos mínimos
            pass

    # -----------------------------------------------------------------
    # 🔓 Asegurar visibilidad total para administradores globales
    # -----------------------------------------------------------------
    if session.get("is_admin"):
        permisos["ver_todas_tareas"] = True
        permisos["es_supervisor"] = True

    # -----------------------------------------------------------------
    # Traemos todas las tareas activas de la Nora
    # -----------------------------------------------------------------
    tareas_resp = (
        supabase.table("tareas")
        .select("*")
        .eq("nombre_nora", nombre_nora)
        .eq("activo", True)
        .execute()
    )
    todas = tareas_resp.data or []

    # -----------------------------------------------------------------
    # Filtros recibidos por querystring
    # -----------------------------------------------------------------
    q_busqueda  = request.args.get("busqueda", "").strip().lower()
    q_estatus   = request.args.get("estatus", "").strip()
    q_prioridad = request.args.get("prioridad", "").strip()
    q_empresa   = request.args.get("empresa_id", "").strip()
    q_asignado  = request.args.get("usuario_empresa_id", "").strip()
    q_ini       = request.args.get("fecha_ini", "").strip()
    q_fin       = request.args.get("fecha_fin", "").strip()

    # -----------------------------------------------------------------
    # Filtrado base según permisos (propias / todas)
    # -----------------------------------------------------------------
    if permisos.get("ver_todas_tareas") or permisos.get("es_supervisor") or not usuario_id:
        tareas = todas
    else:
        tareas = [t for t in todas if t.get("usuario_empresa_id") == usuario_id]

    # -----------------------------------------------------------------
    # Filtros avanzados
    # -----------------------------------------------------------------
    def coincide(t):
        # ya no excluimos aquí; las tareas completadas se mostrarán en su bloque aparte
        if q_busqueda and q_busqueda not in (t.get("titulo","").lower() + " " + t.get("descripcion","").lower()):
            return False
        if q_estatus and t.get("estatus") != q_estatus:
            return False
        if q_prioridad and t.get("prioridad") != q_prioridad:
            return False
        if q_empresa and (t.get("empresa_id") or "") != q_empresa:
            return False
        if q_asignado and (t.get("usuario_empresa_id") or "") != q_asignado:
            return False
        if q_ini and (t.get("fecha_limite") or "") < q_ini:
            return False
        if q_fin and (t.get("fecha_limite") or "") > q_fin:
            return False
        return True

    tareas = [t for t in tareas if coincide(t)]

    # -------------------------------------------------------------
    # Cargar info de empresa y asignado para cada tarea
    # -------------------------------------------------------------
    for t in tareas:
        if t.get("empresa_id"):
            try:
                emp = (
                    supabase.table("cliente_empresas")
                    .select("nombre_empresa")
                    .eq("id", t["empresa_id"])
                    .limit(1)
                    .execute()
                )
                if emp.data:
                    t["empresa_nombre"] = emp.data[0]["nombre_empresa"]
            except Exception:
                t["empresa_nombre"] = ""

        # 💡 la tabla ya NO tiene asignado_a; usamos usuario_empresa_id
        if t.get("usuario_empresa_id"):
            try:
                usr = (
                    supabase.table("usuarios_clientes")
                    .select("nombre")
                    .eq("id", t["usuario_empresa_id"])
                    .limit(1)
                    .execute()
                )
                if usr.data:
                    t["asignado_nombre"] = usr.data[0]["nombre"]
            except Exception:
                t["asignado_nombre"] = ""

    # -------------------------------------------------------------
    # Listas auxiliares para dropdowns
    # -------------------------------------------------------------
    usuarios_resp = (
        supabase.table("usuarios_clientes")
        .select("id, nombre")
        .eq("nombre_nora", nombre_nora)
        .eq("activo", True)
        .execute()
    )
    usuarios = usuarios_resp.data or []

    empresas_resp = (
        supabase.table("cliente_empresas")
        .select("id, nombre_empresa")
        .eq("nombre_nora", nombre_nora)
        .execute()
    )
    empresas = empresas_resp.data or []

    # -------------------------------------------------------------
    # LOG de depuración
    # -------------------------------------------------------------
    logger = logging.getLogger(__name__)
    logger.info(
        f"[Tareas] Recuperadas {len(tareas)} tareas para usuario_id={usuario_id} "
        f"(Nora: {nombre_nora})"
    )
    # Para un detalle completo descomenta:
    # logger.debug("Detalles tareas: %s", tareas)

    # -----------------------------------------------------------------
    # Separar tareas por estatus para mostrar dos tablas
    # -----------------------------------------------------------------
    tareas_activas     = [t for t in tareas if t.get("estatus", "").strip() != "completada"]
    tareas_completadas = [t for t in tareas if t.get("estatus", "").strip() == "completada"]

    is_admin = session.get("is_admin", False)
    if is_admin:
        usuarios_disponibles = supabase.table("usuarios_clientes").select("id,nombre")\
            .eq("nombre_nora", nombre_nora).execute().data or []
    else:
        usuarios_disponibles = []

    return render_template(
        "panel_cliente_tareas/gestionar.html",
        nombre_nora=nombre_nora,
        tareas_activas=tareas_activas,
        tareas_completadas=tareas_completadas,
        permisos=permisos,
        usuarios=usuarios,
        empresas=empresas,
        user={"name": session.get("name", "Usuario"), "id": usuario_id},
        modulo_activo="tareas",
        is_admin=is_admin,
        usuarios_disponibles=usuarios_disponibles
    )

# -------------------------------------------------------------------
# API: actualizar campo (inline edit)
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route(
    "/panel_cliente/<nombre_nora>/tareas/gestionar/actualizar/<tarea_id>",
    methods=["POST"],
)
def actualizar_campo_tarea(nombre_nora, tarea_id):
    payload = request.get_json(silent=True) or {}
    campo = payload.get("campo")
    valor = payload.get("valor")

    if campo not in [
        "titulo",
        "prioridad",
        "fecha_limite",
        "estatus",
        "usuario_empresa_id",  # ← Único campo para “Asignado a”
        "empresa_id",
    ]:
        return jsonify({"error": "Campo no permitido"}), 400

    # Validaciones de valor
    if campo == "prioridad":
        valor = (valor or "").strip().lower()
        if valor not in ("alta", "media", "baja"):
            return jsonify({"error": "Prioridad inválida"}), 400
    if campo == "estatus" and valor not in [
        "pendiente",
        "en progreso",
        "retrasada",
        "completada",
    ]:
        return jsonify({"error": "Estatus inválido"}), 400

    try:
        supabase.table("tareas").update(
            {campo: valor, "updated_at": datetime.utcnow().isoformat()}
        ).eq("id", tarea_id).execute()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------------------------
# API: crear tarea nueva
# -------------------------------------------------------------------
@panel_tareas_gestionar_bp.route(
    "/panel_cliente/<nombre_nora>/tareas/gestionar/crear", methods=["POST"]
)
def crear_tarea(nombre_nora):
    if not session.get("email"):
        return redirect("/login")

    usuario_id = session.get("usuario_empresa_id")

    # ✅ Si es admin, permitir que actúe sin tener usuario_empresa_id propio
    if not usuario_id and not session.get("is_admin"):
        return jsonify({"error": "Usuario no identificado"}), 403

    # Cambia request.get_json(silent=True) or {} por request.form.to_dict()
    payload = request.form.to_dict()
    titulo = payload.get("titulo")
    prioridad = (payload.get("prioridad") or "media").strip().lower()
    fecha_limite = payload.get("fecha_limite")
    estatus = payload.get("estatus", "pendiente")
    # ─── Saneamos cadenas vacías para uuid de empresa ─────────────────
    raw_empresa = (payload.get("empresa_id") or "").strip()
    empresa_id = raw_empresa or None   # "" → None para permitir NULL
    # ─── Determinar si el usuario puede asignar a otros (admin o supervisor) ─
    resp_priv = supabase.table("usuarios_clientes") \
        .select("es_supervisor, es_supervisor_tareas") \
        .eq("id", usuario_id) \
        .limit(1) \
        .execute()
    fila_priv = resp_priv.data[0] if resp_priv.data else {}
    is_supervisor = session.get("is_admin") \
        or fila_priv.get("es_supervisor", False) \
        or fila_priv.get("es_supervisor_tareas", False)
    raw_usuario = (payload.get("usuario_empresa_id") or "").strip()
    if is_supervisor:
        # Admin/supervisor debe elegir un usuario asignado
        if not raw_usuario:
            return jsonify({"error": "Debe seleccionar un usuario asignado"}), 400
        usuario_empresa_id = raw_usuario
    else:
        # Usuario normal solo puede auto-asignarse
        usuario_empresa_id = usuario_id
    # ─── Validar que el usuario_empresa_id exista en usuarios_clientes ────
    usr_check = supabase.table("usuarios_clientes") \
        .select("id") \
        .eq("id", usuario_empresa_id) \
        .limit(1) \
        .execute()
    if not usr_check.data:
        return jsonify({"error": "Usuario asignado inválido"}), 400

    # -----------------------------------------------------------------
    # Prints de depuración de variables recibidas y calculadas
    # -----------------------------------------------------------------
    print("=== crear_tarea ===")
    print(f"payload: {payload}")
    print(f"titulo: {titulo}")
    print(f"prioridad: {prioridad}")
    print(f"fecha_limite: {fecha_limite}")
    print(f"estatus: {estatus}")
    print(f"raw_empresa: {raw_empresa}")
    print(f"empresa_id: {empresa_id}")
    print(f"raw_usuario: {raw_usuario}")
    print(f"usuario_empresa_id: {usuario_empresa_id}")
    print(f"usuario_id (sesión): {usuario_id}")
    print(f"is_admin: {session.get('is_admin')}")
    print(f"nombre_nora: {nombre_nora}")

    # -----------------------------------------------------------------
    # Validaciones
    # -----------------------------------------------------------------
    if not titulo:
        return jsonify({"error": "El título es obligatorio"}), 400
    if prioridad not in ("alta", "media", "baja"):
        return jsonify({"error": "Prioridad inválida"}), 400
    if estatus not in ("pendiente", "en progreso", "retrasada", "completada"):
        return jsonify({"error": "Estatus inválido"}), 400
    # empresa_id *puede* ser None → la FK admite NULL

    # -----------------------------------------------------------------
    # Crear tarea
    # -----------------------------------------------------------------
    # el nombre de sesión puede ser None → convertimos a cadena segura
    creado_por = payload.get("creado_por") if session.get("is_admin") else session.get("usuario_empresa_id")

    nombre_sesion = (session.get("nombre") or "").strip()
    iniciales_usuario = nombre_sesion.split(" ")[:2] if nombre_sesion else ["NN"]

    tarea_data = {
        "id": str(uuid.uuid4()),
        "nombre_nora": nombre_nora,
        "titulo": titulo,
        "prioridad": prioridad,
        "fecha_limite": fecha_limite,
        "estatus": estatus,
        "usuario_empresa_id": usuario_empresa_id,
        "creado_por": creado_por,
        "codigo_tarea": generar_codigo_tarea(iniciales_usuario),
    }
    if empresa_id:
        tarea_data["empresa_id"] = empresa_id

    try:
        supabase.table("tareas").insert(tarea_data).execute()
        return jsonify({"ok": True, "tarea": tarea_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500