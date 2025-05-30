from flask import jsonify, Blueprint
from .panel_cliente_tareas import panel_cliente_tareas_bp
from datetime import datetime
from pytz import timezone
from supabase import create_client
import os
import json  # Asegúrate de tener este import al inicio si no está

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

# ✅ Programada: Enviar tareas del día
def enviar_tareas_del_dia_por_whatsapp():
    try:
        # Obtener todas las Noras con sus módulos
        bots = supabase.table("configuracion_bot").select("nombre_nora, modulos").execute().data

        # Filtrar solo las que tienen "tareas" activado
        noras_con_tareas = [
            bot["nombre_nora"]
            for bot in bots
            if "tareas" in (
                json.loads(bot["modulos"]) if isinstance(bot["modulos"], str) else bot["modulos"]
            )
        ]

        # Procesar cada Nora
        for nombre_nora in noras_con_tareas:
            # Aquí va tu lógica para enviar las tareas por WhatsApp
            print(f"📩 Enviando tareas del día para Nora: {nombre_nora}")
            # ... (tu código real aquí) ...

    except Exception as e:
        print(f"❌ Error al enviar tareas por WhatsApp: {e}")

# ✅ Programada: Enviar resumen de tareas a las 6PM
def enviar_resumen_6pm_por_whatsapp():
    print("📤 Enviando resumen 6PM...")
    hoy = datetime.now(zona).strftime("%Y-%m-%d")

    nora_configs = supabase.table("configuracion_bot").select("nombre_nora").eq("modulo_tareas_activo", True).execute().data

    for config in nora_configs:
        nombre_nora = config["nombre_nora"]
        usuarios = supabase.table("usuarios_clientes").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).execute().data or []

        for usuario in usuarios:
            telefono_original = usuario.get("telefono")
            telefono_normalizado = normalizar_numero(telefono_original)
            if not telefono_normalizado:
                print(f"⚠️ Usuario sin número válido: {usuario['nombre']} ({telefono_original})")
                continue

            tareas = obtener_tareas_para_usuario(usuario["id"], hoy)
            if not tareas:
                continue

            completadas = [t for t in tareas if t["estatus"] == "completada"]
            pendientes = [t for t in tareas if t["estatus"] != "completada"]

            mensaje = f"📍 Resumen de hoy, {usuario['nombre']}:\n"
            mensaje += f"📋 Total tareas: {len(tareas)}\n"
            mensaje += f"✅ Completadas: {len(completadas)}\n"
            mensaje += f"⏳ Pendientes: {len(pendientes)}\n"

            if pendientes:
                mensaje += "\n🔸 Tareas sin completar:\n"
                for t in pendientes:
                    mensaje += f"⏳ {t['codigo_tarea']}: {t['titulo']}\n"

            enviar_mensaje_whatsapp(f"+{telefono_normalizado}", mensaje)

@panel_cliente_tareas_bp.route("/whatsapp/8am", methods=["POST"])
def enviar_tareas_8am():
    enviar_tareas_del_dia_por_whatsapp()
    return jsonify({"status": "enviado"})

@panel_cliente_tareas_bp.route("/whatsapp/6pm", methods=["POST"])
def enviar_resumen_6pm():
    enviar_resumen_6pm_por_whatsapp()
    return jsonify({"status": "enviado"})

whatsapp_bp = Blueprint(
    "whatsapp", __name__,
    template_folder="../../../templates/panel_cliente_tareas"
)

@whatsapp_bp.route("/panel_cliente/<nombre_nora>/whatsapp/prueba", methods=["GET"])
def prueba_whatsapp(nombre_nora):
    return f"Vista de prueba WHATSAPP para {nombre_nora}"