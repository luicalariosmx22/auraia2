print("✅ debug_archivos.py cargado correctamente")

from flask import Blueprint, jsonify
import os

debug_archivos_bp = Blueprint("debug_archivos", __name__, url_prefix="/debug")

@debug_archivos_bp.route("/archivos")
def verificar_archivos():
    archivos_esperados = [
        "clientes/aura/database/bot_data.json",
        "clientes/aura/database/historial/",
        "clientes/aura/config.json",
        "clientes/aura/categorias.json",
        "clientes/aura/servicios_conocimiento.txt",
    ]

    faltantes = []
    for ruta in archivos_esperados:
        if not os.path.exists(ruta):
            faltantes.append(ruta)

    if faltantes:
        print("❌ Archivos faltantes:", faltantes)
        return jsonify({
            "ok": False,
            "faltantes": faltantes
        })

    print("✅ Todos los archivos requeridos están presentes")
    return jsonify({
        "ok": True,
        "mensaje": "Todos los archivos están presentes"
    })
