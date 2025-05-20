# ✅ Archivo: clientes/aura/routes/panel_cliente_tareas/panel_cliente_tareas.py
# 👉 Blueprint exportado correctamente como panel_cliente_tareas

from flask import Blueprint, render_template, request
from datetime import datetime, timedelta
from pytz import timezone
from supabase import create_client
import os
import uuid

panel_cliente_tareas_bp = Blueprint("panel_cliente_tareas", __name__, template_folder="../../templates/panel_cliente_tareas")

# ✅ Inicializar Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
zona = timezone("America/Hermosillo")

# ✅ Mejorada: generar_codigo_tarea()
def generar_codigo_tarea(iniciales_usuario):
    fecha = datetime.now().strftime("%d%m%y")
    # Sanitizar iniciales (solo letras mayúsculas)
    iniciales = ''.join(filter(str.isalnum, iniciales_usuario.upper()))[:3]
    base_codigo = f"{iniciales}-{fecha}"
    existentes = supabase.table("tareas").select("id").ilike("codigo_tarea", f"{base_codigo}-%").execute()
    correlativo = len(existentes.data) + 1
    return f"{base_codigo}-{str(correlativo).zfill(3)}"

# ✅ Función: crear_tarea(data)
def crear_tarea(data):
    if not data.get("usuario_empresa_id"):
        return {"error": "La tarea debe estar asignada a un usuario"}, 400

    iniciales = data.get("iniciales_usuario", "NN")
    codigo = generar_codigo_tarea(iniciales)
    fecha_limite = data.get("fecha_limite")

    # ⚠️ Validar fecha futura
    if fecha_limite and fecha_limite < datetime.now().strftime("%Y-%m-%d"):
        fecha_limite = datetime.now().strftime("%Y-%m-%d")

    nueva = {
        "id": str(uuid.uuid4()),
        "codigo_tarea": codigo,
        "titulo": data.get("titulo"),
        "descripcion": data.get("descripcion"),
        "fecha_limite": fecha_limite,
        "prioridad": data.get("prioridad", "media"),
        "estatus": data.get("estatus", "pendiente"),
        "usuario_empresa_id": data["usuario_empresa_id"],
        "asignado_a": data.get("asignado_a"),
        "empresa_id": data.get("empresa_id"),
        "cliente_id": data.get("cliente_id"),
        "origen": data.get("origen"),
        "creado_por": data.get("creado_por"),
        "activo": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    result = supabase.table("tareas").insert(nueva).execute()
    return result.data, 200

# ✅ Función: obtener_tarea_por_id(tarea_id)
def obtener_tarea_por_id(tarea_id):
    result = supabase.table("tareas").select("*").eq("id", tarea_id).single().execute()
    return result.data

# ✅ Función: listar_tareas_por_usuario(usuario_empresa_id)
def listar_tareas_por_usuario(usuario_empresa_id):
    result = supabase.table("tareas").select("*") \
        .eq("usuario_empresa_id", usuario_empresa_id) \
        .eq("activo", True) \
        .order("fecha_limite", desc=False).execute()
    return result.data

# ✅ Función: actualizar_tarea(tarea_id, data)
def actualizar_tarea(tarea_id, data):
    # Validar que el usuario tenga permiso para editar (solo placeholder aquí)
    data["updated_at"] = datetime.now().isoformat()
    result = supabase.table("tareas").update(data).eq("id", tarea_id).execute()
    return result.data

# ✅ Función: eliminar_tarea(tarea_id)
def eliminar_tarea(tarea_id):
    result = supabase.table("tareas").update({
        "activo": False,
        "updated_at": datetime.now().isoformat()
    }).eq("id", tarea_id).execute()
    return result.data

# ✅ Función: crear_plantilla(data)
def crear_plantilla(data):
    plantilla = {
        "id": str(uuid.uuid4()),
        "titulo": data.get("titulo"),
        "descripcion": data.get("descripcion"),
        "cliente_id": data.get("cliente_id"),
        "creado_por": data.get("creado_por"),
        "fecha_creacion": datetime.now().isoformat(),
        "activo": True
    }
    response = supabase.table("plantillas_tareas").insert(plantilla).execute()
    return response.data

# ✅ Función: obtener_plantilla(plantilla_id)
def obtener_plantilla(plantilla_id):
    response = supabase.table("plantillas_tareas").select("*").eq("id", plantilla_id).single().execute()
    return response.data

# ✅ Función: listar_plantillas_por_cliente(cliente_id)
def listar_plantillas_por_cliente(cliente_id):
    response = supabase.table("plantillas_tareas").select("*").eq("cliente_id", cliente_id).eq("activo", True).order("fecha_creacion", desc=True).execute()
    return response.data

# ✅ Mejorada: aplicar_plantilla()
def aplicar_plantilla(plantilla_id, fecha_base, asignado_a):
    plantilla = obtener_plantilla(plantilla_id)
    if not plantilla:
        return {"error": "❌ Plantilla no encontrada"}

    if not plantilla.get("cliente_id") or not plantilla.get("empresa_id"):
        return {"error": "❌ Plantilla incompleta: falta cliente_id o empresa_id"}

    tareas_tpl = supabase.table("tareas_por_plantilla").select("*").eq("plantilla_id", plantilla_id).execute().data
    tareas_creadas = []

    for tarea_tpl in tareas_tpl:
        dias = tarea_tpl.get("dias_despues") or 0
        fecha_base_dt = datetime.strptime(fecha_base, "%Y-%m-%d")
        fecha_limite = (fecha_base_dt + timedelta(days=dias)).strftime("%Y-%m-%d")

        # ⚠️ Validar fecha límite futura
        if datetime.strptime(fecha_limite, "%Y-%m-%d").date() < datetime.now().date():
            continue  # O registrar advertencia

        codigo = generar_codigo_tarea("PL")

        nueva = {
            "id": str(uuid.uuid4()),
            "codigo_tarea": codigo,
            "titulo": tarea_tpl.get("titulo"),
            "descripcion": tarea_tpl.get("descripcion"),
            "fecha_limite": fecha_limite,
            "prioridad": tarea_tpl.get("prioridad", "media"),
            "estatus": "pendiente",
            "usuario_empresa_id": asignado_a,
            "asignado_a": asignado_a,
            "empresa_id": plantilla["empresa_id"],
            "cliente_id": plantilla["cliente_id"],
            "origen": "plantilla",
            "creado_por": plantilla.get("creado_por"),
            "activo": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        supabase.table("tareas").insert(nueva).execute()
        tareas_creadas.append(nueva)

    return tareas_creadas

# ✅ Función: eliminar_plantilla(plantilla_id)
def eliminar_plantilla(plantilla_id):
    result = supabase.table("plantillas_tareas").update({
        "activo": False,
        "fecha_eliminacion": datetime.now().isoformat()
    }).eq("id", plantilla_id).execute()
    return result.data

# ✅ Funciones para manejo de tareas recurrentes en Nora

def crear_tarea_recurrente(data):
    nueva = {
        "id": str(uuid.uuid4()),
        "cliente_id": data.get("cliente_id"),
        "titulo": data.get("titulo"),
        "descripcion": data.get("descripcion"),
        "frecuencia": data.get("frecuencia"),  # diaria, semanal, mensual
        "dia_ejecucion": data.get("dia_ejecucion"),  # lunes, martes, etc. o 1-31
        "prioridad": data.get("prioridad", "media"),
        "asignado_a": data.get("asignado_a"),
        "hora_preferida": data.get("hora_preferida"),
        "activo": True,
        "creado_por": data.get("creado_por"),
        "created_at": datetime.now().isoformat()
    }
    result = supabase.table("tareas_recurrentes").insert(nueva).execute()
    return result.data

def obtener_tareas_recurrentes_activas(cliente_id):
    result = supabase.table("tareas_recurrentes").select("*") \
        .eq("cliente_id", cliente_id).eq("activo", True).execute()
    return result.data

def ejecutar_recurrencia_diaria():
    hoy = datetime.now()
    dia_nombre = hoy.strftime("%A").lower()  # monday, tuesday, etc.
    dia_numero = hoy.day  # 1-31

    # Buscar tareas con frecuencia diaria
    diarias = supabase.table("tareas_recurrentes").select("*").eq("frecuencia", "diaria").eq("activo", True).execute().data

    # Buscar tareas con frecuencia semanal para hoy
    semanales = supabase.table("tareas_recurrentes").select("*").eq("frecuencia", "semanal").eq("dia_ejecucion", dia_nombre).eq("activo", True).execute().data

    # Buscar tareas mensuales para este día del mes
    mensuales = supabase.table("tareas_recurrentes").select("*").eq("frecuencia", "mensual").eq("dia_ejecucion", str(dia_numero)).eq("activo", True).execute().data

    total_generadas = []

    for tarea in diarias + semanales + mensuales:
        codigo = generar_codigo_tarea("RC")
        nueva_tarea = {
            "id": str(uuid.uuid4()),
            "codigo_tarea": codigo,
            "titulo": tarea.get("titulo"),
            "descripcion": tarea.get("descripcion"),
            "fecha_limite": hoy.strftime("%Y-%m-%d"),
            "prioridad": tarea.get("prioridad", "media"),
            "estatus": "pendiente",
            "usuario_empresa_id": tarea.get("asignado_a"),
            "asignado_a": tarea.get("asignado_a"),
            "empresa_id": tarea.get("empresa_id"),
            "cliente_id": tarea.get("cliente_id"),
            "origen": "recurrente",
            "creado_por": tarea.get("creado_por"),
            "activo": True,
            "created_at": hoy.isoformat(),
            "updated_at": hoy.isoformat()
        }
        supabase.table("tareas").insert(nueva_tarea).execute()
        total_generadas.append(nueva_tarea)

    return {"generadas": len(total_generadas), "tareas": total_generadas}

def eliminar_tarea_recurrente(recurrente_id):
    result = supabase.table("tareas_recurrentes").update({
        "activo": False,
        "updated_at": datetime.now().isoformat()
    }).eq("id", recurrente_id).execute()
    return result.data

# ✅ Funciones para envíos automáticos diarios por WhatsApp en el módulo de TAREAS

def obtener_tareas_para_usuario(usuario_id, fecha):
    result = supabase.table("tareas").select("*") \
        .eq("usuario_empresa_id", usuario_id) \
        .eq("fecha_limite", fecha) \
        .eq("activo", True).execute()
    return result.data

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

# ✅ Mejorada: enviar_mensaje_whatsapp()
def enviar_mensaje_whatsapp(numero, mensaje):
    try:
        if not numero or not numero.startswith("+"):
            print(f"❌ Número inválido u omitido: {numero}")
            return {"status": "omitido", "mensaje": "número inválido"}
        from utils.twilio_client import twilio_client
        full_number = f"whatsapp:{numero}"
        r = twilio_client.messages.create(
            body=mensaje,
            from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
            to=full_number
        )
        return {"status": "enviado", "sid": r.sid}
    except Exception as e:
        print(f"❌ Error al enviar WhatsApp a {numero}: {e}")
        return {"status": "error", "mensaje": str(e)}

# 👉 Funciones programadas para APScheduler

def enviar_reporte_semanal():
    print("📤 Enviando reporte semanal...")
    nora_configs = supabase.table("configuracion_bot").select("nombre_nora, cliente_id").execute().data

    for config in nora_configs:
        nombre_nora = config["nombre_nora"]
        cliente_id = config["cliente_id"]

        completadas = supabase.table("tareas").select("*") \
            .eq("cliente_id", cliente_id).eq("estatus", "completada").eq("activo", True).execute().data

        if not completadas:
            print(f"📭 No hay tareas completadas esta semana para {nombre_nora}")
            continue

        # Determinar número de envío (puede venir de archivo o config)
        numero_admin = os.getenv("WHATSAPP_ADMIN_DEFAULT", "+521234567890")  # usar config dinámica si aplica

        texto = f"📈 Reporte semanal de tareas completadas para {nombre_nora}:\n\n"
        for tarea in completadas:
            texto += f"✅ {tarea['codigo_tarea']}: {tarea['titulo']}\n"

        try:
            twilio_client.messages.create(
                body=texto,
                from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}",
                to=f"whatsapp:{numero_admin}"
            )
            print(f"✅ Reporte enviado a {numero_admin} ({nombre_nora})")
        except Exception as e:
            print(f"❌ Error al enviar reporte a {nombre_nora}: {e}")

# ✅ Función: enviar_tareas_del_dia_por_whatsapp()
def enviar_tareas_del_dia_por_whatsapp():
    print("📤 Enviando tareas del día...")
    hoy = datetime.now(zona).strftime("%Y-%m-%d")

    usuarios = supabase.table("usuarios_empresa").select("*").eq("activo", True).execute().data
    for usuario in usuarios:
        if not usuario.get("telefono") or not usuario["telefono"].startswith("+"):
            print(f"⚠️ Usuario sin número válido: {usuario['nombre']}")
            continue

        tareas = supabase.table("tareas").select("*") \
            .eq("usuario_empresa_id", usuario["id"]) \
            .eq("fecha_limite", hoy).eq("activo", True).execute().data

        if not tareas:
            continue

        mensaje = f"👋 Hola {usuario['nombre']}, estas son tus tareas para hoy:\n\n"
        for t in tareas:
            estado = "⏳"
            if t["estatus"] == "completada":
                estado = "✅"
            elif t["estatus"] in ["vencida", "atrasada"]:
                estado = "❗"
            mensaje += f"{estado} {t['codigo_tarea']}: {t['titulo']}\n"

        try:
            twilio_client.messages.create(
                body=mensaje,
                from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}",
                to=f"whatsapp:{usuario['telefono']}"
            )
            print(f"✅ Mensaje enviado a {usuario['nombre']} ({usuario['telefono']})")
        except Exception as e:
            print(f"❌ Error al enviar a {usuario['nombre']}: {e}")

