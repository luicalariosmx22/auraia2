from flask import jsonify, Blueprint, render_template
from .panel_cliente_tareas import panel_cliente_tareas_bp
from datetime import datetime
from pytz import timezone
from supabase import create_client
import os
import json  # Asegúrate de tener este import al inicio si no está

# 🚫 IMPORTANTE: FUNCIONES DE WHATSAPP DESACTIVADAS
# Las tareas ahora solo se envían por correo electrónico
# Todas las funciones de WhatsApp están comentadas y deshabilitadas

zona = timezone("America/Hermosillo")
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

from clientes.aura.utils.twilio_sender import enviar_mensaje, registrar_envio
from clientes.aura.utils.normalizador import normalizar_numero  # ✅ IMPORT NUEVO

def obtener_tareas_para_usuario(usuario_id, fecha):
    return supabase.table("tareas").select("*") \
        .eq("usuario_empresa_id", usuario_id) \
        .eq("fecha_limite", fecha) \
        .eq("activo", True).execute().data

def generar_mensaje_tareas(tareas, usuario, empresa_nombre):
    if not tareas:
        return f"👋 Hola {usuario['nombre']}, hoy no tienes tareas asignadas en {empresa_nombre}."

    mensaje = f"👋 Hola {usuario['nombre']}, estas son tus tareas de hoy en {empresa_nombre}:\n\n"
    for t in tareas:
        estado = "⏳"
        if t["estatus"] == "completada":
            estado = "✅"
        elif t["estatus"] in ["vencida", "atrasada"]:
            estado = "❗"
        mensaje += f"{estado} {t['codigo_tarea']}: {t['titulo']}\n"

    mensaje += "\nPuedes ver tus tareas completas en tu panel de Nora."
    return mensaje

def enviar_mensaje_whatsapp(numero, mensaje):
    try:
        if not numero or not numero.startswith("+"):
            print(f"❌ Número inválido u omitido: {numero}")
            return {"status": "omitido", "mensaje": "número inválido"}
        full_number = f"whatsapp:{numero}"
        r = enviar_mensaje(
            mensaje,
            os.getenv("TWILIO_WHATSAPP_NUMBER"),
            full_number
        )
        return {"status": "enviado", "sid": r.sid}
    except Exception as e:
        print(f"❌ Error al enviar WhatsApp a {numero}: {e}")
        return {"status": "error", "mensaje": str(e)}

# ❌ DESACTIVADA: Enviar tareas del día por WhatsApp
def enviar_tareas_del_dia_por_whatsapp():
    print("🚫 Función enviar_tareas_del_dia_por_whatsapp DESACTIVADA")
    return {"status": "desactivada", "mensaje": "Función temporalmente deshabilitada"}
    
    # CÓDIGO COMENTADO - NO SE EJECUTA
    # try:
    #     # Obtener solo las Noras con el módulo de tareas activo (campo JSON)
    #     nora_configs = supabase.table("configuracion_bot") \
    #         .select("nombre_nora") \
    #         .filter("modulos->>modulo_tareas", "eq", "true") \
    #         .execute().data

    #     hoy = datetime.now(zona).strftime("%Y-%m-%d")

    #     for config in nora_configs:
    #         nombre_nora = config["nombre_nora"]
    #         print(f"📩 Enviando tareas del día para Nora: {nombre_nora}")
    #         usuarios = supabase.table("usuarios_clientes").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).execute().data or []
    #         for usuario in usuarios:
    #             telefono_original = usuario.get("telefono")
    #             telefono_normalizado = normalizar_numero(telefono_original)
    #             if not telefono_normalizado:
    #                 print(f"⚠️ Usuario sin número válido: {usuario['nombre']} ({telefono_original})")
    #                 continue
    #             tareas = obtener_tareas_para_usuario(usuario["id"], hoy)
    #             if not tareas:
    #                 print(f"ℹ️ Usuario {usuario['nombre']} no tiene tareas para hoy.")
    #                 continue
    #             mensaje = generar_mensaje_tareas(tareas, usuario, nombre_nora)
    #             resultado = enviar_mensaje_whatsapp(f"+{telefono_normalizado}", mensaje)
    #             print(f"➡️ Enviado a {usuario['nombre']} ({telefono_normalizado}): {resultado}")
    # except Exception as e:
    #     print(f"❌ Error al enviar tareas por WhatsApp: {e}")

# ❌ DESACTIVADA: Enviar resumen de tareas a las 6PM
def enviar_resumen_6pm_por_whatsapp():
    print("🚫 Función enviar_resumen_6pm_por_whatsapp DESACTIVADA - Solo se envían por correo")
    return {"status": "desactivada", "mensaje": "Función temporalmente deshabilitada - Solo envío por correo"}
    
    # CÓDIGO COMENTADO - NO SE EJECUTA
    # print("\U0001F4E4 Enviando resumen 6PM...")
    # hoy = datetime.now(zona).strftime("%Y-%m-%d")

    # nora_configs = supabase.table("configuracion_bot") \
    #     .select("nombre_nora") \
    #     .filter("modulos->>modulo_tareas", "eq", "true") \
    #     .execute().data

    # for config in nora_configs:
    #     nombre_nora = config["nombre_nora"]
    #     usuarios = supabase.table("usuarios_clientes").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).execute().data or []

    #     for usuario in usuarios:
    #         telefono_original = usuario.get("telefono")
    #         telefono_normalizado = normalizar_numero(telefono_original)
    #         if not telefono_normalizado:
    #             print(f"⚠️ Usuario sin número válido: {usuario['nombre']} ({telefono_original})")
    #             continue

    #         tareas = obtener_tareas_para_usuario(usuario["id"], hoy)
    #         if not tareas:
    #             continue

    #         completadas = [t for t in tareas if t["estatus"] == "completada"]
    #         pendientes = [t for t in tareas if t["estatus"] != "completada"]

    #         mensaje = f"📍 Resumen de hoy, {usuario['nombre']}:\n"
    #         mensaje += f"📋 Total tareas: {len(tareas)}\n"
    #         mensaje += f"✅ Completadas: {len(completadas)}\n"
    #         mensaje += f"⏳ Pendientes: {len(pendientes)}\n"

    #         if pendientes:
    #             mensaje += "\n🔸 Tareas sin completar:\n"
    #             for t in pendientes:
    #                 mensaje += f"⏳ {t['codigo_tarea']}: {t['titulo']}\n"

    #         enviar_mensaje_whatsapp(f"+{telefono_normalizado}", mensaje)

