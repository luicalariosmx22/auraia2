# ✅ Archivo: clientes/aura/routes/panel_cliente_conocimiento/storage.py
# 👉 Manejo de archivos PDF subidos para conocimiento

from flask import jsonify
from clientes.aura.utils.supabase_client import supabase
from datetime import datetime
import uuid

def handle_subir_pdf(nombre_nora, archivo):
    if not archivo:
        return jsonify({"error": "No se recibió archivo"}), 400

    nombre_archivo = archivo.filename
    contenido = archivo.read()
    path = f"{nombre_nora}/conocimiento/{nombre_archivo}"

    upload = supabase.storage.from_("archivos_nora").upload(path, contenido, {"content-type": "application/pdf", "upsert": True})
    if upload.get("error"):
        return jsonify({"error": "Error al subir archivo"}), 500

    url = supabase.storage.from_("archivos_nora").get_public_url(path)

    nuevo = {
        "id": str(uuid.uuid4()),
        "nombre_nora": nombre_nora,
        "nombre_archivo": nombre_archivo,
        "url_archivo": url,
        "fecha_subida": datetime.utcnow().isoformat(),
        "procesado": False,
        "conocimiento_generado": []
    }

    supabase.table("archivos_conocimiento").insert(nuevo).execute()
    return jsonify({"url": url}), 200
