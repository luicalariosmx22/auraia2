// ✅ Archivo: clientes/aura/static/js/tareas_eliminar.js

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".btn-eliminar-tarea").forEach((btn) => {
    btn.addEventListener("click", () => {
      const tareaId = btn.dataset.id;
      const nombreNora = document.querySelector("#contenedorGestorTareas")?.dataset.nora;
      if (!nombreNora) return alert("⚠️ No se detectó el nombre de Nora.");

      if (!confirm("¿Estás seguro de que quieres eliminar esta tarea?")) return;

      fetch(`/panel_cliente/${nombreNora}/tareas/eliminar/${tareaId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.ok) {
            alert("✅ Tarea eliminada correctamente.");
            location.reload();
          } else {
            alert("❌ Error al eliminar: " + (data.error || "Respuesta inválida"));
          }
        })
        .catch((error) => {
          console.error("❌ Error inesperado:", error);
          alert("❌ Error inesperado al eliminar la tarea.");
        });
    });
  });
});
