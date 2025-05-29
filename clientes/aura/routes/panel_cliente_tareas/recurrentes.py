from flask import Blueprint, request, jsonify, session, redirect
from datetime import datetime
import uuid
from clientes.aura.utils.supabase_client import supabase

panel_tareas_recurrentes_bp = Blueprint(
    "panel_tareas_recurrentes_bp",
    __name__,
    url_prefix="/panel_cliente/<nombre_nora>/tareas/recurrentes"
)

@panel_tareas_recurrentes_bp.route("/crear", methods=["POST"])
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

@panel_tareas_recurrentes_bp.route("", methods=["GET"])
def vista_recurrentes(nombre_nora):
    if not session.get("email"):
        return redirect("/login")

    user = session.get("user", {})
    usuario_id = user.get("id", session.get("usuario_empresa_id"))

    # Obtener tareas recurrentes activas
    resp = supabase.table("tareas_recurrentes") \
        .select("*") \
        .eq("active", True) \
        .execute()

    recurrentes = resp.data or []

    # Obtener títulos de tareas base
    tareas_ids = list(set([r["tarea_id"] for r in recurrentes if r.get("tarea_id")]))
    tareas = {}
    if tareas_ids:
        tarea_resp = supabase.table("tareas").select("id, titulo").in_("id", tareas_ids).execute()
        for t in tarea_resp.data or []:
            tareas[t["id"]] = t["titulo"]

    for r in recurrentes:
        r["titulo_base"] = tareas.get(r["tarea_id"], "—")

    return render_template("panel_cliente_tareas/recurrentes/index.html",
        nombre_nora=nombre_nora,
        recurrentes=recurrentes,
        user=user
    )

from flask import request, jsonify

@panel_tareas_recurrentes_bp.route("/actualizar/<rec_id>", methods=["POST"])
def actualizar_estado_recurrente(nombre_nora, rec_id):
    nuevo_estado = request.form.get("active") == "true"
    try:
        supabase.table("tareas_recurrentes").update({"active": nuevo_estado}).eq("id", rec_id).execute()
        return redirect(f"/panel_cliente/{nombre_nora}/tareas/recurrentes")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@panel_tareas_recurrentes_bp.route("/eliminar/<rec_id>", methods=["POST"])
def eliminar_recurrente(nombre_nora, rec_id):
    try:
        supabase.table("tareas_recurrentes").delete().eq("id", rec_id).execute()
        return redirect(f"/panel_cliente/{nombre_nora}/tareas/recurrentes")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
