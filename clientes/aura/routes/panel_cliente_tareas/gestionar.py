from flask import Blueprint, render_template, request, redirect, session
from datetime import datetime
from clientes.aura.utils.supabase_client import supabase
import uuid

panel_tareas_gestionar_bp = Blueprint("panel_tareas_gestionar", __name__)

@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar", methods=["GET"])
def gestionar_tareas(nombre_nora):
    user = session.get("user", {})
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
        empresa_id=empresa_id,
        user=user
    )

@panel_tareas_gestionar_bp.route("/panel_cliente/<nombre_nora>/tareas/gestionar/guardar", methods=["POST"])
def guardar_tarea_gestor(nombre_nora):
    print("🔵 [gestionar.py] guardar_tarea_gestor llamado")
    form = request.form
    print(f"🔵 Formulario recibido: {form}")
    user = session.get("user", {})

    empresa_id = form.get("empresa_id") or user.get("empresa_id") or ""
    creado_por = form.get("creado_por") or user.get("nombre", "")
    iniciales_usuario = form.get("iniciales_usuario") or "".join([w[0] for w in creado_por.split()]) or "NN"
    asignado_a = form.get("asignado_a") or ""
    titulo = form.get("titulo") or ""
    prioridad = form.get("prioridad") or ""
    fecha_limite = form.get("fecha_limite") or ""

    print(f"🧪 empresa_id={empresa_id}, creado_por={creado_por}, asignado_a={asignado_a}, titulo={titulo}")

    if not empresa_id or empresa_id.strip() == "":
        return "❌ Falta empresa_id", 400
    if not creado_por or creado_por.strip() == "":
        return "❌ Falta creado_por", 400
    if not asignado_a or asignado_a.strip() == "":
        return "❌ Falta asignado_a", 400
    if not titulo.strip():
        return "❌ Falta título", 400

    tarea_data = {
        "id": str(uuid.uuid4()),
        "codigo_tarea": "",  # se genera abajo
        "titulo": titulo,
        "descripcion": form.get("descripcion", ""),
        "fecha_limite": fecha_limite,
        "prioridad": prioridad,
        "estatus": "pendiente",
        "usuario_empresa_id": asignado_a,
        "asignado_a": asignado_a,
        "empresa_id": empresa_id,
        "nombre_nora": nombre_nora,
        "creado_por": creado_por,
        "iniciales_usuario": iniciales_usuario,
        "origen": "manual",
        "activo": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    def generar_codigo_tarea(iniciales_usuario):
        fecha = datetime.now().strftime("%d%m%y")
        base_codigo = f"{iniciales_usuario.upper()}-{fecha}"
        existentes = supabase.table("tareas").select("id").ilike("codigo_tarea", f"{base_codigo}-%").execute()
        correlativo = len(existentes.data) + 1
        return f"{base_codigo}-{str(correlativo).zfill(3)}"

    tarea_data["codigo_tarea"] = generar_codigo_tarea(iniciales_usuario)

    try:
        result = supabase.table("tareas").insert(tarea_data).execute()
        print(f"✅ Tarea insertada: {result.data}")
        return redirect(f"/panel_cliente/{nombre_nora}/tareas/gestionar")
    except Exception as e:
        print(f"❌ Error al insertar tarea: {e}")
        return f"❌ Error al crear tarea: {e}", 500