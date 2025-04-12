# 📁 clientes/aura/routes/admin_noras.py

from flask import Blueprint, render_template
import os
import json

admin_noras_bp = Blueprint("admin_noras", __name__)

@admin_noras_bp.route("/admin/noras")
def ver_noras():
    base_path = "clientes"
    noras_info = []

    if os.path.exists(base_path):
        for carpeta in os.listdir(base_path):
            ruta_config = os.path.join(base_path, carpeta, "config.json")

            if os.path.isfile(ruta_config):
                with open(ruta_config, "r", encoding="utf-8") as f:
                    data = json.load(f)

                nombre = data.get("nombre", carpeta)
                telefono = data.get("telefono", "No asignado")
                modulos = data.get("modulos", [])
                estado = data.get("estado", "desconocido")
                ultima_actividad = "Simulado"  # Aquí puedes integrar lectura real

                noras_info.append({
                    "nombre": nombre,
                    "telefono": telefono,
                    "modulos": modulos,
                    "estado": estado,
                    "ultima_actividad": ultima_actividad,
                    "carpeta": carpeta
                })

    return render_template("admin_noras.html", noras=noras_info)
