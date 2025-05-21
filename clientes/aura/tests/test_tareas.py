# ✅ Archivo: clientes/aura/tests/test_tareas.py
# 👉 Verificación básica del módulo de TAREAS (manual o automatizada)

from clientes.aura.routes.panel_cliente_tareas.tareas_crud import (
    crear_tarea, actualizar_tarea, eliminar_tarea,
    crear_plantilla, aplicar_plantilla,
    ejecutar_recurrencia_diaria
)
from clientes.aura.routes.panel_cliente_tareas.reportes import (
    enviar_tareas_del_dia_por_whatsapp, enviar_reporte_6pm_por_whatsapp,
    obtener_resumen_general, obtener_ranking_usuarios_por_completadas
)
from clientes.aura.utils.permisos_tareas import (
    puede_reasignar_tareas, validar_limite_supervisores
)

def test_crud_basico():
    print("🔹 PRUEBAS CRUD")

    # Crear tarea
    tarea = crear_tarea({
        "titulo": "Tarea de prueba",
        "descripcion": "Prueba de creación",
        "fecha_limite": "2025-12-31",
        "prioridad": "alta",
        "usuario_empresa_id": "usuario1",
        "empresa_id": "empresa1",
        "cliente_id": "cliente1",
        "creado_por": "admin1",
        "iniciales_usuario": "TP"
    })
    assert tarea[0]["codigo_tarea"].startswith("TP-"), "❌ Código incorrecto"
    print("✅ Tarea creada y código generado")

    # Editar tarea
    actualizar = actualizar_tarea(tarea[0]["id"], {"prioridad": "media", "estatus": "completada"})
    assert actualizar, "❌ Error al actualizar tarea"
    print("✅ Tarea actualizada correctamente")

    # Eliminar tarea
    eliminar = eliminar_tarea(tarea[0]["id"])
    assert eliminar[0]["activo"] is False, "❌ Tarea no fue desactivada"
    print("✅ Tarea eliminada (desactivada)")

def test_plantillas():
    print("🔹 PRUEBAS DE PLANTILLAS")

    plantilla = crear_plantilla({
        "titulo": "Plantilla test",
        "descripcion": "Plantilla para pruebas",
        "cliente_id": "cliente1",
        "creado_por": "admin1"
    })
    assert plantilla, "❌ Error al crear plantilla"

    aplicar = aplicar_plantilla(plantilla[0]["id"], "2025-12-01", "usuario1")
    assert aplicar, "❌ No se generaron tareas desde plantilla"
    print("✅ Plantilla aplicada y tareas generadas")

def test_permisos():
    print("🔹 PRUEBAS DE PERMISOS")

    assert not puede_reasignar_tareas("usuario_sin_permiso"), "❌ Usuario sin permiso pudo reasignar"
    assert validar_limite_supervisores("cliente1", nuevo=False), "❌ Límite de supervisores excedido"
    print("✅ Validación de permisos correcta")

def test_whatsapp_simulado():
    print("🔹 PRUEBAS DE WHATSAPP (simuladas)")

    am = enviar_tareas_del_dia_por_whatsapp()
    pm = enviar_reporte_6pm_por_whatsapp()
    assert isinstance(am, list) and isinstance(pm, list), "❌ Error en simulación de mensajes"
    print(f"✅ Mensajes simulados enviados a {len(am)} usuarios (AM), {len(pm)} (PM)")

def test_estadisticas():
    print("🔹 PRUEBAS DE ESTADÍSTICAS")

    resumen = obtener_resumen_general("cliente1")
    ranking = obtener_ranking_usuarios_por_completadas("cliente1")
    assert "tareas_completadas" in resumen, "❌ Resumen incompleto"
    assert isinstance(ranking, list), "❌ Ranking inválido"
    print("✅ Estadísticas y ranking generados correctamente")

def test_automatizaciones():
    print("🔹 PRUEBAS DE AUTOMATIZACIONES")

    generadas = ejecutar_recurrencia_diaria()
    assert "generadas" in generadas, "❌ No se ejecutó recurrencia"
    print(f"✅ Automatización ejecutada. Tareas creadas: {generadas['generadas']}")

# Ejecutar todo
if __name__ == "__main__":
    test_crud_basico()
    test_plantillas()
    test_permisos()
    test_whatsapp_simulado()
    test_estadisticas()
    test_automatizaciones()
