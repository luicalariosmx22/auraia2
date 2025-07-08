from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from clientes.aura.utils.supabase_client import supabase
from clientes.aura.utils.login_required import login_required
import uuid
from datetime import datetime

panel_cliente_etiquetas_conocimiento_bp = Blueprint("panel_cliente_etiquetas_conocimiento", __name__)

@panel_cliente_etiquetas_conocimiento_bp.route("/", methods=["GET"])
@login_required
def index_etiquetas():
    nombre_nora = request.path.split("/")[2]
    etiquetas_res = supabase.table("etiquetas_nora") \
        .select("*") \
        .eq("nombre_nora", nombre_nora) \
        .eq("modulo", "conocimiento") \
        .order("creado_en", desc=True) \
        .execute()

    etiquetas = etiquetas_res.data or []

    return render_template("panel_cliente_etiquetas_conocimiento.html", nombre_nora=nombre_nora, etiquetas=etiquetas)

@panel_cliente_etiquetas_conocimiento_bp.route("/crear", methods=["POST"])
@login_required
def crear_etiqueta():
    nombre_nora = request.path.split("/")[2]
    etiqueta = request.form.get("etiqueta", "").strip()

    if not etiqueta:
        return redirect(url_for("panel_cliente_etiquetas_conocimiento.index_etiquetas", nombre_nora=nombre_nora))

    nueva = {
        "id": str(uuid.uuid4()),
        "nombre_nora": nombre_nora,
        "etiqueta": etiqueta,
        "modulo": "conocimiento",
        "creado_en": datetime.utcnow().isoformat()
    }

    supabase.table("etiquetas_nora").insert(nueva).execute()

    return redirect(url_for("panel_cliente_etiquetas_conocimiento.index_etiquetas", nombre_nora=nombre_nora))

@panel_cliente_etiquetas_conocimiento_bp.route("/eliminar/<etiqueta_id>", methods=["POST"])
@login_required
def eliminar_etiqueta(etiqueta_id):
    nombre_nora = request.path.split("/")[2]
    supabase.table("etiquetas_nora").delete().eq("id", etiqueta_id).execute()

    return redirect(url_for("panel_cliente_etiquetas_conocimiento.index_etiquetas", nombre_nora=nombre_nora))

@panel_cliente_etiquetas_conocimiento_bp.route("/json", methods=["GET"])
@login_required
def etiquetas_json():
    nombre_nora = request.path.split("/")[2]

    try:
        res = supabase.table("etiquetas_nora") \
            .select("etiqueta") \
            .eq("nombre_nora", nombre_nora) \
            .eq("modulo", "conocimiento") \
            .execute()

        etiquetas = [item["etiqueta"] for item in res.data or []]
        return jsonify(etiquetas)

    except Exception as e:
        print(f"❌ Error obteniendo etiquetas JSON: {e}")
        return jsonify([])
