print("✅ panel_cliente_respuestas.py cargado correctamente")

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import os
import json

panel_cliente_respuestas_bp = Blueprint("panel_cliente_respuestas", __name__)

@panel_cliente_respuestas_bp.route("/panel_cliente/respuestas/<nombre_nora>", methods=["GET", "POST"])
def panel_respuestas(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    ruta_archivo = f"clientes/{nombre_nora}/database/bot_data.json"
    if not os.path.exists(ruta_archivo):
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            json.dump([], f)

    if request.method == "POST":
        palabra_clave = request.form.get("palabra_clave", "").strip().lower()
        respuesta = request.form.get("respuesta", "").strip()
        index = request.form.get("index")

        if not palabra_clave or not respuesta:
            flash("❌ Completa ambos campos", "error")
            return redirect(request.url)

        with open(ruta_archivo, "r", encoding="utf-8") as f:
            data = json.load(f)

        if index:
            try:
                idx = int(index)
                data[idx] = {"keyword": palabra_clave, "respuesta": respuesta}
                flash("✅ Respuesta actualizada", "success")
            except:
                flash("❌ No se pudo editar", "error")
        else:
            data.append({"keyword": palabra_clave, "respuesta": respuesta})
            flash("✅ Respuesta agregada", "success")

        with open(ruta_archivo, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return redirect(url_for("panel_cliente.panel_cliente_respuestas.panel_respuestas", nombre_nora=nombre_nora))

    eliminar = request.args.get("eliminar")
    if eliminar is not None:
        try:
            idx = int(eliminar)
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                data = json.load(f)
            if 0 <= idx < len(data):
                eliminada = data.pop(idx)
                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                flash(f"❌ Respuesta eliminada: '{eliminada['keyword']}'", "success")
        except:
            flash("❌ No se pudo eliminar", "error")
        return redirect(url_for("panel_cliente.panel_cliente_respuestas.panel_respuestas", nombre_nora=nombre_nora))

    with open(ruta_archivo, "r", encoding="utf-8") as f:
        respuestas = json.load(f)

    return render_template(
        "panel_cliente_respuestas.html",
        nombre_nora=nombre_nora,
        respuestas=respuestas,
        user=session["user"]
    )