@panel_cliente_tareas_bp.route("/whatsapp/8am", methods=["POST"])
def enviar_tareas_8am():
    resultado = enviar_tareas_del_dia_por_whatsapp()
    return jsonify(resultado)

@panel_cliente_tareas_bp.route("/whatsapp/6pm", methods=["POST"])
def enviar_resumen_6pm():
    resultado = enviar_resumen_6pm_por_whatsapp()
    return jsonify(resultado)

@panel_cliente_tareas_bp.route("/whatsapp/manual", methods=["POST", "GET"])
def enviar_tareas_manual():
    return jsonify({
        "ok": False, 
        "msg": "🚫 Envío por WhatsApp desactivado - Solo se envían tareas por correo electrónico",
        "status": "desactivado"
    })
    
    # CÓDIGO COMENTADO - NO SE EJECUTA
    # from flask import request
    # print("[DEBUG] Método:", request.method)
    # if request.method == "POST":
    #     print("[DEBUG] POST data:", request.json)
    #     usuario_id = request.json.get("usuario_id") if request.json else None
    #     fecha = request.json.get("fecha") if request.json else None
    # else:  # GET
    #     print("[DEBUG] GET args:", request.args)
    #     usuario_id = request.args.get("usuario_id")
    #     fecha = request.args.get("fecha")
    # print(f"[DEBUG] usuario_id: {usuario_id}, fecha: {fecha}")
    # if not usuario_id:
    #     print("[DEBUG] Falta usuario_id")
    #     return jsonify({"ok": False, "msg": "Falta usuario_id"}), 400
    # if not fecha:
    #     fecha = datetime.now(zona).strftime("%Y-%m-%d")
    # usuario = supabase.table("usuarios_clientes").select("*").eq("id", usuario_id).single().execute().data
    # print(f"[DEBUG] usuario: {usuario}")
    # if not usuario:
    #     print("[DEBUG] Usuario no encontrado")
    #     return jsonify({"ok": False, "msg": "Usuario no encontrado"}), 404
    # telefono_original = usuario.get("telefono")
    # telefono_normalizado = normalizar_numero(telefono_original)
    # print(f"[DEBUG] telefono_original: {telefono_original}, telefono_normalizado: {telefono_normalizado}")
    # if not telefono_normalizado:
    #     print("[DEBUG] Usuario sin número válido")
    #     return jsonify({"ok": False, "msg": f"Usuario sin número válido: {telefono_original}"}), 400
    # tareas = obtener_tareas_para_usuario(usuario_id, fecha)
    # print(f"[DEBUG] tareas: {tareas}")
    # if not tareas:
    #     print("[DEBUG] El usuario no tiene tareas para esa fecha")
    #     return jsonify({"ok": False, "msg": "El usuario no tiene tareas para esa fecha"}), 200
    # mensaje = generar_mensaje_tareas(tareas, usuario, usuario.get("nombre_nora", "Nora"))
    # print(f"[DEBUG] mensaje: {mensaje}")
    # resultado = enviar_mensaje_whatsapp(f"+{telefono_normalizado}", mensaje)
    # print(f"[DEBUG] resultado envio: {resultado}")
    # return jsonify({"ok": True, "msg": "Envío realizado", "resultado": resultado})

@panel_cliente_tareas_bp.route("/<nombre_nora>/tareas/whatsapp/manual/panel", methods=["GET"])
def panel_envio_manual_whatsapp(nombre_nora):
    # Panel desactivado - redirigir o mostrar mensaje
    return f"""
    <div style="text-align: center; padding: 50px; font-family: Arial;">
        <h2>🚫 Panel de WhatsApp Desactivado</h2>
        <p>El envío de tareas por WhatsApp ha sido deshabilitado.</p>
        <p>Las tareas ahora se envían únicamente por <strong>correo electrónico</strong>.</p>
        <br>
        <a href="/panel_cliente/{nombre_nora}/tareas" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
            Volver al Panel de Tareas
        </a>
    </div>
    """

whatsapp_bp = Blueprint(
    "whatsapp", __name__,
    template_folder="../../../templates/panel_cliente_tareas"
)

@whatsapp_bp.route("/panel_cliente/<nombre_nora>/whatsapp/prueba", methods=["GET"])
def prueba_whatsapp(nombre_nora):
    return f"Vista de prueba WHATSAPP para {nombre_nora}"

# --- EXPORTS PARA COMPATIBILIDAD CON SCHEDULER Y OTROS MODULOS ---
__all__ = [
    "enviar_tareas_del_dia_por_whatsapp",
    "enviar_resumen_6pm_por_whatsapp",
]