from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from clientes.aura.utils.login_required import login_required
from clientes.aura.utils.supabase_client import supabase
from datetime import datetime
import uuid

panel_cliente_menus_conocimiento_bp = Blueprint("panel_cliente_menus_conocimiento", __name__)

@panel_cliente_menus_conocimiento_bp.route("/", methods=["GET"])
@login_required
def index_menus(nombre_nora):
    try:
        res = supabase.table("menus_conocimiento").select("*")\
            .eq("nombre_nora", nombre_nora).order("creado_en", desc=True).execute()
        menus = res.data or []

        # Agrupar por etiquetas para visual
        menus_por_etiqueta = {}
        for menu in menus:
            for etiqueta in menu.get("etiquetas", []):
                menus_por_etiqueta.setdefault(etiqueta, []).append(menu)

        # Leer todas las etiquetas disponibles
        etiquetas_res = supabase.table("etiquetas_conocimiento").select("nombre")\
            .eq("nombre_nora", nombre_nora).eq("activa", True).execute()
        etiquetas = [et["nombre"] for et in etiquetas_res.data] if etiquetas_res.data else []

        return render_template("panel_cliente_conocimiento/menus.html", nombre_nora=nombre_nora,
                               menus_por_etiqueta=menus_por_etiqueta,
                               etiquetas_disponibles=etiquetas)
    except Exception as e:
        print(f"❌ Error cargando menús: {e}")
        flash("Error cargando los menús", "error")
        return redirect(url_for("panel_cliente_conocimiento.index_conocimiento", nombre_nora=nombre_nora))

@panel_cliente_menus_conocimiento_bp.route("/crear", methods=["POST"])
@login_required
def crear_menu(nombre_nora):
    try:
        data = request.get_json()
        contenido = data.get("contenido", "").strip()
        opciones = data.get("opciones", [])
        etiquetas = data.get("etiquetas", [])
        prioridad = data.get("prioridad", False)

        if not contenido or not opciones:
            return jsonify({"error": "Contenido y al menos una opción son obligatorios"}), 400

        insert_data = {
            "id": str(uuid.uuid4()),
            "nombre_nora": nombre_nora,
            "contenido": contenido,
            "opciones": opciones,
            "etiquetas": etiquetas,
            "prioridad": prioridad,
            "activo": True,
            "creado_en": datetime.utcnow().isoformat()
        }
        supabase.table("menus_conocimiento").insert(insert_data).execute()
        return jsonify({"success": True}), 201

    except Exception as e:
        print(f"❌ Error al crear menú: {e}")
        return jsonify({"error": "Error al guardar el menú"}), 500

@panel_cliente_menus_conocimiento_bp.route("/editar/<menu_id>", methods=["POST"])
@login_required
def editar_menu(nombre_nora, menu_id):
    try:
        data = request.get_json()
        update_data = {
            "contenido": data.get("contenido", "").strip(),
            "opciones": data.get("opciones", []),
            "etiquetas": data.get("etiquetas", []),
            "prioridad": data.get("prioridad", False),
            "activo": data.get("activo", True),
        }
        supabase.table("menus_conocimiento").update(update_data).eq("id", menu_id).execute()
        return jsonify({"success": True}), 200

    except Exception as e:
        print(f"❌ Error al editar menú: {e}")
        return jsonify({"error": "No se pudo editar el menú."}), 500

@panel_cliente_menus_conocimiento_bp.route("/eliminar/<menu_id>", methods=["POST"])
@login_required
def eliminar_menu(nombre_nora, menu_id):
    try:
        supabase.table("menus_conocimiento").delete().eq("id", menu_id).execute()
        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"❌ Error al eliminar menú: {e}")
        return jsonify({"error": "No se pudo eliminar el menú."}), 500