# ✅ Función: enviar_resumen_6pm_por_whatsapp()
def enviar_resumen_6pm_por_whatsapp():
    print("📤 Enviando resumen 6PM...")
    hoy = datetime.now(zona).strftime("%Y-%m-%d")

    usuarios = supabase.table("usuarios_empresa").select("*").eq("activo", True).execute().data
    for usuario in usuarios:
        if not usuario.get("telefono") or not usuario["telefono"].startswith("+"):
            print(f"⚠️ Usuario sin número válido: {usuario['nombre']}")
            continue

        tareas = supabase.table("tareas").select("*") \
            .eq("usuario_empresa_id", usuario["id"]) \
            .eq("fecha_limite", hoy).eq("activo", True).execute().data

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

        try:
            twilio_client.messages.create(
                body=mensaje,
                from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}",
                to=f"whatsapp:{usuario['telefono']}"
            )
            print(f"✅ Resumen 6PM enviado a {usuario['nombre']}")
        except Exception as e:
            print(f"❌ Error al enviar resumen a {usuario['nombre']}: {e}")

# ✅ Funciones para estadísticas clave y rankings en el módulo de TAREAS

def obtener_resumen_general(cliente_id):
    tareas = supabase.table("tareas").select("*").eq("cliente_id", cliente_id).eq("activo", True).execute().data
    completadas = [t for t in tareas if t["estatus"] == "completada"]
    vencidas = [t for t in tareas if t["estatus"] in ["vencida", "atrasada"]]
    activas = [t for t in tareas if t["estatus"] not in ["completada", "cancelada"]]

    return {
        "tareas_total": len(tareas),
        "tareas_completadas": len(completadas),
        "tareas_activas": len(activas),
        "tareas_vencidas": len(vencidas),
        "porcentaje_cumplimiento": calcular_porcentaje_cumplimiento(cliente_id)
    }

