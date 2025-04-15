print("✅ admin_nora_dashboard.py cargado correctamente")

from flask import Blueprint, render_template, request, redirect, url_for
import os
import json
from datetime import datetime

admin_nora_dashboard_bp = Blueprint("admin_nora_dashboard", __name__)

@admin_nora_dashboard_bp.route("/admin/nora/<nombre_nora>/dashboard")
def dashboard_nora(nombre_nora):
    base_path = f"clientes/{nombre_nora}"
    ruta_config = os.path.join(base_path, "config.json")
    ruta_contactos = os.path.join(base_path, "crm", "contactos.json")
    ruta_respuestas = os.path.join(base_path, "database", "bot_data.json")
    ruta_tickets = os.path.join(base_path, "soporte", "tickets.json")

    datos = {
        "nombre_nora": nombre_nora,
        "config": {},
        "contactos": [],
        "respuestas": [],
        "tickets": []
    }

    if os.path.exists(ruta_config):
        with open(ruta_config, "r", encoding="utf-8") as f:
            datos["config"] = json.load(f)

    if os.path.exists(ruta_contactos):
        with open(ruta_contactos, "r", encoding="utf-8") as f:
            datos["contactos"] = json.load(f)

    if os.path.exists(ruta_respuestas):
        with open(ruta_respuestas, "r", encoding="utf-8") as f:
            datos["respuestas"] = json.load(f)

    os.makedirs(os.path.dirname(ruta_tickets), exist_ok=True)
    if not os.path.exists(ruta_tickets):
        with open(ruta_tickets, "w", encoding="utf-8") as f:
            json.dump([], f)

    with open(ruta_tickets, "r", encoding="utf-8") as f:
        datos["tickets"] = json.load(f)

    total_contactos = len(datos["contactos"])
    sin_ia = len([c for c in datos["contactos"] if not c.get("ia", True)])
    sin_etiquetas = len([c for c in datos["contactos"] if not c.get("etiquetas")])

    respuestas_claves = [r.get("keyword") for r in datos["respuestas"] if isinstance(r, dict) and "keyword" in r]

    return render_template("admin_nora_dashboard.html",
        nombre_nora=nombre_nora,
        ia_activada=datos["config"].get("ia_activada", False),
        modulos=datos["config"].get("modulos", []),
        total_contactos=total_contactos,
        sin_ia=sin_ia,
        sin_etiquetas=sin_etiquetas,
        total_respuestas=len(datos["respuestas"]),
        respuestas_claves=respuestas_claves,
        tickets=datos["tickets"]
    )

@admin_nora_dashboard_bp.route("/admin/nora/<nombre_nora>/ticket/<ticket_id>/resolver", methods=["POST"])
def resolver_ticket(nombre_nora, ticket_id):
    ruta_tickets = f"clientes/{nombre_nora}/soporte/tickets.json"

    if os.path.exists(ruta_tickets):
        with open(ruta_tickets, "r", encoding="utf-8") as f:
            tickets = json.load(f)

        for t in tickets:
            if t["id"] == ticket_id:
                t["estado"] = "resuelto"
                t.setdefault("resuelto_en", datetime.now().isoformat())
                break

        with open(ruta_tickets, "w", encoding="utf-8") as f:
            json.dump(tickets, f, indent=4, ensure_ascii=False)

    return redirect(url_for("admin_nora_dashboard.dashboard_nora", nombre_nora=nombre_nora))
