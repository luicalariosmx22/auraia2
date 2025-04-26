print("✅ panel_chat_api.py cargado correctamente")

from flask import jsonify, request, session, redirect, url_for
from clientes.aura.routes.panel_chat import panel_chat_bp
from clientes.aura.routes.panel_chat_utils import normalizar_numero, leer_contactos, guardar_historial
import datetime

@panel_chat_bp.route("/api/chat/<telefono>")
def api_chat(telefono):
    print(f"🔍 Iniciando función api_chat para el teléfono: {telefono}")
    try:
        telefono = normalizar_numero(telefono)
        print(f"🔍 Teléfono normalizado: {telefono}")

        print("🔍 Leyendo contactos...")
        contactos = leer_contactos()
        print(f"✅ Contactos cargados: {len(contactos)}")

        print("🔍 Buscando contacto específico...")
        contacto = next((c for c in contactos if normalizar_numero(c["telefono"]) == telefono), {})

        if not contacto.get("nombre"):
            contacto["nombre"] = f"Usuario {telefono[-10:]}"

        print(f"✅ Contacto encontrado: {contacto}")

        # No cargamos historial, solo contacto
        return jsonify({
            "success": True,
            "contacto": contacto,
            "mensajes": []
        })
    except Exception as e:
        print(f"❌ Error en api_chat para el teléfono {telefono}: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@panel_chat_bp.route("/api/enviar-mensaje", methods=["POST"])
def api_enviar_mensaje():
    print("🔍 Iniciando función api_enviar_mensaje...")
    data = request.json
    print(f"🔍 Datos recibidos: {data}")
    telefono = normalizar_numero(data.get("numero"))
    texto = data.get("mensaje")

    if not all([telefono, texto]):
        print("❌ Datos incompletos para enviar mensaje.")
        return jsonify({"success": False, "error": "Datos incompletos"}), 400

    print("🔍 Guardando nuevo mensaje...")
    nuevo_mensaje = {
        "nombre_nora": "Nora",
        "telefono": telefono,
        "mensaje": texto,
        "emisor": "usuario",
        "hora": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp": datetime.datetime.now().isoformat()
    }
    try:
        from clientes.aura.routes.panel_chat_utils import supabase
        print("🔍 Insertando mensaje en historial_conversaciones...")
        supabase.table("historial_conversaciones").insert(nuevo_mensaje).execute()
        print(f"✅ Mensaje guardado exitosamente para {telefono}.")
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error al guardar mensaje: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@panel_chat_bp.route("/api/toggle-ia/<telefono>", methods=["POST"])
def api_toggle_ia(telefono):
    print(f"🔍 Iniciando función api_toggle_ia para el teléfono: {telefono}")
    from clientes.aura.routes.panel_chat_utils import supabase
    telefono = normalizar_numero(telefono)
    try:
        response = supabase.table("contactos").select("*").eq("telefono", telefono).execute()
        if not response.data:
            print(f"❌ Contacto no encontrado para {telefono}.")
            return jsonify({"success": False})

        contacto = response.data[0]
        nuevo_estado = not contacto.get("ia_activada", True)
        supabase.table("contactos").update({"ia_activada": nuevo_estado}).eq("telefono", telefono).execute()
        print(f"✅ Estado de IA cambiado a {nuevo_estado} para {telefono}")
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error al cambiar estado de IA: {str(e)}")
        return jsonify({"success": False})

@panel_chat_bp.route("/api/etiqueta/<telefono>", methods=["POST", "DELETE"])
def api_gestion_etiqueta(telefono):
    print(f"🔍 Iniciando función api_gestion_etiqueta para el teléfono: {telefono}")
    from clientes.aura.routes.panel_chat_utils import supabase
    body = request.get_json()
    etiqueta = body.get("etiqueta", "").strip().lower()
    telefono = normalizar_numero(telefono)

    try:
        response = supabase.table("contactos").select("*").eq("telefono", telefono).execute()
        if not response.data:
            print(f"❌ Contacto no encontrado para {telefono}.")
            return jsonify({"success": False, "error": "Contacto no encontrado"}), 404

        contacto = response.data[0]
        etiquetas = set(contacto.get("etiquetas", []))

        if request.method == "POST":
            etiquetas.add(etiqueta)
            print(f"✅ Etiqueta '{etiqueta}' agregada.")
        elif request.method == "DELETE":
            etiquetas.discard(etiqueta)
            print(f"✅ Etiqueta '{etiqueta}' eliminada.")

        supabase.table("contactos").update({"etiquetas": list(etiquetas)}).eq("telefono", telefono).execute()
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error en api_gestion_etiqueta: {str(e)}")
        return jsonify({"success": False, "error": str(e)})
