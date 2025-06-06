from flask import Blueprint, request, jsonify, session, redirect, render_template
from datetime import datetime
import uuid
from clientes.aura.utils.supabase_client import supabase

panel_tareas_recurrentes_bp = Blueprint(
    "panel_tareas_recurrentes_bp",
    __name__,
    # Prefijo estático; las partes dinámicas van en cada @route
    url_prefix="/panel_cliente"
)

# ───────────────────────────────────────────────────────────────
# GET  /panel_cliente/<nombre_nora>/tareas/recurrentes
# Lista todas las reglas recurrentes asociadas a la Nora
# ───────────────────────────────────────────────────────────────
@panel_tareas_recurrentes_bp.route(
    "/<nombre_nora>/tareas/recurrentes/",
    methods=["GET"],
    endpoint="vista_recurrentes",
    strict_slashes=False,  # permite acceder con o sin barra final
)
def vista_recurrentes(nombre_nora):
    # Requiere usuario logueado
    if not session.get("email"):
        return redirect("/login")

    # Obtener todas las reglas recurrentes (sin join)
    res_raw = (
        supabase.table("tareas_recurrentes")
        .select("*")
        .order("dtstart")
        .execute()
    )
    res_data = res_raw if isinstance(res_raw, list) else (res_raw.data or [])
    tareas_recurrentes_ids = set(r["tarea_id"] for r in res_data)
    print(f"[DEBUG recurrentes] IDs de tareas recurrentes: {tareas_recurrentes_ids}")

    # Obtener todos los tarea_padre_id de subtareas
    subtareas_resp = supabase.table("subtareas").select("tarea_padre_id").execute()
    ids_tareas_con_subtareas = set(s["tarea_padre_id"] for s in (subtareas_resp.data or []) if s.get("tarea_padre_id"))

    # Obtener todas las tareas activas de la Nora (solo tareas principales)
    # NOTA: La tabla 'tareas' NO tiene columna tarea_padre_id, así que solo filtramos por activo y nombre_nora
    tareas_resp = supabase.table("tareas").select("id, titulo, nombre_nora, empresa_id, usuario_empresa_id").eq("nombre_nora", nombre_nora).eq("activo", True).execute()
    tareas = tareas_resp.data or []
    print(f"[DEBUG recurrentes] Tareas activas traídas de la BD: {[{'id': t['id'], 'titulo': t['titulo']} for t in tareas]}")
    for t in tareas:
        t["es_subtarea"] = False  # Las tareas principales nunca son subtareas
        t["ya_recurrente"] = t["id"] in tareas_recurrentes_ids
    tareas_dict = {t["id"]: t for t in tareas}

    # Obtener empresas y usuarios activos
    empresas_resp = supabase.table("cliente_empresas").select("id, nombre_empresa").eq("nombre_nora", nombre_nora).execute()
    empresas = {e["id"]: e["nombre_empresa"] for e in (empresas_resp.data or [])}
    usuarios_resp = supabase.table("usuarios_clientes").select("id, nombre").eq("nombre_nora", nombre_nora).eq("activo", True).execute()
    usuarios = {u["id"]: u["nombre"] for u in (usuarios_resp.data or [])}

    recurrentes = []
    for r in res_data:
        tarea_id = r.get("tarea_id")
        tarea = tareas_dict.get(tarea_id)
        if tarea:
            r["titulo_base"] = tarea.get("titulo", "—")
            r["empresa_id"] = tarea.get("empresa_id", "—")
            r["usuario_empresa_id"] = tarea.get("usuario_empresa_id", "—")
            r["empresa_nombre"] = empresas.get(tarea.get("empresa_id"), "—") if tarea.get("empresa_id") else "—"
            r["usuario_nombre"] = usuarios.get(tarea.get("usuario_empresa_id"), "—") if tarea.get("usuario_empresa_id") else "—"
        else:
            r["titulo_base"] = "—"
            r["empresa_id"] = "—"
            r["usuario_empresa_id"] = "—"
            r["empresa_nombre"] = "—"
            r["usuario_nombre"] = "—"
        recurrentes.append(r)

    # Print tareas principales activas NO recurrentes
    tareas_no_recurrentes = [t for t in tareas if not t["ya_recurrente"]]
    print(f"[DEBUG recurrentes] Tareas principales activas NO recurrentes: {[{'id': t['id'], 'titulo': t['titulo']} for t in tareas_no_recurrentes]}")

    print(f"[DEBUG recurrentes] recurrentes mostrados para {nombre_nora}: {recurrentes}")

    return render_template(
        "panel_cliente_tareas/recurrentes/index.html",
        nombre_nora=nombre_nora,
        recurrentes=recurrentes,
        user=session.get("user", {}),
        tareas=tareas,
    )

