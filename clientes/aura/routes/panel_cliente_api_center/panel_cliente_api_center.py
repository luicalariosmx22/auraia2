
from flask import Blueprint, render_template, request, redirect, url_for, flash
from clientes.aura.utils.supabase_client import supabase
import uuid
import json

panel_cliente_api_center_bp = Blueprint(
    "panel_cliente_api_center_bp",
    __name__,
    url_prefix="/panel_cliente/<nombre_nora>/api_center"
)

@panel_cliente_api_center_bp.route("/editar/<uuid:api_id>")
def mostrar_edicion(api_id):
    nombre_nora = request.view_args.get("nombre_nora")
    api = supabase.table("apis_registradas").select("*").eq("id", str(api_id)).single().execute().data
    return render_template("panel_cliente_api_center/editar.html", api=api, nombre_nora=nombre_nora)

@panel_cliente_api_center_bp.route("/eliminar/<uuid:api_id>")
def confirmar_eliminar(api_id):
    nombre_nora = request.view_args.get("nombre_nora")
    supabase.table("apis_registradas").delete().eq("id", str(api_id)).execute()
    flash("API eliminada correctamente", "success")
    return redirect(url_for("panel_cliente_api_center_bp.vista_api_center", nombre_nora=nombre_nora))

@panel_cliente_api_center_bp.route("/", methods=["GET"])
def vista_api_center():
    nombre_nora = request.view_args.get("nombre_nora")
    respuesta = supabase.table("apis_registradas").select("*").execute()
    apis = respuesta.data if respuesta.data else []
    return render_template("panel_cliente_api_center/index.html", nombre_nora=nombre_nora, apis=apis)

@panel_cliente_api_center_bp.route("/crear", methods=["POST"])
def crear_api():
    data = request.form
    nombre = data.get("nombre")
    descripcion = data.get("descripcion")
    url_base = data.get("url_base")
    clave_api = data.get("clave_api")
    documentacion = data.get("documentacion")
    nombre_nora = request.view_args.get("nombre_nora")

    if not nombre or not url_base:
        flash("Nombre y URL base son obligatorios", "error")
        return redirect(url_for("panel_cliente_api_center_bp.vista_api_center", nombre_nora=nombre_nora))

    try:
        docu_json = json.loads(documentacion) if documentacion else None
    except Exception:
        docu_json = documentacion or None

    supabase.table("apis_registradas").insert({
        "id": str(uuid.uuid4()),
        "nombre": nombre,
        "descripcion": descripcion,
        "url_base": url_base,
        "clave_api": clave_api,
        "documentacion": docu_json,
        "nora": nombre_nora,
        "activa": True
    }).execute()

    flash("API registrada correctamente", "success")
    return redirect(url_for("panel_cliente_api_center_bp.vista_api_center", nombre_nora=nombre_nora))

@panel_cliente_api_center_bp.route("/editar/<uuid:api_id>", methods=["POST"])
def editar_api(api_id):
    data = request.form
    cambios = {
        "nombre": data.get("nombre"),
        "descripcion": data.get("descripcion"),
        "url_base": data.get("url_base"),
        "clave_api": data.get("clave_api"),
        "documentacion": None
    }
    docu = data.get("documentacion")
    if docu:
        try:
            cambios["documentacion"] = json.loads(docu)
        except Exception:
            cambios["documentacion"] = docu
    else:
        cambios.pop("documentacion")

    cambios = {k: v for k, v in cambios.items() if v is not None}
    supabase.table("apis_registradas").update(cambios).eq("id", str(api_id)).execute()
    flash("API actualizada correctamente", "success")

    nombre_nora = request.view_args.get("nombre_nora")
    return redirect(url_for("panel_cliente_api_center_bp.vista_api_center", nombre_nora=nombre_nora))

@panel_cliente_api_center_bp.route("/eliminar/<uuid:api_id>", methods=["POST"])
def eliminar_api(api_id):
    supabase.table("apis_registradas").delete().eq("id", str(api_id)).execute()
    flash("API eliminada correctamente", "success")

    nombre_nora = request.view_args.get("nombre_nora")
    return redirect(url_for("panel_cliente_api_center_bp.vista_api_center", nombre_nora=nombre_nora))
