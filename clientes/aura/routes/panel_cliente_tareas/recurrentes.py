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
    res_error = None if isinstance(res_raw, list) else getattr(res_raw, "error", None)

    # Obtener todas las tareas activas de la Nora
    tareas_resp = supabase.table("tareas").select("id, titulo, nombre_nora, empresa_id, usuario_empresa_id").eq("nombre_nora", nombre_nora).eq("activo", True).execute()
    tareas = tareas_resp.data or []
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

    print(f"[DEBUG recurrentes] recurrentes mostrados para {nombre_nora}: {recurrentes}")

    return render_template(
        "panel_cliente_tareas/recurrentes/index.html",
        nombre_nora=nombre_nora,
        recurrentes=recurrentes,
        user=session.get("user", {}),
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
