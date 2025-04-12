print("✅ admin_noras.py cargado correctamente")

from flask import Blueprint, render_template, redirect, url_for
import os
import json
from datetime import datetime

admin_noras_bp = Blueprint("admin_noras", __name__)

@admin_noras_bp.route("/admin/noras")
def vista_admin():
    directorio_clientes = "clientes"
    lista_noras = []

    for nombre in os.listdir(directorio_clientes):
        ruta_config = os.path.join(directorio_clientes, nombre, "config.json")
        ruta_tickets = os.path.join(directorio_clientes, nombre, "soporte", "tickets.json")

        if os.path.exists(ruta_config):
            try:
                with open(ruta_config, "r", encoding="utf-8") as f:
                    config = json.load(f)

                # Leer tickets pendientes
                pendientes = 0
                if os.path.exists(ruta_tickets):
                    with open(ruta_tickets, "r", encoding="utf-8") as tf:
                        tickets = json.load(tf)
                        pendientes = len([t for t in tickets if t.get("estado") == "pendiente"])

                fecha_mod = datetime.fromtimestamp(os.path.getmtime(ruta_config)).strftime("%Y-%m-%d %H:%M")
                lista_noras.append({
                    "nombre": nombre,
                    "ia_activada": config.get("ia_activada", False),
                    "modulos": config.get("modulos", []),
                    "ultima_actualizacion": fecha_mod,
                    "tickets_pendientes": pendientes
                })

            except Exception as e:
                print(f"❌ Error al procesar Nora {nombre}: {str(e)}")

    return render_template("admin_noras.html", noras=lista_noras)


@admin_noras_bp.route("/admin")
def redireccionar_a_noras():
    return redirect(url_for("admin_noras.vista_admin"))