# ───────────────────────────────────────────────────────────────
@panel_tareas_recurrentes_bp.route(
    "/<nombre_nora>/tareas/recurrentes/crear",
    methods=["POST"],
)
def crear_recurrente(nombre_nora):
    if not session.get("email"):
        return redirect("/login")

    usuario_id = session.get("usuario_empresa_id")
    if not usuario_id:
        return jsonify({"error": "Usuario no identificado"}), 403

    form = request.form
    tarea_id   = form.get("tarea_id")
    dtstart    = form.get("dtstart")
    rrule_type = form.get("rrule_type")
    until      = form.get("until")      or None
    count      = form.get("count")      or None

    if not tarea_id:
        return jsonify({"error": "Debe indicar la tarea origen"}), 400
    if not dtstart or not rrule_type:
        return jsonify({"error": "Inicio y tipo de recurrencia obligatorios"}), 400

    # construir texto RRULE básico
    rrule = f"FREQ={rrule_type.upper()}"
    if count:
        rrule += f";COUNT={int(count)}"
    if until:
        rrule += f";UNTIL={until.replace('-', '')}T000000Z"

    nueva = {
        "id":       str(uuid.uuid4()),
        "tarea_id": tarea_id,
        "dtstart":  dtstart,
        "rrule":    rrule,
        "until":    until,
        "count":    int(count) if count else None,
        "active":   True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    try:
        supabase.table("tareas_recurrentes").insert(nueva).execute()
        return jsonify({"ok": True, "recurrente": nueva})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

from flask import request, jsonify

@panel_tareas_recurrentes_bp.route(
    "/<nombre_nora>/tareas/recurrentes/actualizar/<rec_id>",
    methods=["POST"],
)
def actualizar_estado_recurrente(nombre_nora, rec_id):
    nuevo_estado = request.form.get("active") == "true"
    try:
        supabase.table("tareas_recurrentes").update({"active": nuevo_estado}).eq("id", rec_id).execute()
        return redirect(f"/panel_cliente/{nombre_nora}/tareas/recurrentes")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@panel_tareas_recurrentes_bp.route(
    "/<nombre_nora>/tareas/recurrentes/eliminar/<rec_id>",
    methods=["POST"],
)
def eliminar_recurrente(nombre_nora, rec_id):
    try:
        supabase.table("tareas_recurrentes").delete().eq("id", rec_id).execute()
        return redirect(f"/panel_cliente/{nombre_nora}/tareas/recurrentes")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def crear_instancia_tarea_recurrente(tarea_base, fecha_instancia, id_instancia=None):
    """
    Crea una instancia de una tarea recurrente y replica sus subtareas.
    - tarea_base: dict con los datos de la tarea padre (recurrente)
    - fecha_instancia: fecha para la nueva instancia (str o datetime)
    - id_instancia: opcional, forzar un id específico
    """
    from copy import deepcopy
    if not tarea_base:
        return None
    nueva_id = id_instancia or str(uuid.uuid4())
    nueva_tarea = deepcopy(tarea_base)
    nueva_tarea["id"] = nueva_id
    nueva_tarea["fecha_limite"] = fecha_instancia if isinstance(fecha_instancia, str) else fecha_instancia.strftime("%Y-%m-%d")
    nueva_tarea["created_at"] = datetime.utcnow().isoformat()
    nueva_tarea["updated_at"] = datetime.utcnow().isoformat()
    nueva_tarea["origen"] = "recurrente"
    # Elimina campos que no deben copiarse
    nueva_tarea.pop("codigo_tarea", None)
    supabase.table("tareas").insert(nueva_tarea).execute()
    # Replicar subtareas
    subtareas = supabase.table("subtareas").select("*").eq("tarea_padre_id", tarea_base["id"]).execute().data or []
    for subt in subtareas:
        nueva_subt = deepcopy(subt)
        nueva_subt["id"] = str(uuid.uuid4())
        nueva_subt["tarea_padre_id"] = nueva_id
        nueva_subt["created_at"] = datetime.utcnow().isoformat()
        nueva_subt["updated_at"] = datetime.utcnow().isoformat()
        supabase.table("subtareas").insert(nueva_subt).execute()
    return nueva_id

@panel_tareas_recurrentes_bp.route(
    "/<nombre_nora>/tareas/recurrentes/instanciar",
    methods=["POST"],
)
def instanciar_recurrente(nombre_nora):
    data = request.get_json() or request.form
    tarea_id = data.get("tarea_id")
    fecha = data.get("fecha")  # formato 'YYYY-MM-DD'
    if not tarea_id or not fecha:
        return jsonify({"ok": False, "error": "Faltan datos"}), 400
    tarea_base = supabase.table("tareas").select("*").eq("id", tarea_id).single().execute().data
    if not tarea_base:
        return jsonify({"ok": False, "error": "Tarea no encontrada"}), 404
    nueva_id = crear_instancia_tarea_recurrente(tarea_base, fecha)
    return jsonify({"ok": True, "nueva_tarea_id": nueva_id})
