# 📁 clientes/aura/routes/panel_cliente_conocimiento.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from clientes.aura.utils.login_required import login_required
from clientes.aura.utils.supabase_client import supabase
import os

panel_cliente_conocimiento_bp = Blueprint("panel_cliente_conocimiento", __name__)

@panel_cliente_conocimiento_bp.route("/panel_cliente/<nombre_nora>/conocimiento", methods=["GET", "POST"])
@login_required
def conocimiento_nora(nombre_nora):
    try:
        config_res = supabase.table("configuracion_bot").select("numero_nora").eq("nombre_nora", nombre_nora).single().execute()
        numero_nora = config_res.data["numero_nora"]

        if request.method == "POST":
            titulo = request.form.get("titulo", "").strip()
            contenido = request.form.get("contenido", "").strip()

            if not titulo or not contenido:
                flash("❌ Título y contenido son obligatorios", "error")
            else:
                bloques = [b.strip() for b in contenido.split("\n\n") if b.strip()]
                inserts = [{"numero_nora": numero_nora, "titulo": titulo, "contenido": b} for b in bloques]
                supabase.table("conocimiento_nora").insert(inserts).execute()
                flash("✅ Conocimiento agregado", "success")

        # Mostrar bloques existentes
        data_res = supabase.table("conocimiento_nora").select("id, titulo, contenido").eq("numero_nora", numero_nora).execute()
        bloques = data_res.data or []

        return render_template("entrena_conocimiento.html", nombre_nora=nombre_nora, bloques=bloques)

    except Exception as e:
        print(f"❌ Error al cargar conocimiento: {e}")
        flash("❌ Error al cargar conocimiento", "error")
        return redirect(url_for("panel_cliente.panel_cliente", nombre_nora=nombre_nora))

@panel_cliente_conocimiento_bp.route("/panel_cliente/<nombre_nora>/conocimiento/eliminar/<bloque_id>", methods=["POST"])
def eliminar_bloque(nombre_nora, bloque_id):
    try:
        supabase.table("conocimiento_nora").delete().eq("id", bloque_id).execute()
        flash("✅ Bloque eliminado", "success")
    except Exception as e:
        print(f"❌ Error al eliminar bloque: {e}")
        flash("❌ Error al eliminar bloque", "error")

    return redirect(url_for("panel_cliente_conocimiento.conocimiento_nora", nombre_nora=nombre_nora))
