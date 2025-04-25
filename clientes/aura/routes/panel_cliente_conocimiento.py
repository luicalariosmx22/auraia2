# 📁 clientes/aura/routes/panel_cliente_conocimiento.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

panel_cliente_conocimiento_bp = Blueprint("panel_cliente_conocimiento", __name__)

@panel_cliente_conocimiento_bp.route("/panel_cliente/<nombre_nora>/conocimiento", methods=["GET", "POST"])
def conocimiento_nora(nombre_nora):
    try:
        # Obtener número de Nora
        config = supabase.table("configuracion_bot").select("numero_nora").eq("nombre_nora", nombre_nora).single().execute().data
        numero_nora = config.get("numero_nora")

        # Insertar conocimiento nuevo si es POST
        if request.method == "POST":
            titulo = request.form.get("titulo", "").strip()
            contenido = request.form.get("contenido", "").strip()
            if titulo and contenido:
                bloques = [b.strip() for b in contenido.split("\n\n") if b.strip()]
                inserts = [{"numero_nora": numero_nora, "titulo": titulo, "contenido": bloque} for bloque in bloques]
                supabase.table("conocimiento_nora").insert(inserts).execute()
                flash("✅ Conocimiento agregado", "success")
            return redirect(url_for("panel_cliente_conocimiento.conocimiento_nora", nombre_nora=nombre_nora))

        # Cargar bloques existentes
        bloques_res = supabase.table("conocimiento_nora").select("id, titulo, contenido").eq("numero_nora", numero_nora).execute()
        bloques = bloques_res.data or []

        return render_template("panel_cliente_conocimiento.html", nombre_nora=nombre_nora, bloques=bloques)

    except Exception as e:
        print(f"❌ Error: {e}")
        flash("❌ Error al cargar el centro de conocimiento", "error")
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
