from flask import request, jsonify, Blueprint
from .panel_cliente_tareas import panel_cliente_tareas_bp
from datetime import datetime, timedelta
from supabase import create_client
import os
import uuid

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

plantillas_bp = Blueprint(
    "plantillas", __name__,
    template_folder="../../../templates/panel_cliente_tareas"
)

# ✅ Crear una plantilla
@panel_cliente_tareas_bp.route("/plantillas/crear", methods=["POST"])
def crear_plantilla():
    data = request.get_json()
    plantilla = {
        "id": str(uuid.uuid4()),
        "titulo": data["titulo"],
        "descripcion": data.get("descripcion", ""),
        "cliente_id": data["cliente_id"],
        "nombre_nora": data["nombre_nora"],
        "activo": True,
        "created_at": datetime.now().isoformat()
    }
    supabase.table("plantillas_tareas").insert(plantilla).execute()

    # Insertar las tareas hijas
    for t in data.get("tareas", []):
        tarea = {
            "id": str(uuid.uuid4()),
            "plantilla_id": plantilla["id"],
            "titulo": t["titulo"],
            "descripcion": t.get("descripcion", ""),
            "prioridad": t.get("prioridad", "media"),
            "dias_despues": t.get("dias_despues", 0),
            "created_at": datetime.now().isoformat()
        }
        supabase.table("tareas_por_plantilla").insert(tarea).execute()

    return jsonify({"success": True})

# ✅ Obtener una plantilla por ID
@panel_cliente_tareas_bp.route("/plantillas/<plantilla_id>", methods=["GET"])
def obtener_plantilla(plantilla_id):
    plantilla = supabase.table("plantillas_tareas").select("*").eq("id", plantilla_id).single().execute().data
    tareas = supabase.table("tareas_por_plantilla").select("*").eq("plantilla_id", plantilla_id).execute().data or []
    return jsonify({"plantilla": plantilla, "tareas": tareas})

# ✅ Listar todas las plantillas activas por cliente
@panel_cliente_tareas_bp.route("/plantillas/listar/<cliente_id>", methods=["GET"])
def listar_plantillas_por_cliente(cliente_id):
    plantillas = supabase.table("plantillas_tareas").select("*") \
        .eq("cliente_id", cliente_id).eq("activo", True).execute().data or []
    return jsonify(plantillas)

# ✅ Aplicar una plantilla generando tareas reales
@panel_cliente_tareas_bp.route("/plantillas/aplicar", methods=["POST"])
def aplicar_plantilla():
    data = request.get_json()
    plantilla_id = data["plantilla_id"]
    fecha_base = datetime.strptime(data["fecha_base"], "%Y-%m-%d")
    asignado_a = data["asignado_a"]
    empresa_id = data["empresa_id"]
    cliente_id = data["cliente_id"]
    nombre_nora = data["nombre_nora"]
    creado_por = data["creado_por"]

    plantilla = supabase.table("plantillas_tareas").select("*").eq("id", plantilla_id).single().execute().data
    if not plantilla or not cliente_id or not empresa_id:
        return jsonify({"error": "Falta información para aplicar plantilla"}), 400

    tareas = supabase.table("tareas_por_plantilla").select("*").eq("plantilla_id", plantilla_id).execute().data or []
    creadas = []

    for t in tareas:
        fecha_limite = fecha_base + timedelta(days=t["dias_despues"])
        iniciales = ''.join(filter(str.isalnum, t["titulo"][:2].upper()))
        fecha_str = fecha_limite.strftime("%d%m%y")
        codigo_base = f"{iniciales}-{fecha_str}"
        count = supabase.table("tareas").select("id").ilike("codigo_tarea", f"{codigo_base}-%").execute().data
        correlativo = len(count) + 1
        codigo = f"{codigo_base}-{str(correlativo).zfill(3)}"

        nueva = {
            "id": str(uuid.uuid4()),
            "codigo_tarea": codigo,
            "titulo": t["titulo"],
            "descripcion": t.get("descripcion", ""),
            "fecha_limite": fecha_limite.strftime("%Y-%m-%d"),
            "prioridad": t.get("prioridad", "media"),
            "estatus": "pendiente",
            "usuario_empresa_id": asignado_a,
            "asignado_a": asignado_a,
            "empresa_id": empresa_id,
            "cliente_id": cliente_id,
            "origen": "plantilla",
            "creado_por": creado_por,
            "activo": True,
            "nombre_nora": nombre_nora,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        supabase.table("tareas").insert(nueva).execute()
        creadas.append(codigo)

    return jsonify({"success": True, "creadas": creadas})

# ✅ Eliminar plantilla (soft delete)
@panel_cliente_tareas_bp.route("/plantillas/eliminar/<plantilla_id>", methods=["DELETE"])
def eliminar_plantilla(plantilla_id):
    supabase.table("plantillas_tareas").update({
        "activo": False,
        "updated_at": datetime.now().isoformat()
    }).eq("id", plantilla_id).execute()
    return jsonify({"success": True})

@plantillas_bp.route("/panel_cliente/<nombre_nora>/plantillas/prueba", methods=["GET"])
def prueba_plantillas(nombre_nora):
    return f"Vista de prueba PLANTILLAS para {nombre_nora}"