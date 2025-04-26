print("✅ panel_chat_api.py cargado correctamente")

from flask import jsonify, request, redirect, url_for, session
from clientes.aura.routes.panel_chat import panel_chat_bp
from clientes.aura.routes.panel_chat_utils import normalizar_numero, leer_contactos, leer_historial, guardar_historial
import datetime

@panel_chat_bp.route("/api/chat/<telefono>")
def api_chat(telefono):
    print(f"\U0001f50d Iniciando función api_chat para el teléfono: {telefono}")
    try:
        telefono = normalizar_numero(telefono)
        print(f"\U0001f50d Teléfono normalizado: {telefono}")

        contactos = leer_contactos()
        print(f"✅ Contactos cargados: {len(contactos)}")

        contacto = next((c for c in contactos if normalizar_numero(c["telefono"]) == telefono), {})
        print(f"\U0001f50d Contacto encontrado: {contacto}")

        historial = leer_historial(telefono)
        print(f"✅ Historial cargado: {len(historial)} mensajes")

        if not contacto.get("nombre"):
            contacto["nombre"] = f"Usuario {telefono[-10:]}"

        for mensaje in historial:
            mensaje["remitente"] = "Tú" if mensaje["emisor"] == "nora" else contacto["nombre"]

        print(f"✅ Respuesta lista para el teléfono: {telefono}")
        return jsonify({
            "success": True,
            "contacto": contacto,
            "mensajes": historial
        })
    except Exception as e:
        print(f"❌ Error en api_chat para el teléfono {telefono}: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@panel_chat_bp.route("/api/enviar-mensaje", methods=["POST"])
def api_enviar_mensaje():
    print("\U0001f50d Iniciando función api_enviar_mensaje...")
    data = request.json
    print(f"\U0001f50d Datos recibidos: {data}")
    telefono = normalizar_numero(data.get("numero"))
    texto = data.get("mensaje")

    if not all([telefono, texto]):
        print("❌ Datos incompletos para enviar mensaje.")
        return jsonify({"success": False, "error": "Datos incompletos"}), 400

    historial = leer_historial(telefono)
    historial.append({
        "emisor": "usuario",
        "mensaje": texto,
        "fecha": datetime.datetime.now().strftime("%d-%b %H:%M")
    })

    guardar_historial("Nora", telefono, historial)
    print(f"✅ Mensaje enviado y guardado en el historial para {telefono}.")
    return jsonify({"success": True})

@panel_chat_bp.route("/api/toggle-ia/<telefono>", methods=["POST"])
def api_toggle_ia(telefono):
    print(f"\U0001f50d Iniciando función api_toggle_ia para el teléfono: {telefono}")
    from clientes.aura.routes.panel_chat_utils import supabase  # Importación puntual
    telefono = normalizar_numero(telefono)
    try:
        response = supabase.table("contactos").select("*").eq("telefono", telefono).execute()
        if not response.data:
            print(f"❌ Error al cargar contacto para {telefono}.")
            return jsonify({"success": False})

        contacto = response.data[0]
        nuevo_estado = not contacto.get("ia_activada", True)
        supabase.table("contactos").update({"ia_activada": nuevo_estado}).eq("telefono", telefono).execute()
        print(f"✅ Estado de IA cambiado para {telefono}: {nuevo_estado}")
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error al cambiar estado de IA para {telefono}: {str(e)}")
        return jsonify({"success": False})

@panel_chat_bp.route("/api/programar-envio", methods=["POST"])
def api_programar_envio():
    print("\U0001f50d Iniciando función api_programar_envio...")
    data = request.json
    print(f"\U0001f50d Datos recibidos: {data}")
    try:
        from clientes.aura.routes.panel_chat_utils import supabase  # Importación puntual
        response = supabase.table("envios_programados").insert({
            "numero": data.get("numero"),
            "mensaje": data.get("mensaje"),
            "fecha": data.get("fecha"),
            "hora": data.get("hora")
        }).execute()
        if not response.data:
            print("❌ Error al programar envío.")
            return jsonify({"success": False})
        print(f"✅ Envío programado correctamente: {response.data}")
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error al programar envío: {str(e)}")
        return jsonify({"success": False})

@panel_chat_bp.route("/api/etiqueta/<telefono>", methods=["POST", "DELETE"])
def api_gestion_etiqueta(telefono):
    print(f"\U0001f50d Iniciando función api_gestion_etiqueta para el teléfono: {telefono}")
    from clientes.aura.routes.panel_chat_utils import supabase  # Importación puntual
    body = request.get_json()
    etiqueta = body.get("etiqueta", "").strip().lower()
    telefono = normalizar_numero(telefono)

    try:
        response = supabase.table("contactos").select("*").eq("telefono", telefono).execute()
        if not response.data:
            print(f"❌ Contacto no encontrado para el teléfono: {telefono}")
            return jsonify({"success": False, "error": "Contacto no encontrado"}), 404

        contacto = response.data[0]
        etiquetas = set(contacto.get("etiquetas", []))

        if request.method == "POST":
            etiquetas.add(etiqueta)
            print(f"✅ Etiqueta '{etiqueta}' agregada al contacto {telefono}.")
        elif request.method == "DELETE":
            etiquetas.discard(etiqueta)
            print(f"✅ Etiqueta '{etiqueta}' eliminada del contacto {telefono}.")

        supabase.table("contactos").update({"etiquetas": list(etiquetas)}).eq("telefono", telefono).execute()
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error en api_gestion_etiqueta para el teléfono {telefono}: {str(e)}")
        return jsonify({"success": False, "error": str(e)})
