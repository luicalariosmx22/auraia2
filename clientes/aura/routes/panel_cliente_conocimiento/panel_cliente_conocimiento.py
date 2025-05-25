# ✅ Archivo: clientes/aura/routes/panel_cliente_conocimiento/panel_cliente_conocimiento.py
# 👉 Define el blueprint y conecta rutas con handlers

from flask import Blueprint, request, jsonify, render_template
from clientes.aura.utils.login_required import login_required
from clientes.aura.utils.vinculo_servicios import vincular_bloque_a_servicio
from .handlers import (
    handle_listar_bloques,
    handle_crear_bloque,
    handle_editar_bloque,
    handle_eliminar_bloque,
    handle_listar_por_etiqueta,
    handle_listar_tipo_menu,
    handle_conocimiento_por_servicio,
)
from .storage import handle_subir_pdf

panel_cliente_conocimiento_bp = Blueprint("panel_cliente_conocimiento", __name__)

@panel_cliente_conocimiento_bp.route("/bloques", methods=["GET"])
@login_required
def listar_bloques():
    nombre_nora = request.path.split("/")[2]
    return handle_listar_bloques(nombre_nora)

@panel_cliente_conocimiento_bp.route("/crear", methods=["POST"])
@login_required
def crear_bloque_manual():
    nombre_nora = request.path.split("/")[2]
    data = request.get_json()

    if not data:
        return jsonify({"error": "Datos vacíos o mal formateados"}), 400

    respuesta = handle_crear_bloque(nombre_nora, data)

    if respuesta[1] == 201:
        bloque_id = respuesta[0].json[0]["id"]
        etiquetas = data.get("etiquetas", [])
        vincular_bloque_a_servicio(nombre_nora, bloque_id, etiquetas)

    return respuesta

@panel_cliente_conocimiento_bp.route("/editar/<bloque_id>", methods=["POST"])
@login_required
def editar_bloque(bloque_id):
    nombre_nora = request.path.split("/")[2]
    data = request.json
    respuesta = handle_editar_bloque(bloque_id, data)

    if respuesta[1] == 200:
        etiquetas = data.get("etiquetas", [])
        vincular_bloque_a_servicio(nombre_nora, bloque_id, etiquetas)

    return respuesta

@panel_cliente_conocimiento_bp.route("/eliminar/<bloque_id>", methods=["POST"])
@login_required
def eliminar_bloque(bloque_id):
    return handle_eliminar_bloque(bloque_id)

@panel_cliente_conocimiento_bp.route("/etiqueta/<etiqueta>", methods=["GET"])
@login_required
def listar_bloques_por_etiqueta(etiqueta):
    nombre_nora = request.path.split("/")[2]
    return handle_listar_por_etiqueta(nombre_nora, etiqueta)

@panel_cliente_conocimiento_bp.route("/menu", methods=["GET"])
@login_required
def listar_bloques_tipo_menu():
    nombre_nora = request.path.split("/")[2]
    return handle_listar_tipo_menu(nombre_nora)

@panel_cliente_conocimiento_bp.route("/subir_pdf", methods=["POST"])
@login_required
def subir_archivo_pdf():
    nombre_nora = request.path.split("/")[2]
    return handle_subir_pdf(nombre_nora, request.files.get("archivo"))

@panel_cliente_conocimiento_bp.route("/servicio/<servicio_id>/conocimiento", methods=["GET"])
@login_required
def conocimiento_por_servicio(servicio_id):
    nombre_nora = request.path.split("/")[2]
    return handle_conocimiento_por_servicio(nombre_nora, servicio_id)

@panel_cliente_conocimiento_bp.route("/", methods=["GET"])
@login_required
def index_conocimiento():
    nombre_nora = request.path.split("/")[2]

    # Obtener todos los bloques planos
    response, status = handle_listar_bloques(nombre_nora)
    bloques = response.get_json()

    # Agrupar por etiqueta
    bloques_por_etiqueta = {}
    etiquetas_unicas = set()

    for bloque in bloques:
        for etiqueta in bloque.get("etiquetas", []):
            etiquetas_unicas.add(etiqueta)
            if etiqueta not in bloques_por_etiqueta:
                bloques_por_etiqueta[etiqueta] = []
            bloques_por_etiqueta[etiqueta].append(bloque)

    return render_template(
        "panel_cliente_conocimiento/index.html",
        nombre_nora=nombre_nora,
        bloques_por_etiqueta=bloques_por_etiqueta,
        etiquetas=sorted(etiquetas_unicas)
    )
