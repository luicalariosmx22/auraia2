# ✅ Archivo: clientes/aura/routes/panel_cliente_tareas/utils/alertas_y_ranking.py

from supabase import create_client, Client
import os
from collections import defaultdict
from datetime import datetime, timedelta

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def actualizar_estadisticas_alertas(nombre_nora):
    print("🟡 Ejecutando actualizar_estadisticas_alertas")

    try:
        tareas_resp = supabase.table("tareas").select("*").eq("nombre_nora", nombre_nora).eq("activo", True).execute()
        tareas = tareas_resp.data or []

        usuarios_resp = supabase.table("usuarios_clientes").select("id, nombre").eq("nombre_nora", nombre_nora).execute()
        usuarios = {u["id"]: u["nombre"] for u in usuarios_resp.data or []}

        empresas_resp = supabase.table("cliente_empresas").select("id, nombre_empresa").eq("nombre_nora", nombre_nora).execute()
        empresas = {e["id"]: e["nombre_empresa"] for e in empresas_resp.data or []}

        empresa_tareas_activas = defaultdict(int)
        for t in tareas:
            if t["estatus"] != "completada" and t.get("empresa_id"):
                empresa_tareas_activas[t["empresa_id"]] += 1
        empresa_mas_activas = max(empresa_tareas_activas.items(), key=lambda x: x[1], default=(None, 0))[0]
        empresa_nombre = empresas.get(empresa_mas_activas, "Sin datos")

        usuario_tareas_vencidas = defaultdict(int)
        for t in tareas:
            if t.get("estatus") in ["retrasada", "vencida"] and t.get("usuario_empresa_id"):
                usuario_tareas_vencidas[t["usuario_empresa_id"]] += 1
        usuario_peor = max(usuario_tareas_vencidas.items(), key=lambda x: x[1], default=(None, 0))[0]
        usuario_peor_nombre = usuarios.get(usuario_peor, "Sin datos")

        hoy = datetime.utcnow().date()
        inactivos = []
        for uid, nombre in usuarios.items():
            completadas = [
                t for t in tareas
                if t.get("usuario_empresa_id") == uid and t.get("estatus") == "completada" and t.get("updated_at")
            ]
            if completadas:
                fechas = [datetime.fromisoformat(t["updated_at"]).date() for t in completadas if t["updated_at"]]
                ultima = max(fechas)
                if (hoy - ultima).days >= 3:
                    inactivos.append({"nombre": nombre})
            else:
                inactivos.append({"nombre": nombre})

        inicio_semana = hoy - timedelta(days=hoy.weekday())
        ranking = defaultdict(int)
        for t in tareas:
            if t.get("estatus") == "completada" and t.get("updated_at"):
                fecha = datetime.fromisoformat(t["updated_at"]).date()
                if fecha >= inicio_semana and t.get("usuario_empresa_id"):
                    ranking[t["usuario_empresa_id"]] += 1

        ranking_semanal = sorted(
            [{"nombre": usuarios.get(uid, "Sin nombre"), "tareas_completadas": count} for uid, count in ranking.items()],
            key=lambda x: x["tareas_completadas"],
            reverse=True
        )

        print("🟢 Empresa con más tareas activas:", empresa_nombre)
        print("🟢 Usuario con más tareas vencidas:", usuario_peor_nombre)
        print("🟢 Usuarios inactivos:", inactivos)
        print("🟢 Ranking semanal:", ranking_semanal)

        # Puedes definir aquí los valores de resumen, usuarios y config según tu lógica
        resumen = {}   # ← ajusta según tu lógica real
        usuarios_dict = usuarios  # ya es un dict id->nombre
        config = {}

        return {
            "empresa_mas_activas": empresa_nombre,
            "usuario_mas_atrasado": usuario_peor_nombre,
            "usuarios_inactivos": inactivos,
            "ranking_semanal": ranking_semanal,
            "resumen": resumen,
            "usuarios": usuarios_dict,
            "config": config
        }

    except Exception as e:
        print("❌ Error en alertas_y_ranking:", str(e))
        return {}

def obtener_datos_alertas_y_ranking(nombre_nora, tareas, usuarios):
    """
    Procesa tareas y usuarios para generar:
    - Empresas con más tareas activas
    - Usuario con más tareas vencidas
    - Ranking semanal de cumplimiento
    """
    empresa_tareas_activas = defaultdict(int)
    usuario_tareas_vencidas = defaultdict(int)
    ranking = []

    for t in tareas:
        if t["estatus"] != "completada" and t["empresa_id"]:
            empresa_tareas_activas[t["empresa_id"]] += 1
        if t["estatus"] in ["vencida", "atrasada"] and t["asignado_a"]:
            usuario_tareas_vencidas[t["asignado_a"]] += 1

    # Detectar empresa con más tareas activas
    empresa_mas_activas = max(empresa_tareas_activas.items(), key=lambda x: x[1], default=(None, 0))[0]

    # Detectar usuario con más tareas vencidas
    usuario_mas_atrasado = max(usuario_tareas_vencidas.items(), key=lambda x: x[1], default=(None, 0))[0]

    # Construir ranking semanal
    for u in usuarios:
        completadas = sum(1 for t in tareas if t["estatus"] == "completada" and t.get("asignado_a") == u["id"])
        asignadas = sum(1 for t in tareas if t.get("asignado_a") == u["id"])
        cumplimiento = round((completadas / asignadas) * 100, 1) if asignadas > 0 else 0
        ranking.append({
            "usuario": u,
            "cumplimiento": cumplimiento,
            "completadas": completadas,
            "asignadas": asignadas
        })

    # Ordenar ranking por cumplimiento
    ranking.sort(key=lambda x: x["cumplimiento"], reverse=True)

    return {}, ranking, usuario_mas_atrasado, empresa_mas_activas