def obtener_tareas_por_estado(cliente_id, fecha_inicio, fecha_fin):
    tareas = supabase.table("tareas").select("*") \
        .eq("cliente_id", cliente_id) \
        .gte("fecha_limite", fecha_inicio) \
        .lte("fecha_limite", fecha_fin) \
        .eq("activo", True).execute().data

    estado_count = {}
    for t in tareas:
        estado = t.get("estatus", "sin_estado")
        estado_count[estado] = estado_count.get(estado, 0) + 1

    return estado_count

def obtener_ranking_usuarios_por_completadas(cliente_id):
    tareas = supabase.table("tareas").select("usuario_empresa_id, estatus") \
        .eq("cliente_id", cliente_id).eq("activo", True).execute().data

    ranking = {}
    for t in tareas:
        uid = t["usuario_empresa_id"]
        if t["estatus"] == "completada":
            ranking[uid] = ranking.get(uid, 0) + 1

    lista = [{"usuario_empresa_id": k, "completadas": v} for k, v in ranking.items()]
    return sorted(lista, key=lambda x: x["completadas"], reverse=True)

def obtener_ranking_usuarios_por_vencidas(cliente_id):
    tareas = supabase.table("tareas").select("usuario_empresa_id, estatus") \
        .eq("cliente_id", cliente_id).eq("activo", True).execute().data

    ranking = {}
    for t in tareas:
        uid = t["usuario_empresa_id"]
        if t["estatus"] in ["vencida", "atrasada"]:
            ranking[uid] = ranking.get(uid, 0) + 1

    lista = [{"usuario_empresa_id": k, "vencidas": v} for k, v in ranking.items()]
    return sorted(lista, key=lambda x: x["vencidas"], reverse=True)

