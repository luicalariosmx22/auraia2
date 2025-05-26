from flask import Blueprint, render_template, request, redirect, session
from datetime import datetime
from clientes.aura.utils.supabase_client import supabase
import uuid

panel_tareas_gestionar_bp = Blueprint("panel_tareas_gestionar", __name__)

@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar", methods=["GET"])
def gestionar_tareas(nombre_nora):
    user = session.get("user", {})
    cliente_id = user.get("cliente_id", "")
    empresa_id = user.get("empresa_id", "")

    tareas = supabase.table("tareas")\
        .select("*")\
        .eq("nombre_nora", nombre_nora)\
        .eq("activo", True)\
        .order("created_at", desc=True)\
        .execute().data or []

    usuarios = supabase.table("usuarios_clientes").select("*").eq("nombre_nora", nombre_nora).execute().data or []
    empresas = supabase.table("cliente_empresas").select("id, nombre_empresa").eq("nombre_nora", nombre_nora).execute().data or []

    return render_template("panel_cliente_tareas/gestionar.html",
        nombre_nora=nombre_nora,
        tareas=tareas,
        usuarios=usuarios,
        empresas=empresas,
        cliente_id=cliente_id,
        empresa_id=empresa_id,
        user=user
    )

@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar/guardar", methods=["POST"])
def guardar_tarea_gestor(nombre_nora):
    print("🔵 [gestionar.py] guardar_tarea_gestor llamado")
    form = request.form
    print(f"🔵 Formulario recibido: {form}")
    user = session.get("user", {})
    cliente_id = form.get("cliente_id") or user.get("cliente_id", "")
    empresa_id = form.get("empresa_id") or user.get("empresa_id", "")
    creado_por = user.get("nombre", "Desconocido")
    iniciales_usuario = "".join([w[0] for w in user.get("nombre", "NN").split()]) if user.get("nombre") else "NN"

    if not cliente_id or not empresa_id:
        return "❌ Faltan campos requeridos (cliente_id o empresa_id)", 400

    tarea_data = {
        "titulo": form.get("titulo"),
        "descripcion": form.get("descripcion"),
        "prioridad": form.get("prioridad"),
        "fecha_limite": form.get("fecha_limite"),
        "asignado_a": form.get("asignado_a"),
        "empresa_id": empresa_id,
        "usuario_empresa_id": form.get("asignado_a"),
        "cliente_id": cliente_id,
        "nombre_nora": nombre_nora,
        "creado_por": creado_por,
        "iniciales_usuario": iniciales_usuario,
        "origen": "manual"
    }

    print(f"🔵 tarea_data a crear: {tarea_data}")

    def generar_codigo_tarea(iniciales_usuario):
        fecha = datetime.now().strftime("%d%m%y")
        iniciales = ''.join(filter(str.isalnum, iniciales_usuario.upper()))[:3]
        base_codigo = f"{iniciales}-{fecha}"
        existentes = supabase.table("tareas").select("id").ilike("codigo_tarea", f"{base_codigo}-%").execute()
        correlativo = len(existentes.data) + 1
        return f"{base_codigo}-{str(correlativo).zfill(3)}"

    tarea_data["codigo_tarea"] = generar_codigo_tarea(iniciales_usuario)
    tarea_data["id"] = str(uuid.uuid4())
    tarea_data["estatus"] = "pendiente"
    tarea_data["activo"] = True
    tarea_data["created_at"] = datetime.now().isoformat()
    tarea_data["updated_at"] = datetime.now().isoformat()

    try:
        result = supabase.table("tareas").insert(tarea_data).execute()
        print(f"🔵 Resultado de creación desde gestor: {result.data}")
        return redirect(f"/panel_cliente/{nombre_nora}/tareas/gestionar")
    except Exception as e:
        print(f"❌ Error al insertar tarea: {e}")
        return f"❌ Error al crear tarea: {e}", 500