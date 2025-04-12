print("✅ panel_cliente_respuestas.py cargado correctamente")

from flask import Blueprint, render_template, session, request, redirect, url_for, flash
import os
import json

panel_cliente_respuestas_bp = Blueprint("panel_cliente_respuestas", __name__)

@panel_cliente_respuestas_bp.route("/panel_cliente/respuestas/<nombre_nora>", methods=["GET", "POST"])
def panel_respuestas(nombre_nora):
    if "user" not in session:
        return redirect(url_for("login.login_google"))

    ruta_json = f"clientes/{nombre_nora}/database/bot_data.json"
    os.makedirs(os.path.dirname(ruta_json), exist_ok=True)

    # Si no existe el archivo, se crea vacío
    if not os.path.exists(ruta_json):
        with open(ruta_json, "w", encoding="utf-8") as f:
            json.dump({}, f)

    # Leer las respuestas actuales
    with open(ruta_json, "r", encoding="utf-8") as f:
        respuestas = json.load(f)

    # POST: actualizar contenido de una respuesta
    if request.method == "POST":
        clave = request.form.get("clave")
        nuevo_contenido = request.form.get("contenido")
        nueva_categoria = request.form.get("categoria")

        if clave in respuestas:
            respuestas[clave]["contenido"] = nuevo_contenido
            respuestas[clave]["categoria"] = nueva_categoria
            flash(f"Respuesta '{clave}' actualizada correctamente ✅")
        else:
            flash(f"❌ No se encontró la clave '{clave}' en el archivo.")

        with open(ruta_json, "w", encoding="utf-8") as f:
            json.dump(respuestas, f, indent=4, ensure_ascii=False)

        return redirect(url_for("panel_cliente_respuestas.panel_respuestas", nombre_nora=nombre_nora))

    return render_template(
        "panel_cliente_respuestas.html",
        user=session["user"],
        nombre_nora=nombre_nora,
        respuestas=respuestas
    )
