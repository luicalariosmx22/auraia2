from flask import Blueprint, request, session, jsonify, redirect, render_template
from datetime import datetime
import uuid
from clientes.aura.utils.supabase_client import supabase

panel_tareas_recurrentes_bp = Blueprint("panel_tareas_recurrentes_bp", __name__, template_folder="../../../templates/panel_cliente_tareas/recurrentes")

@panel_tareas_recurrentes_bp.route(
    "/panel_cliente/<nombre_nora>/tareas/recurrentes/crear", methods=["POST"]
)
def crear_tarea_recurrente(nombre_nora):
    if not session.get("email"):
        return redirect("/login")

    usuario_id = session.get("usuario_empresa_id")
    if not usuario_id:
        return jsonify({"error": "Usuario no identificado"}), 403

    payload = request.get_json(silent=True) or {}
    tarea_id = payload.get("tarea_id")
    dtstart  = payload.get("dtstart")
    rrule    = payload.get("rrule")
    until    = payload.get("until")
    count    = payload.get("count")

    # Validar campos obligatorios
    if not tarea_id or not dtstart or not rrule:
        return jsonify({"error": "tarea_id, dtstart y rrule son obligatorios"}), 400

    # Verificar que la tarea original exista
    orig = (
        supabase.table("tareas")
        .select("id")
        .eq("id", tarea_id)
        .limit(1)
        .execute()
    )
    if not orig.data:
        return jsonify({"error": "Tarea original no encontrada"}), 400

    recurrente = {
        "id":           str(uuid.uuid4()),
        "tarea_id":     tarea_id,
        "dtstart":      dtstart,
        "rrule":        rrule,
        "until":        until or None,
        "count":        count or None,
        "active":       True,
        "created_at":   datetime.utcnow().isoformat(),
        "updated_at":   datetime.utcnow().isoformat(),
    }

    try:
        supabase.table("tareas_recurrentes").insert(recurrente).execute()
        # TODO: Registrar job en APScheduler según rrule y dtstart
        return jsonify({"ok": True, "recurrente": recurrente})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@panel_tareas_recurrentes_bp.route("/panel_cliente/<nombre_nora>/tareas/recurrentes", methods=["GET"])
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

@panel_tareas_recurrentes_bp.route("/panel_cliente/<nombre_nora>/tareas/recurrentes/actualizar/<rec_id>", methods=["POST"])
def actualizar_estado_recurrente(nombre_nora, rec_id):
    nuevo_estado = request.form.get("active") == "true"
    try:
        supabase.table("tareas_recurrentes").update({"active": nuevo_estado}).eq("id", rec_id).execute()
        return redirect(f"/panel_cliente/{nombre_nora}/tareas/recurrentes")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@panel_tareas_recurrentes_bp.route("/panel_cliente/<nombre_nora>/tareas/recurrentes/eliminar/<rec_id>", methods=["POST"])
def eliminar_recurrente(nombre_nora, rec_id):
    try:
        supabase.table("tareas_recurrentes").delete().eq("id", rec_id).execute()
        return redirect(f"/panel_cliente/{nombre_nora}/tareas/recurrentes")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
