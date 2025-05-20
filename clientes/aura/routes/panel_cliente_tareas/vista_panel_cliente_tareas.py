# ✅ Archivo: clientes/aura/routes/panel_cliente_tareas/vista_panel_cliente_tareas.py
# 👉 Vista principal del módulo de tareas con AI y templates por proyecto

from flask import Blueprint, render_template, request, redirect, url_for, session
from clientes.aura.utils.supabase_utils import obtener_tareas_por_nora, crear_tarea, obtener_templates_tarea
from clientes.aura.utils.login_required import login_required_cliente

panel_cliente_tareas_bp = Blueprint('panel_cliente_tareas', __name__)

@panel_cliente_tareas_bp.route('/panel_cliente/<nombre_nora>/tareas')
@login_required_cliente
def panel_tareas(nombre_nora):
    if not session.get("modulos_activos", {}).get("tareas", False):
        return redirect(url_for('panel_cliente.panel_cliente', nombre_nora=nombre_nora))

    tareas = obtener_tareas_por_nora(nombre_nora)
    templates = obtener_templates_tarea()
    return render_template("panel_cliente_tareas/index.html", tareas=tareas, templates=templates, nombre_nora=nombre_nora)

@panel_cliente_tareas_bp.route('/panel_cliente/<nombre_nora>/tareas/crear', methods=['POST'])
@login_required_cliente
def crear_tarea_nueva(nombre_nora):
    data = request.form
    tarea = {
        "titulo": data.get("titulo"),
        "descripcion": data.get("descripcion"),
        "fecha_inicio": data.get("fecha_inicio"),
        "fecha_plazo": data.get("fecha_plazo"),
        "asignado_a": data.get("asignado_a"),
        "empresa": data.get("empresa"),
        "nombre_nora": nombre_nora,
    }
    crear_tarea(tarea)
    return redirect(url_for('panel_cliente_tareas.panel_tareas', nombre_nora=nombre_nora))