def obtener_usuarios_mas_activos(cliente_id):
    tareas = supabase.table("tareas").select("usuario_empresa_id") \
        .eq("cliente_id", cliente_id).eq("activo", True).execute().data

    conteo = {}
    for t in tareas:
        uid = t["usuario_empresa_id"]
        conteo[uid] = conteo.get(uid, 0) + 1

    lista = [{"usuario_empresa_id": k, "tareas": v} for k, v in conteo.items()]
    return sorted(lista, key=lambda x: x["tareas"], reverse=True)

def calcular_porcentaje_cumplimiento(cliente_id):
    tareas = supabase.table("tareas").select("estatus") \
        .eq("cliente_id", cliente_id).eq("activo", True).execute().data
    total = len(tareas)
    completadas = len([t for t in tareas if t["estatus"] == "completada"])
    if total == 0:
        return 0
    return round((completadas / total) * 100, 2)

# ✅ Ruta correcta para el panel principal (respetando url_prefix ya definido)
@panel_cliente_tareas_bp.route("/", endpoint="index_tareas")
def index_tareas(nombre_nora):
    # Obtener configuración del bot para esta Nora
    config_result = supabase.table("configuracion_bot").select("*").eq("nombre_nora", nombre_nora).single().execute()
    config_data = config_result.data or {}

    cliente_id = config_data.get("cliente_id")
    empresa_id = config_data.get("empresa_id")

    # 🛡 Validar que estén definidos para evitar error UUID None
    if not cliente_id or not empresa_id:
        return render_template("panel_cliente_tareas/index.html",
            nombre_nora=nombre_nora,
            tareas=[],
            tarea=None,
            usuarios=[],
            permisos={"ver_todas": False},
            datos={"tareas_semana": 0, "tareas_completadas": 0, "tareas_activas": 0, "tareas_vencidas": 0, "porcentaje_cumplimiento": 0, "ranking_usuarios": []},
            resumen={"tareas_activas": 0, "tareas_completadas": 0, "tareas_vencidas": 0, "porcentaje_cumplimiento": 0},
            config={},
            alertas={},
            supervisores_activos=0,
            usuarios_empresa=[],
            verificaciones={},
            reportes_whatsapp=[],
            empresa_id=None,
            cliente_id=None
        )

    # Obtener usuarios
    usuarios = supabase.table("usuarios_clientes").select("*") \
        .eq("nombre_nora", nombre_nora).eq("activo", True).execute().data or []

    # Obtener tareas activas (simples por ahora)
    tareas = supabase.table("tareas").select("*").eq("cliente_id", cliente_id).eq("activo", True).execute().data or []

    # Resumen y métricas
    resumen = obtener_resumen_general(cliente_id)
    ranking = obtener_ranking_usuarios_por_completadas(cliente_id)

    # Alertas
    alertas = {
        "empresa_mas_activas": {"nombre": "Sin datos", "total": 0},
        "usuario_mas_atrasado": {"nombre": "Sin datos", "total": 0},
        "usuarios_inactivos": [],
        "ranking_semanal": []
    }

    # Renderizar plantilla
    return render_template("panel_cliente_tareas/index.html",
        nombre_nora=nombre_nora,
        tareas=tareas,
        tarea=None,
        usuarios=usuarios,
        permisos={"ver_todas": True},
        datos={
            "tareas_semana": 0,
            "tareas_completadas": resumen["tareas_completadas"],
            "tareas_activas": resumen["tareas_activas"],
            "tareas_vencidas": resumen["tareas_vencidas"],
            "porcentaje_cumplimiento": resumen["porcentaje_cumplimiento"],
            "ranking_usuarios": ranking
        },
        resumen=resumen,
        config={
            "tareas_recurrentes": config_data.get("tareas_recurrentes", False),
            "alertas_whatsapp": config_data.get("alertas_whatsapp", False),
            "reporte_semanal": config_data.get("reporte_semanal", False),
            "tareas_sugeridas_modulos": config_data.get("tareas_sugeridas_modulos", False)
        },
        alertas=alertas,
        supervisores_activos=0,
        usuarios_empresa=usuarios,
        verificaciones={},
        reportes_whatsapp=[],
        empresa_id=empresa_id,
        cliente_id=cliente_id
    )
