// ✅ Archivo: clientes/aura/static/js/tareas_eliminar.js

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".btn-eliminar-tarea").forEach((btn) => {
    btn.addEventListener("click", () => {
      const tareaId = btn.dataset.id;
      const nombreNora = document.querySelector("#contenedorGestorTareas")?.dataset.nora;
      if (!nombreNora) return alert("⚠️ No se detectó el nombre de Nora.");

      fetch(`/panel_cliente/${nombreNora}/tareas/gestionar/eliminar/${tareaId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.ok) {
            // Quitar la fila de la tarea eliminada del DOM
            const fila = btn.closest("tr");
            if (fila) fila.remove();
            // Si no es una tabla, intentar ocultar el elemento padre relevante
            // (opcional: puedes adaptar esto según la estructura de la UI)
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
